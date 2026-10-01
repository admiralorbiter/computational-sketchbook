"""Core domain models for the Signal Observatory.

All collected evidence flows through these models. The key architectural invariant
is that Artifacts (observed evidence) and Annotations (model-derived interpretations)
are always stored separately. Annotations reference artifacts but never contaminate them.
"""

import hashlib
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, computed_field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Platform(StrEnum):
    """Supported collection platforms."""

    BLUESKY = "bluesky"
    YOUTUBE = "youtube"
    REDDIT = "reddit"
    WEB = "web"
    REVIEWS = "reviews"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    CITIZEN = "citizen"
    SNAPCHAT = "snapchat"


class ContentType(StrEnum):
    """Type of collected content."""

    POST = "post"
    COMMENT = "comment"
    VIDEO = "video"
    THREAD = "thread"
    IMAGE = "image"
    ARTICLE = "article"
    REVIEW = "review"
    FOOTAGE = "footage"


class DiscoveryMethod(StrEnum):
    """How this artifact was found."""

    SEARCH = "search"
    THREAD_EXPANSION = "thread_expansion"
    MEDIA_TRACE = "media_trace"
    FIREHOSE = "firehose"
    MANUAL = "manual"
    LINKED = "linked"


class PreservationLevel(StrEnum):
    """How much evidence to preserve."""

    METADATA = "metadata"
    CANDIDATES = "candidates"
    FULL = "full"


class InquiryMode(StrEnum):
    """Research mode for an inquiry."""

    INVESTIGATE = "investigate"
    WATCH = "watch"
    DISCOVER = "discover"


class AnnotationType(StrEnum):
    """Types of model-derived annotations."""

    TOPIC = "topic"
    STANCE = "stance"
    FRAME = "frame"
    TRANSCRIPTION = "transcription"
    IMAGE_DESCRIPTION = "image_description"
    SUMMARY = "summary"
    LANGUAGE = "language"
    CLAIM = "claim"
    FRICTION = "friction"


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------


def artifact_id(platform: str, native_id: str) -> str:
    """Generate a deterministic artifact ID from platform and native ID.

    The same post always produces the same artifact_id regardless of
    when or how it was collected.

    Args:
        platform: The source platform name.
        native_id: The platform's native identifier for the content.

    Returns:
        A hex SHA-256 hash string.
    """
    raw = f"{platform}:{native_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class EngagementSnapshot(BaseModel):
    """Point-in-time engagement metrics.

    Platform-specific fields are stored in `extra` to avoid
    an ever-growing union of platform schemas.
    """

    likes: int = 0
    reposts: int = 0
    replies: int = 0
    views: int | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    extra: dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    """A single piece of collected evidence.

    This is the fundamental unit of the corpus. Every artifact has a
    deterministic ID derived from its platform and native identifier,
    ensuring natural deduplication.
    """

    platform: Platform
    native_id: str
    canonical_url: str | None = None
    content_type: ContentType

    # Source metadata
    author_handle: str | None = None
    author_platform_id: str | None = None
    published_at: datetime | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    language: str | None = None

    # Content
    text: str | None = None
    media_refs: list[str] = Field(default_factory=list)
    thread_parent: str | None = None

    # Engagement
    engagement: EngagementSnapshot | None = None

    # Provenance
    query_id: str | None = None
    discovery_method: DiscoveryMethod = DiscoveryMethod.SEARCH
    run_id: str = ""
    collector_version: str = ""
    raw_record_hash: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def artifact_id(self) -> str:
        """Deterministic ID: SHA-256 of platform:native_id."""
        return artifact_id(self.platform.value, self.native_id)


class Annotation(BaseModel):
    """A model-derived interpretation of an artifact.

    Annotations are always stored separately from artifacts.
    They carry full attribution so you know which model, prompt,
    and version produced them.
    """

    annotation_id: str
    artifact_id: str
    annotation_type: AnnotationType
    value: Any
    model: str
    model_version: str = ""
    prompt_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: float | None = None


# ---------------------------------------------------------------------------
# Inquiry & Run Models
# ---------------------------------------------------------------------------


class TimeScope(BaseModel):
    """Time boundaries for an inquiry."""

    since: datetime
    until: datetime | None = None


class InquiryScope(BaseModel):
    """Geographic, temporal, and linguistic scope."""

    time: TimeScope
    geography: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


class InquirySeeds(BaseModel):
    """Starting points for investigation."""

    terms: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    accounts: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)


class InquiryBudget(BaseModel):
    """Resource limits for a research run."""

    max_queries: int = 100
    max_artifacts: int = 1000
    max_media_downloads: int = 100


class Inquiry(BaseModel):
    """A research question with scope, seeds, and constraints.

    This is the primary input to the observatory. An inquiry defines
    what to investigate, where to look, and how much evidence to collect.
    """

    id: str
    question: str
    mode: InquiryMode = InquiryMode.INVESTIGATE
    scope: InquiryScope
    seeds: InquirySeeds = Field(default_factory=InquirySeeds)
    platforms: list[Platform] = Field(default_factory=lambda: [Platform.BLUESKY])
    budget: InquiryBudget = Field(default_factory=InquiryBudget)
    preservation: PreservationLevel = PreservationLevel.CANDIDATES
    analysis: dict[str, bool] = Field(default_factory=dict)


class QueryRecord(BaseModel):
    """Record of a single search query executed during a run."""

    query_id: str
    run_id: str
    platform: Platform
    query_text: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result_count: int = 0
    cursor: str | None = None
    parent_query_id: str | None = None  # if this was an expansion


class RunManifest(BaseModel):
    """Manifest tracking a complete research run."""

    run_id: str
    inquiry_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    status: str = "running"
    total_queries: int = 0
    total_artifacts: int = 0
    total_media: int = 0
    platforms_searched: list[str] = Field(default_factory=list)
    notes: str = ""
