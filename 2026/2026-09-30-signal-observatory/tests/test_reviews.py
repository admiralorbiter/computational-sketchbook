"""Tests for ReviewsCollector."""

from observatory.collectors.reviews import ReviewsCollector
from observatory.models import ContentType, Platform


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
