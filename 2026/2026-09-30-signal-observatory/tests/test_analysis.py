"""Tests for the Discourse Analysis & Drama Engine."""

from observatory.analysis import DiscourseAnalyzer
from observatory.models import Artifact, ContentType, DiscoveryMethod, Platform
from observatory.store.corpus import CorpusStore


def _make_sample_artifact(
    native_id: str, text: str, content_type: ContentType = ContentType.POST
) -> Artifact:
    return Artifact(
        platform=Platform.YOUTUBE,
        native_id=native_id,
        content_type=content_type,
        text=text,
        author_handle="test_user",
        discovery_method=DiscoveryMethod.SEARCH,
        run_id="test_run_1",
        collector_version="test-0.1.0",
        raw_record_hash="hash123",
    )


class TestDiscourseAnalyzer:
    """Test faction classification and friction detection."""

    def test_friction_detection(self, test_corpus: CorpusStore) -> None:
        analyzer = DiscourseAnalyzer(settings=test_corpus.settings)
        artifacts = [
            _make_sample_artifact(
                "v1",
                "The roof had a partial collapse due to unpermitted "
                "renovation and code violations!",
            ),
            _make_sample_artifact(
                "v2",
                "Normal sunny day in Kansas City park with birds chirping.",
            ),
            _make_sample_artifact(
                "v3",
                "Missouri sues over deceptive pricing discrepancy, "
                "overcharging customers at register!",
            ),
        ]

        res = analyzer._synthesize(artifacts, {}, "test_run_1")
        assert res["total_artifacts"] == 3
        assert res["total_friction_events"] == 2

        # Verify friction categories matched
        top_friction = res["friction_events"][0]
        assert (
            "Blight, Hazard & Code Enforcement" in top_friction["categories"]
            or "Labor Strain & Consumer Friction" in top_friction["categories"]
        )

    def test_faction_classification(self, test_corpus: CorpusStore) -> None:
        analyzer = DiscourseAnalyzer(settings=test_corpus.settings)
        artifacts = [
            _make_sample_artifact(
                "c1",
                "I live in this neighborhood and my kid goes to school down the street.",
                content_type=ContentType.COMMENT,
            ),
            _make_sample_artifact(
                "w1",
                "The staff in our store is understaffed and we only have "
                "one person working the shift.",
                content_type=ContentType.COMMENT,
            ),
            _make_sample_artifact(
                "p1",
                "District spokesperson announced an official statement on board approved plan.",
                content_type=ContentType.POST,
            ),
        ]

        res = analyzer._synthesize(artifacts, {}, "test_run_1")
        assert len(res["factions"]["resident_shopper"]) >= 1
        assert len(res["factions"]["frontline_worker"]) >= 1
        assert len(res["factions"]["institutional_leadership"]) >= 1
        assert len(res["annotations"]) >= 3
