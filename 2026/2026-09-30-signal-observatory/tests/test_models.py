"""Tests for core domain models."""

from datetime import UTC, datetime

from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Inquiry,
    InquiryMode,
    InquiryScope,
    InquirySeeds,
    Platform,
    PreservationLevel,
    TimeScope,
    artifact_id,
)


class TestArtifactId:
    """Deterministic artifact ID generation."""

    def test_same_input_same_id(self) -> None:
        id1 = artifact_id("bluesky", "at://did:plc:abc/app.bsky.feed.post/123")
        id2 = artifact_id("bluesky", "at://did:plc:abc/app.bsky.feed.post/123")
        assert id1 == id2

    def test_different_platform_different_id(self) -> None:
        id1 = artifact_id("bluesky", "123")
        id2 = artifact_id("youtube", "123")
        assert id1 != id2

    def test_returns_hex_sha256(self) -> None:
        result = artifact_id("bluesky", "test")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestArtifact:
    """Artifact model behavior."""

    def test_computed_artifact_id(self) -> None:
        artifact = Artifact(
            platform=Platform.BLUESKY,
            native_id="at://did:plc:abc/app.bsky.feed.post/123",
            content_type=ContentType.POST,
        )
        expected = artifact_id("bluesky", "at://did:plc:abc/app.bsky.feed.post/123")
        assert artifact.artifact_id == expected

    def test_default_values(self) -> None:
        artifact = Artifact(
            platform=Platform.BLUESKY,
            native_id="test",
            content_type=ContentType.POST,
        )
        assert artifact.discovery_method == DiscoveryMethod.SEARCH
        assert artifact.media_refs == []
        assert artifact.thread_parent is None

    def test_engagement_snapshot(self) -> None:
        engagement = EngagementSnapshot(likes=42, reposts=10, replies=5)
        artifact = Artifact(
            platform=Platform.BLUESKY,
            native_id="test",
            content_type=ContentType.POST,
            engagement=engagement,
        )
        assert artifact.engagement is not None
        assert artifact.engagement.likes == 42


class TestInquiry:
    """Inquiry model behavior."""

    def test_minimal_inquiry(self) -> None:
        inquiry = Inquiry(
            id="test-inquiry",
            question="What is happening?",
            scope=InquiryScope(
                time=TimeScope(since=datetime(2026, 9, 1, tzinfo=UTC)),
            ),
        )
        assert inquiry.mode == InquiryMode.INVESTIGATE
        assert inquiry.platforms == [Platform.BLUESKY]
        assert inquiry.preservation == PreservationLevel.CANDIDATES

    def test_full_inquiry(self) -> None:
        inquiry = Inquiry(
            id="kc-ice-activity",
            question="What discourse exists around ICE activity in KC?",
            mode=InquiryMode.INVESTIGATE,
            scope=InquiryScope(
                time=TimeScope(
                    since=datetime(2026, 9, 1, tzinfo=UTC),
                    until=datetime(2026, 9, 30, tzinfo=UTC),
                ),
                geography=["Kansas City", "Wyandotte County"],
                languages=["en", "es"],
            ),
            seeds=InquirySeeds(
                terms=["ICE raid", "immigration enforcement"],
                hashtags=["#ICE", "#KansasCity"],
            ),
            platforms=[Platform.BLUESKY],
            preservation=PreservationLevel.FULL,
        )
        assert len(inquiry.seeds.terms) == 2
        assert inquiry.preservation == PreservationLevel.FULL
