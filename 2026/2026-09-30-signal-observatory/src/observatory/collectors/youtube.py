"""YouTube collector using yt-dlp and youtube-transcript-api.

No API keys required. This collector uses:
- yt-dlp for search, video metadata, and subtitle/caption extraction
- youtube-transcript-api for transcript retrieval

yt-dlp extracts richer metadata than the official API in many cases,
including view counts, like counts, comment counts, upload dates,
descriptions, tags, chapters, and subtitle tracks — all without
any authentication or quota limits.
"""

import hashlib
import json
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson
from tenacity import retry, stop_after_attempt, wait_exponential

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Platform,
)

COLLECTOR_VERSION = "youtube-collector-0.1.0"


def _run_ytdlp(args: list[str], timeout: int = 60) -> str:
    """Run yt-dlp as a subprocess and return stdout.

    Args:
        args: Command-line arguments to pass to yt-dlp.
        timeout: Maximum seconds to wait.

    Returns:
        Stdout as a string.

    Raises:
        RuntimeError: If yt-dlp exits with an error.
    """
    cmd = ["yt-dlp", *args]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp error: {result.stderr.strip()}")
    return result.stdout


def _parse_ytdlp_date(date_str: str | None) -> datetime | None:
    """Parse yt-dlp's YYYYMMDD date format."""
    if not date_str or len(date_str) != 8:
        return None
    try:
        return datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC)
    except ValueError:
        return None


class YouTubeCollector(BaseCollector):
    """Collector for YouTube using yt-dlp and youtube-transcript-api.

    No API key or authentication required.
    """

    @property
    def platform(self) -> Platform:
        return Platform.YOUTUBE

    @property
    def version(self) -> str:
        return COLLECTOR_VERSION

    def capabilities(self) -> CollectorCapabilities:
        return CollectorCapabilities(
            can_search=True,
            can_fetch=True,
            can_fetch_thread=False,
            can_stream=False,
            can_snapshot_engagement=True,
            supported_search_params=["query", "limit"],
            max_results_per_query=50,
            requires_auth=False,
            rate_limit_info="No official rate limit; self-throttle to be respectful",
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def search(
        self,
        query: str,
        *,
        limit: int = 20,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search YouTube for videos matching a query.

        Uses yt-dlp's ytsearch to find videos. Note: yt-dlp search
        does not support date filtering directly, but results can be
        post-filtered by upload date.

        Args:
            query: Search query string.
            limit: Maximum number of results (default 20, max ~50).
            since: Not directly supported by yt-dlp search; used for post-filtering.
            until: Not directly supported by yt-dlp search; used for post-filtering.
            cursor: Not supported for YouTube search.

        Returns:
            Tuple of (artifacts, next_cursor, raw_records).
        """
        # yt-dlp search syntax: ytsearchN:query
        search_query = f"ytsearch{limit}:{query}"

        raw_output = _run_ytdlp(
            [
                search_query,
                "--dump-json",
                "--no-download",
                "--flat-playlist",
            ],
            timeout=120,
        )

        raw_records: list[dict[str, Any]] = []
        artifacts: list[Artifact] = []

        for line in raw_output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            raw_records.append(record)
            artifact = self._normalize_video(record)

            # Post-filter by date if specified
            if since and artifact.published_at:
                since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
                if artifact.published_at < since_dt:
                    continue
            if until and artifact.published_at:
                until_dt = datetime.fromisoformat(until.replace("Z", "+00:00"))
                if artifact.published_at > until_dt:
                    continue

            artifacts.append(artifact)

        return artifacts, None, raw_records

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch metadata for a single YouTube video.

        Args:
            native_id: YouTube video ID (e.g. 'dQw4w9WgXcQ') or full URL.

        Returns:
            Tuple of (artifact, raw_record) or (None, None).
        """
        url = native_id
        if not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={native_id}"

        try:
            raw_output = _run_ytdlp(
                [url, "--dump-json", "--no-download"],
                timeout=60,
            )
            record = json.loads(raw_output.strip())
            return self._normalize_video(record), record
        except (RuntimeError, json.JSONDecodeError):
            return None, None

    async def fetch_transcript(
        self, video_id: str, languages: list[str] | None = None
    ) -> str | None:
        """Fetch the transcript for a YouTube video.

        Uses youtube-transcript-api which extracts transcripts from
        YouTube's player caption tracks without any API key.

        Args:
            video_id: YouTube video ID.
            languages: Preferred languages (defaults to ['en']).

        Returns:
            Full transcript text, or None if unavailable.
        """
        langs = languages or ["en"]
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            api = YouTubeTranscriptApi()
            if hasattr(api, "fetch"):
                fetched = api.fetch(video_id, languages=langs)
                return " ".join(item.text for item in fetched)
            elif hasattr(YouTubeTranscriptApi, "get_transcript"):
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)
                return " ".join(entry["text"] for entry in transcript)
            return None
        except Exception:
            return None

    async def fetch_comments(
        self, video_id: str, max_comments: int = 50
    ) -> tuple[list[Artifact], list[dict[str, Any]]]:
        """Harvest real user comments from a YouTube video discussion section.

        Uses yt-dlp to extract user comments, upvotes, and author handles
        without requiring any YouTube API key or authentication.

        Args:
            video_id: YouTube video ID.
            max_comments: Maximum number of comments to extract.

        Returns:
            Tuple of (list of comment Artifacts, raw comment dicts).
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        args = [
            url,
            "--write-comments",
            "--dump-json",
            "--no-download",
            "--extractor-args",
            f"youtube:max_comments={max_comments}",
        ]

        try:
            raw_output = _run_ytdlp(args, timeout=60)
            data = json.loads(raw_output.strip().split("\n")[0])
            raw_comments = data.get("comments") or []
        except Exception:
            return [], []

        artifacts: list[Artifact] = []
        for c in raw_comments:
            c_id = c.get("id") or str(uuid.uuid4())[:8]
            text = c.get("text", "")
            if not text:
                continue

            author = c.get("author") or "anonymous"
            likes = c.get("like_count") or 0

            # Parse comment timestamp if available
            timestamp = None
            ts = c.get("timestamp")
            if ts:
                try:
                    timestamp = datetime.fromtimestamp(ts, tz=UTC)
                except Exception:
                    pass

            raw_bytes = orjson.dumps(c, option=orjson.OPT_SORT_KEYS)
            raw_hash = hashlib.sha256(raw_bytes).hexdigest()

            comment_artifact = Artifact(
                platform=Platform.YOUTUBE,
                native_id=f"{video_id}#comment_{c_id}",
                canonical_url=f"https://www.youtube.com/watch?v={video_id}&lc={c_id}",
                content_type=ContentType.COMMENT,
                author_handle=author,
                author_platform_id=c.get("author_id", ""),
                published_at=timestamp,
                text=text,
                thread_parent=video_id,
                engagement=EngagementSnapshot(likes=likes),
                discovery_method=DiscoveryMethod.THREAD_EXPANSION,
                collector_version=COLLECTOR_VERSION,
                raw_record_hash=raw_hash,
            )
            artifacts.append(comment_artifact)

        return artifacts, raw_comments

    def download_video(
        self,
        video_id: str,
        output_dir: Path | str,
        max_height: int = 720,
    ) -> Path | None:
        """Download raw video footage using yt-dlp.

        Args:
            video_id: YouTube video ID or full URL.
            output_dir: Directory where the MP4 file will be stored.
            max_height: Max video resolution (defaults to 720p).

        Returns:
            Path to downloaded video file, or None if failed.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        clean_id = video_id.split("v=")[-1].split("&")[0].split("/")[-1]
        out_template = str(out_path / f"{clean_id}.%(ext)s")
        target_file = out_path / f"{clean_id}.mp4"

        if target_file.exists():
            return target_file

        url = f"https://www.youtube.com/watch?v={clean_id}"
        args = [
            "-f",
            f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best",
            "--merge-output-format",
            "mp4",
            "-o",
            out_template,
            "--no-playlist",
            url,
        ]

        try:
            _run_ytdlp(args, timeout=180)
            if target_file.exists():
                return target_file
            matches = list(out_path.glob(f"{clean_id}.*"))
            if matches:
                return matches[0]
            return None
        except Exception:
            return None

    def _normalize_video(self, record: dict[str, Any]) -> Artifact:
        """Convert yt-dlp JSON output into a normalized Artifact."""
        video_id = record.get("id", "")
        title = record.get("title", "")
        description = record.get("description", "")

        # Combine title and description as text
        text_parts = [title]
        if description:
            text_parts.append(description)
        text = "\n\n".join(text_parts)

        engagement = EngagementSnapshot(
            likes=record.get("like_count") or 0,
            views=record.get("view_count"),
            replies=record.get("comment_count") or 0,
            extra={
                "duration": record.get("duration"),
                "tags": record.get("tags", []),
                "categories": record.get("categories", []),
                "channel_follower_count": record.get("channel_follower_count"),
            },
        )

        # Extract thumbnail as media ref
        media_refs: list[str] = []
        thumbnail = record.get("thumbnail")
        if thumbnail:
            media_refs.append(thumbnail)

        raw_bytes = orjson.dumps(record, option=orjson.OPT_SORT_KEYS)
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()

        return Artifact(
            platform=Platform.YOUTUBE,
            native_id=video_id,
            canonical_url=record.get("webpage_url", f"https://www.youtube.com/watch?v={video_id}"),
            content_type=ContentType.VIDEO,
            author_handle=record.get("uploader") or record.get("channel"),
            author_platform_id=record.get("channel_id", ""),
            published_at=_parse_ytdlp_date(record.get("upload_date")),
            language=record.get("language"),
            text=text,
            media_refs=media_refs,
            engagement=engagement,
            discovery_method=DiscoveryMethod.SEARCH,
            collector_version=COLLECTOR_VERSION,
            raw_record_hash=raw_hash,
        )
