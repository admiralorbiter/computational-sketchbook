"""Culture Migration Graph — cross-platform travel, latency, and semantic mutation.

Tracks how cultural objects, memes, slang terms, emerging venue scenes, or consumer
controversies travel across platforms (e.g. TikTok -> Reddit -> YouTube -> Web).

Core Epistemic Principles:
- "Earliest appearance in the observed corpus", never "This creator invented it".
- Reconstruct latency between hops: Delta t = t_target - t_source.
- Measure lexical mutation: vocabulary divergence and newly introduced terms at each hop.
- Quantify creator expansion: how many independent creators appeared before first crossover.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from observatory.config import Settings, get_settings
from observatory.models import Artifact, Platform, TimestampQuality
from observatory.store.corpus import CorpusStore

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's",
    "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "http", "https", "com", "www", "video", "post", "like", "just", "get", "one", "also",
}


def _tokenize(text: str) -> list[str]:
    """Tokenize and normalize text into meaningful terms."""
    import re
    cleaned = re.sub(r"[^a-zA-Z0-9#@_\s]", " ", text.lower())
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 2]
    return [t for t in tokens if t not in STOPWORDS]


class MigrationNode(BaseModel):
    """A point of observation within a migration timeline."""

    artifact_id: str
    platform: Platform
    author: str
    published_at: datetime
    published_at_quality: TimestampQuality
    text_snippet: str
    canonical_url: str | None = None
    views: int | None = None
    likes: int = 0


class MigrationHop(BaseModel):
    """Transition edge between two platform appearances."""

    source_node: MigrationNode
    target_node: MigrationNode
    latency_hours: float
    jaccard_divergence: float
    new_keywords: list[str] = Field(default_factory=list)
    top_shared_keywords: list[str] = Field(default_factory=list)


class CultureMigrationGraph(BaseModel):
    """Complete graph reconstructing how a phenomenon migrated across digital spaces."""

    query: str
    total_artifacts_analyzed: int
    platforms_observed: list[Platform]
    earliest_appearance: MigrationNode | None = None
    timeline_nodes: list[MigrationNode] = Field(default_factory=list)
    hops: list[MigrationHop] = Field(default_factory=list)
    time_to_second_platform_hours: float | None = None
    time_to_mainstream_hours: float | None = None
    creators_before_crossover: int = 0
    originating_platform: Platform | None = None
    role_classification: str = "single_platform"  # originator, multi_platform_crossover, etc.
    mermaid_diagram: str = ""

    def summary_markdown(self) -> str:
        """Generate GitHub-flavored markdown narrative of the migration graph."""
        lines = [
            f"# Culture Migration Graph: '{self.query}'",
            "",
            f"- **Platforms Observed:** {', '.join(p.value for p in self.platforms_observed)}",
            f"- **Total Evidence Traces:** {self.total_artifacts_analyzed}",
            f"- **Independent Creators Before Crossover:** {self.creators_before_crossover}",
        ]

        if self.earliest_appearance:
            lines.extend([
                f"- **Earliest Observed Platform:** `{self.earliest_appearance.platform.value}`",
                (
                    f"- **Earliest Observed Date:** "
                    f"{self.earliest_appearance.published_at.strftime('%Y-%m-%d %H:%M UTC')} "
                    f"({self.earliest_appearance.published_at_quality.value})"
                ),
            ])

        if self.time_to_second_platform_hours is not None:
            lines.append(
                f"- **Time to Second Platform:** {self.time_to_second_platform_hours:.1f} hours "
                f"({self.time_to_second_platform_hours / 24.0:.1f} days)"
            )

        if self.time_to_mainstream_hours is not None:
            lines.append(
                f"- **Time to Mainstream/Press:** {self.time_to_mainstream_hours:.1f} hours "
                f"({self.time_to_mainstream_hours / 24.0:.1f} days)"
            )

        lines.extend([
            "",
            "## Visual Migration Path",
            "```mermaid",
            self.mermaid_diagram,
            "```",
            "",
            "## Cross-Platform Hops & Lexical Mutation",
        ])

        for i, hop in enumerate(self.hops, start=1):
            src_p = hop.source_node.platform.value
            tgt_p = hop.target_node.platform.value
            new_kw = ", ".join(f"`{k}`" for k in hop.new_keywords[:6]) or "_None_"
            shared_kw = ", ".join(f"`{k}`" for k in hop.top_shared_keywords[:6]) or "_None_"

            lines.extend([
                f"### Hop {i}: {src_p} -> {tgt_p} (+{hop.latency_hours:.1f}h)",
                f"- **From:** @{hop.source_node.author} ({src_p}) at "
                f"{hop.source_node.published_at.strftime('%Y-%m-%d %H:%M')}",
                f"- **To:** @{hop.target_node.author} ({tgt_p}) at "
                f"{hop.target_node.published_at.strftime('%Y-%m-%d %H:%M')}",
                f"- **Lexical Divergence:** {hop.jaccard_divergence * 100:.1f}%",
                f"- **New Vocabulary Introduced:** {new_kw}",
                f"- **Shared Anchor Keywords:** {shared_kw}",
                f"- **Target Snippet:** \"{hop.target_node.text_snippet}\"",
                "",
            ])

        return "\n".join(lines)


class CultureMigrationAnalyzer:
    """Extracts and traces cultural migration trajectories across corpus artifacts."""

    def __init__(self, store: CorpusStore | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.store = store or CorpusStore(self.settings)

    def trace(
        self,
        query: str,
        artifacts: list[Artifact] | None = None,
        min_quality: list[TimestampQuality] | None = None,
    ) -> CultureMigrationGraph:
        """Trace cross-platform migration for a search query or artifact collection.

        Args:
            query: Term or topic to trace.
            artifacts: Optional explicit artifact set. If None, queries corpus DuckDB.
            min_quality: Allowed timestamp qualities (defaults to excluding fallbacks).
        """
        if artifacts is None:
            arts = self._load_matching_artifacts(query)
        else:
            arts = artifacts

        allowed_qualities = min_quality or [
            TimestampQuality.SOURCE_EXACT,
            TimestampQuality.SOURCE_DATE_ONLY,
            TimestampQuality.SEARCH_INDEX,
            TimestampQuality.INFERRED,
            TimestampQuality.UNKNOWN,
        ]

        def _to_utc(dt: datetime) -> datetime:
            return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)

        # Filter out artifacts with missing or disallowed timestamps
        valid_arts = [
            a for a in arts
            if a.published_at is not None
            and a.published_at_quality in allowed_qualities
        ]

        # Sort chronologically with uniform timezone awareness
        valid_arts.sort(key=lambda a: _to_utc(a.published_at))  # type: ignore

        if not valid_arts:
            return CultureMigrationGraph(
                query=query,
                total_artifacts_analyzed=0,
                platforms_observed=[],
                role_classification="insufficient_evidence",
                mermaid_diagram="flowchart LR\n  empty[No chronologically valid traces found]",
            )

        # Convert to MigrationNodes
        nodes: list[MigrationNode] = []
        for a in valid_arts:
            author = a.author_handle or "anonymous"
            snippet = (a.text[:120] + "...") if len(a.text) > 120 else a.text
            likes = a.engagement.likes if a.engagement else 0
            views = a.engagement.views if a.engagement else None

            nodes.append(
                MigrationNode(
                    artifact_id=a.artifact_id,
                    platform=a.platform,
                    author=author,
                    published_at=a.published_at,  # type: ignore
                    published_at_quality=a.published_at_quality,
                    text_snippet=snippet.replace("\n", " "),
                    canonical_url=a.canonical_url,
                    views=views,
                    likes=likes,
                )
            )

        earliest = nodes[0]
        origin_platform = earliest.platform

        # Track discovery order of distinct platforms
        seen_platforms: list[Platform] = []
        platform_first_nodes: dict[Platform, MigrationNode] = {}

        for n in nodes:
            if n.platform not in seen_platforms:
                seen_platforms.append(n.platform)
                platform_first_nodes[n.platform] = n

        # Count independent creators prior to the first crossover hop
        creators_before_crossover = 0
        if len(seen_platforms) > 1:
            second_platform = seen_platforms[1]
            first_crossover_time = platform_first_nodes[second_platform].published_at
            pre_crossover_authors = {
                n.author for n in nodes if n.published_at < first_crossover_time
            }
            creators_before_crossover = len(pre_crossover_authors)
        else:
            creators_before_crossover = len({n.author for n in nodes})

        # Build chronological platform migration hops
        hops: list[MigrationHop] = []
        time_to_second: float | None = None
        time_to_mainstream: float | None = None

        for i in range(len(seen_platforms) - 1):
            src_p = seen_platforms[i]
            tgt_p = seen_platforms[i + 1]
            src_node = platform_first_nodes[src_p]
            tgt_node = platform_first_nodes[tgt_p]

            latency_sec = max(
                (tgt_node.published_at - src_node.published_at).total_seconds(), 0.0
            )
            latency_hours = round(latency_sec / 3600.0, 2)

            if i == 0:
                time_to_second = latency_hours

            if tgt_p == Platform.WEB and time_to_mainstream is None:
                total_latency_sec = max(
                    (tgt_node.published_at - earliest.published_at).total_seconds(), 0.0
                )
                time_to_mainstream = round(total_latency_sec / 3600.0, 2)

            # Semantic mutation analysis
            src_tokens = _tokenize(src_node.text_snippet)
            tgt_tokens = _tokenize(tgt_node.text_snippet)
            src_set = set(src_tokens)
            tgt_set = set(tgt_tokens)

            union = src_set.union(tgt_set)
            intersection = src_set.intersection(tgt_set)
            jaccard = (1.0 - (len(intersection) / len(union))) if union else 1.0

            new_terms = sorted(tgt_set - src_set)
            shared_terms = sorted(intersection)

            hops.append(
                MigrationHop(
                    source_node=src_node,
                    target_node=tgt_node,
                    latency_hours=latency_hours,
                    jaccard_divergence=round(jaccard, 3),
                    new_keywords=new_terms,
                    top_shared_keywords=shared_terms,
                )
            )

        mermaid = self._generate_mermaid(nodes, hops, seen_platforms)

        role = "single_platform"
        if len(seen_platforms) > 1:
            role = "multi_platform_crossover"
            if time_to_mainstream is not None:
                role = "crossover_to_mainstream"

        return CultureMigrationGraph(
            query=query,
            total_artifacts_analyzed=len(valid_arts),
            platforms_observed=seen_platforms,
            earliest_appearance=earliest,
            timeline_nodes=nodes,
            hops=hops,
            time_to_second_platform_hours=time_to_second,
            time_to_mainstream_hours=time_to_mainstream,
            creators_before_crossover=creators_before_crossover,
            originating_platform=origin_platform,
            role_classification=role,
            mermaid_diagram=mermaid,
        )

    def _generate_mermaid(
        self,
        nodes: list[MigrationNode],
        hops: list[MigrationHop],
        platforms: list[Platform],
    ) -> str:
        """Generate Mermaid flowchart visualizing cross-platform transitions."""
        lines = ["flowchart TD"]

        # Subgraph per platform
        platform_nodes: dict[Platform, list[MigrationNode]] = {}
        for n in nodes:
            platform_nodes.setdefault(n.platform, []).append(n)

        node_id_map: dict[str, str] = {}
        counter = 1

        for p in platforms:
            p_clean = p.value.capitalize()
            lines.append(f'  subgraph sg_{p.value} ["{p_clean}"]')
            # Show up to 2 key nodes per platform to keep diagram legible
            for n in platform_nodes[p][:2]:
                m_id = f"node_{counter}"
                counter += 1
                node_id_map[n.artifact_id] = m_id

                safe_author = n.author.replace('"', "'")
                date_str = n.published_at.strftime("%Y-%m-%d %H:%M")
                safe_snippet = (
                    n.text_snippet[:45].replace('"', "'") + "..."
                    if len(n.text_snippet) > 45
                    else n.text_snippet.replace('"', "'")
                )
                label = f'"{safe_author} ({date_str})<br/>{safe_snippet}"'
                lines.append(f"    {m_id}[{label}]")
            lines.append("  end")

        # Add transition edges for hops
        for hop in hops:
            src_id = node_id_map.get(hop.source_node.artifact_id)
            tgt_id = node_id_map.get(hop.target_node.artifact_id)
            if src_id and tgt_id:
                top_new = hop.new_keywords[0] if hop.new_keywords else "remix"
                edge_label = f'"+{hop.latency_hours:.1f}h | {top_new}"'
                lines.append(f"  {src_id} -->|{edge_label}| {tgt_id}")

        return "\n".join(lines)

    def _load_matching_artifacts(self, query: str) -> list[Artifact]:
        """Search Parquet corpus store for artifacts matching query."""
        artifacts_parquet = self.settings.normalized_dir / "artifacts.parquet"
        if not artifacts_parquet.exists():
            return []

        import polars as pl
        df = pl.read_parquet(artifacts_parquet)
        if df.height == 0:
            return []

        # Filter by text containing query (case insensitive)
        q_lower = query.lower()
        matching_rows = []
        for row in df.to_dicts():
            text = str(row.get("text", "")).lower()
            if q_lower in text:
                matching_rows.append(row)

        artifacts: list[Artifact] = []
        for row in matching_rows:
            try:
                # Reconstruct Artifact
                pub_at = None
                if row.get("published_at"):
                    pub_at = datetime.fromisoformat(row["published_at"])
                    if pub_at.tzinfo is None:
                        pub_at = pub_at.replace(tzinfo=UTC)
                    else:
                        pub_at = pub_at.astimezone(UTC)
                if row.get("observed_at"):
                    obs_at = datetime.fromisoformat(row["observed_at"])
                    if obs_at.tzinfo is None:
                        obs_at = obs_at.replace(tzinfo=UTC)
                    else:
                        obs_at = obs_at.astimezone(UTC)
                else:
                    obs_at = datetime.now(UTC)

                q_val = row.get("published_at_quality")
                if q_val and q_val in TimestampQuality:
                    quality = TimestampQuality(q_val)
                elif pub_at is not None:
                    plat_val = str(row.get("platform", "")).lower()
                    if plat_val in ("reddit", "youtube", "bluesky", "snapchat"):
                        quality = TimestampQuality.SOURCE_EXACT
                    elif plat_val in ("web", "reviews"):
                        quality = TimestampQuality.SOURCE_DATE_ONLY
                    else:
                        quality = TimestampQuality.UNKNOWN
                else:
                    quality = TimestampQuality.UNKNOWN

                art = Artifact(
                    platform=Platform(row["platform"]),
                    native_id=row["native_id"],
                    canonical_url=row.get("canonical_url"),
                    content_type=row.get("content_type", "post"),
                    author_handle=row.get("author_handle"),
                    published_at=pub_at,
                    published_at_quality=quality,
                    observed_at=obs_at,
                    text=row.get("text", ""),
                )
                artifacts.append(art)
            except Exception:
                continue

        return artifacts
