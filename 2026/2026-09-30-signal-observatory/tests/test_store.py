"""Tests for the corpus store."""

from observatory.models import Artifact, ContentType, DiscoveryMethod, Platform
from observatory.store.corpus import CorpusStore


def _make_artifact(native_id: str = "test-123", text: str = "Hello world") -> Artifact:
    """Create a test artifact."""
    return Artifact(
        platform=Platform.BLUESKY,
        native_id=native_id,
        content_type=ContentType.POST,
        text=text,
        author_handle="test.bsky.social",
        discovery_method=DiscoveryMethod.SEARCH,
        run_id="test-run",
        collector_version="test-0.1.0",
        raw_record_hash="abc123",
    )


class TestCorpusStore:
    """Corpus store operations."""

    def test_store_raw(self, test_corpus: CorpusStore) -> None:
        records = [{"id": "1", "text": "test"}]
        path = test_corpus.store_raw(records, platform="bluesky", query_id="q1")
        assert path.exists()
        assert path.suffix == ".jsonl"

    def test_store_artifacts(self, test_corpus: CorpusStore) -> None:
        artifacts = [_make_artifact("id-1"), _make_artifact("id-2")]
        count = test_corpus.store_artifacts(artifacts)
        assert count == 2

    def test_deduplication(self, test_corpus: CorpusStore) -> None:
        artifacts = [_make_artifact("id-1")]
        test_corpus.store_artifacts(artifacts)
        # Store the same artifact again
        count = test_corpus.store_artifacts(artifacts)
        assert count == 0  # No new artifacts

    def test_corpus_stats_empty(self, test_corpus: CorpusStore) -> None:
        stats = test_corpus.corpus_stats()
        assert stats["artifacts"] == 0
        assert stats["annotations"] == 0

    def test_corpus_stats_with_data(self, test_corpus: CorpusStore) -> None:
        artifacts = [_make_artifact("id-1"), _make_artifact("id-2")]
        test_corpus.store_artifacts(artifacts)
        stats = test_corpus.corpus_stats()
        assert stats["artifacts"] == 2
        assert "bluesky" in stats["platforms"]

    def test_sql_query(self, test_corpus: CorpusStore) -> None:
        artifacts = [_make_artifact("id-1", "Hello"), _make_artifact("id-2", "World")]
        test_corpus.store_artifacts(artifacts)
        result = test_corpus.query("SELECT COUNT(*) AS n FROM artifacts")
        assert result["n"][0] == 2
