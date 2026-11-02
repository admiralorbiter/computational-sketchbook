"""Tests for ReviewsCollector."""

from observatory.collectors.reviews import ReviewsCollector
from observatory.models import ContentType, Platform, TimestampQuality


class TestReviewsCollector:
    """Test reviews collector normalization and capabilities."""

    def test_capabilities(self) -> None:
        collector = ReviewsCollector()
        caps = collector.capabilities()
        assert caps.can_search is True
        assert caps.requires_auth is False
        assert collector.platform == Platform.REVIEWS

    def test_normalize_review(self) -> None:
        collector = ReviewsCollector()
        record = {
            "business": "In-A-Tub",
            "author": "Alice",
            "text": "The powdered cheese deep fried tacos are legendary in the Northland!",
            "rating": 5.0,
            "source_type": "review_directory",
        }
        url = "https://www.restaurantji.com/mo/kansas-city/in-a-tub-/"
        artifact = collector._normalize_review(record, url)

        assert artifact.platform == Platform.REVIEWS
        assert artifact.content_type == ContentType.REVIEW
        assert artifact.author_handle == "Alice"
        assert "powdered cheese" in artifact.text
        assert artifact.engagement is not None
        assert artifact.engagement.likes == 5
        assert artifact.engagement.extra["business"] == "In-A-Tub"
        assert artifact.canonical_url == url
        assert artifact.published_at is not None
        assert artifact.published_at_quality == TimestampQuality.COLLECTION_FALLBACK

    def test_date_parsing_qualities(self) -> None:
        collector = ReviewsCollector()
        dt1, q1 = collector._parse_review_date("2023-10-15", "review_directory")
        assert dt1.year == 2023 and dt1.month == 10 and dt1.day == 15
        assert q1 == TimestampQuality.SOURCE_DATE_ONLY

        dt2, q2 = collector._parse_review_date("2024-01-10T14:30:00Z", "review_directory")
        assert q2 == TimestampQuality.SOURCE_EXACT

        dt3, q3 = collector._parse_review_date("2 weeks ago", "review_directory")
        assert q3 == TimestampQuality.INFERRED

        dt4, q4 = collector._parse_review_date("Jan 12, 2024", "web_review_index")
        assert q4 == TimestampQuality.SEARCH_INDEX
