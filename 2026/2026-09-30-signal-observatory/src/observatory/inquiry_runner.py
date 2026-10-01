"""Inquiry execution runner.

Coordinates end-to-end research runs based on declarative inquiry specifications.
Manages the run directory lifecycle, query execution, raw logging, artifact storage,
media/transcript enrichment, and manifest generation.
"""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml
from rich.console import Console

from observatory.collectors.base import BaseCollector
from observatory.collectors.bluesky import BlueskyCollector
from observatory.collectors.footage import CitizenFootageCollector
from observatory.collectors.reddit import RedditCollector
from observatory.collectors.reviews import ReviewsCollector
from observatory.collectors.web import WebCollector
from observatory.collectors.youtube import YouTubeCollector
from observatory.config import Settings, get_settings
from observatory.media import download_media_footage
from observatory.models import (
    Annotation,
    AnnotationType,
    Artifact,
    ContentType,
    Inquiry,
    Platform,
    QueryRecord,
    RunManifest,
)
from observatory.store.corpus import CorpusStore

console = Console()


def load_inquiry(path: Path) -> Inquiry:
    """Load and validate an inquiry YAML file.

    Args:
        path: Path to the inquiry YAML file.

    Returns:
        Validated Inquiry object.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Support top-level 'inquiry' key or direct dict
    inquiry_dict = data.get("inquiry", data)
    return Inquiry.model_validate(inquiry_dict)


class InquiryRunner:
    """Executes a structured research inquiry across platform collectors."""

    def __init__(self, inquiry: Inquiry, settings: Settings | None = None) -> None:
        self.inquiry = inquiry
        self.settings = settings or get_settings()
        self.corpus = CorpusStore(settings=self.settings)

        # Generate run ID
        date_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{self.inquiry.id}_{date_str}"
        self.run_dir = self.settings.runs_dir / self.run_id

    def setup_run_dir(self) -> Path:
        """Initialize the run directory and record initial inquiry."""
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # Save run-specific inquiry copy
        inquiry_dump = self.inquiry.model_dump(mode="json")
        with open(self.run_dir / "inquiry.json", "w", encoding="utf-8") as f:
            json.dump(inquiry_dump, f, indent=2, default=str)

        return self.run_dir

    def _get_collector(self, platform: Platform) -> BaseCollector | None:
        """Instantiate the appropriate collector for the platform."""
        match platform:
            case Platform.BLUESKY:
                return BlueskyCollector()
            case Platform.YOUTUBE:
                return YouTubeCollector()
            case Platform.REDDIT:
                return RedditCollector()
            case Platform.WEB:
                return WebCollector()
            case Platform.REVIEWS:
                return ReviewsCollector()
            case Platform.CITIZEN | Platform.TIKTOK | Platform.FACEBOOK:
                return CitizenFootageCollector()
            case _:
                return None

    async def execute(self, auto_transcribe: bool = True) -> RunManifest:
        """Execute the research run according to the inquiry specifications.

        Args:
            auto_transcribe: Automatically fetch transcripts for collected video artifacts.

        Returns:
            Completed RunManifest.
        """
        self.setup_run_dir()
        manifest = RunManifest(
            run_id=self.run_id,
            inquiry_id=self.inquiry.id,
            started_at=datetime.now(UTC),
            status="running",
        )

        queries_file = self.run_dir / "queries.jsonl"
        collected_artifacts: list[Artifact] = []
        platforms_searched: set[str] = set()

        query_budget = self.inquiry.budget.max_queries
        artifact_budget = self.inquiry.budget.max_artifacts
        queries_executed = 0

        # Build search terms combining seeds and geography
        search_terms: list[str] = list(self.inquiry.seeds.terms)
        for hashtag in self.inquiry.seeds.hashtags:
            if hashtag not in search_terms:
                search_terms.append(hashtag)

        # Execute searches across requested platforms
        for platform in self.inquiry.platforms:
            collector = self._get_collector(platform)
            if not collector:
                continue

            platforms_searched.add(platform.value)

            try:
                for term in search_terms:
                    if queries_executed >= query_budget:
                        break
                    if len(collected_artifacts) >= artifact_budget:
                        break

                    query_id = str(uuid.uuid4())[:8]
                    executed_at = datetime.now(UTC)

                    since_str = self.inquiry.scope.time.since.isoformat()
                    until_str = (
                        self.inquiry.scope.time.until.isoformat()
                        if self.inquiry.scope.time.until
                        else None
                    )

                    try:
                        artifacts, next_cursor, raw_records = await collector.search(
                            term,
                            limit=min(25, artifact_budget - len(collected_artifacts)),
                            since=since_str,
                            until=until_str,
                        )

                        # Tag provenance
                        for a in artifacts:
                            a.query_id = query_id
                            a.run_id = self.run_id

                        # Store raw data
                        if raw_records:
                            self.corpus.store_raw(
                                raw_records,
                                platform=platform.value,
                                query_id=query_id,
                            )

                        # Store normalized artifacts
                        if artifacts:
                            self.corpus.store_artifacts(artifacts)
                            collected_artifacts.extend(artifacts)

                        # Record query
                        q_record = QueryRecord(
                            query_id=query_id,
                            run_id=self.run_id,
                            platform=platform,
                            query_text=term,
                            parameters={"since": since_str, "until": until_str},
                            executed_at=executed_at,
                            result_count=len(artifacts),
                            cursor=next_cursor,
                        )

                        with open(queries_file, "a", encoding="utf-8") as qf:
                            qf.write(q_record.model_dump_json() + "\n")

                        queries_executed += 1

                    except Exception as err:
                        # Log error in query record
                        with open(queries_file, "a", encoding="utf-8") as qf:
                            error_payload = {
                                "query_id": query_id,
                                "run_id": self.run_id,
                                "platform": platform.value,
                                "query_text": term,
                                "error": str(err),
                                "executed_at": executed_at.isoformat(),
                            }
                            qf.write(json.dumps(error_payload) + "\n")
                        queries_executed += 1

            finally:
                if hasattr(collector, "close"):
                    await collector.close()

        # Step 2: Auto-enrich transcripts, raw footage downloads, and user comments
        total_media = 0
        total_comments = 0
        max_downloads = getattr(self.inquiry.budget, "max_media_downloads", 0)
        downloaded_count = 0
        run_media_dir = self.run_dir / "media"
        user_media_dir = get_settings().media_dir

        if auto_transcribe:
            yt_collector = YouTubeCollector()
            for artifact in collected_artifacts:
                is_video = (
                    artifact.platform
                    in (
                        Platform.YOUTUBE,
                        Platform.TIKTOK,
                        Platform.FACEBOOK,
                        Platform.CITIZEN,
                    )
                    and artifact.content_type in (ContentType.VIDEO, ContentType.FOOTAGE)
                )
                if is_video:
                    total_media += 1

                    # 1. Download raw video footage with descriptive naming if requested in budget
                    if downloaded_count < max_downloads:
                        try:
                            video_url = (
                                artifact.canonical_url
                                or f"https://www.youtube.com/watch?v={artifact.native_id}"
                            )
                            local_file, _ = download_media_footage(
                                video_url, output_dir=user_media_dir, max_height=720
                            )
                            if local_file and local_file.exists():
                                run_media_dir.mkdir(parents=True, exist_ok=True)
                                run_copy = run_media_dir / local_file.name
                                if not run_copy.exists():
                                    import shutil

                                    shutil.copy2(local_file, run_copy)
                                artifact.media_refs.append(str(local_file))
                                downloaded_count += 1
                        except Exception:
                            pass

                    # 2. Fetch spoken transcript (for YouTube)
                    if artifact.platform == Platform.YOUTUBE:
                        try:
                            transcript_text = await yt_collector.fetch_transcript(
                                artifact.native_id
                            )
                            if transcript_text:
                                annotation = Annotation(
                                    annotation_id=str(uuid.uuid4())[:12],
                                    artifact_id=artifact.artifact_id,
                                    annotation_type=AnnotationType.TRANSCRIPTION,
                                    value=transcript_text,
                                    model="youtube-captions",
                                    model_version="auto",
                                )
                                self.corpus.store_annotations([annotation])
                        except Exception:
                            pass

                        # 3. Harvest user discussion comments
                        try:
                            comments, raw_comments = await yt_collector.fetch_comments(
                                artifact.native_id, max_comments=25
                            )
                            if comments:
                                for c in comments:
                                    c.run_id = self.run_id
                                    c.query_id = artifact.query_id
                                self.corpus.store_raw(
                                    raw_comments,
                                    platform="youtube",
                                    query_id=f"comments_{artifact.native_id[:8]}",
                                )
                                new_c = self.corpus.store_artifacts(comments)
                                total_comments += new_c
                        except Exception:
                            pass

        # Finalize manifest
        manifest.completed_at = datetime.now(UTC)
        manifest.status = "completed"
        manifest.total_queries = queries_executed
        manifest.total_artifacts = len(collected_artifacts)
        manifest.total_media = total_media
        manifest.platforms_searched = sorted(platforms_searched)

        manifest_path = self.run_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as mf:
            mf.write(manifest.model_dump_json(indent=2))

        # Generate human-readable run summary memo
        self._write_run_memo(manifest, collected_artifacts)

        # Step 3: Run discourse synthesis & drama analysis
        try:
            from observatory.analysis import DiscourseAnalyzer

            analyzer = DiscourseAnalyzer(settings=self.settings)
            analyzer.analyze_run(self.run_id)
        except Exception:
            pass

        return manifest

    def _write_run_memo(self, manifest: RunManifest, artifacts: list[Artifact]) -> None:
        """Write a comprehensive research memo for the run."""
        memo_path = self.run_dir / "RUN_SUMMARY.md"
        lines = [
            f"# Run Summary: {manifest.run_id}",
            "",
            f"- **Inquiry ID:** `{manifest.inquiry_id}`",
            f"- **Question:** {self.inquiry.question.strip()}",
            f"- **Started:** {manifest.started_at}",
            f"- **Completed:** {manifest.completed_at}",
            f"- **Platforms:** {', '.join(manifest.platforms_searched)}",
            f"- **Total Queries Executed:** {manifest.total_queries}",
            f"- **Total Artifacts Collected:** {manifest.total_artifacts}",
            f"- **Media Enriched:** {manifest.total_media}",
            "",
            "## Collected Evidence Highlights",
            "",
            "| # | Platform | Author | Score / Views | Content Preview | Canonical Link |",
            "|---|---|---|---|---|---|",
        ]

        for i, a in enumerate(artifacts[:20], 1):
            eng = a.engagement.likes if a.engagement else 0
            views = ""
            if a.engagement and a.engagement.views:
                views = f" ({a.engagement.views:,} views)"
            score_str = f"{eng}{views}"
            preview = (a.text or "").replace("\n", " ")[:80]
            link = f"[Link]({a.canonical_url})" if a.canonical_url else "-"
            author = a.author_handle or "unknown"
            lines.append(
                f"| {i} | {a.platform.value} | {author} | {score_str} | {preview}... | {link} |"
            )

        if len(artifacts) > 20:
            lines.append(f"\n*...and {len(artifacts) - 20} more artifacts stored in Parquet.*")

        # Media downloads section
        media_dir = self.run_dir / "media"
        if media_dir.exists():
            media_files = list(media_dir.glob("*.mp4")) + list(media_dir.glob("*.webm"))
            if media_files:
                lines.extend([
                    "",
                    "## Captured Raw Video Footage & Media Files",
                    "",
                    "| File Name | Size (MB) | Local Path |",
                    "|---|---|---|",
                ])
                for mf in media_files:
                    size_mb = mf.stat().st_size / (1024 * 1024)
                    lines.append(f"| `{mf.name}` | {size_mb:.2f} MB | `{mf}` |")

        with open(memo_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
