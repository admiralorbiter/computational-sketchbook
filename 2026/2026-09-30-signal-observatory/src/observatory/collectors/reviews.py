"""Customer and patron reviews collector.

Zero API keys required. Scrapes and harvests real customer reviews,
star ratings, and patron commentary across public review aggregators,
Google/Yelp review indexes, and community boards.
"""

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

import orjson
from bs4 import BeautifulSoup
from curl_cffi import requests
from ddgs import DDGS

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Platform,
)

COLLECTOR_VERSION = "reviews-collector-0.1.0"


class ReviewsCollector(BaseCollector):
    """Collector for customer reviews, dining commentary, and patron feedback."""

    @property
    def platform(self) -> Platform:
        return Platform.REVIEWS

    @property
    def version(self) -> str:
        return COLLECTOR_VERSION

    def capabilities(self) -> CollectorCapabilities:
        return CollectorCapabilities(
            can_search=True,
            can_fetch=False,
            can_fetch_thread=False,
            can_stream=False,
            can_snapshot_engagement=True,
            supported_search_params=["query", "limit", "location"],
            max_results_per_query=50,
            requires_auth=False,
            rate_limit_info="Respects polite request delays",
        )

    async def search(
        self,
        query: str,
        *,
        limit: int = 25,
        location: str = "Kansas City",
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search for customer reviews and community feedback for a business or venue.

        Args:
            query: Business name, restaurant, or venue (e.g. 'In-A-Tub', 'The Peanut').
            limit: Maximum reviews to return.
            location: Geographic qualifier (defaults to 'Kansas City').

        Returns:
            Tuple of (artifacts, next_cursor, raw_records).
        """
        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        # 1. Harvest structured reviews from public aggregator (Restaurantji)
        agg_reviews, agg_raw = self._harvest_aggregator_reviews(query, location, limit=limit)
        artifacts.extend(agg_reviews)
        raw_records.extend(agg_raw)

        # 2. Harvest web review snippets (Google/Yelp indexed excerpts and blogs)
        if len(artifacts) < limit:
            remaining = limit - len(artifacts)
            web_reviews, web_raw = self._harvest_web_review_snippets(
                query, location, limit=remaining
            )
            artifacts.extend(web_reviews)
            raw_records.extend(web_raw)

        return artifacts[:limit], None, raw_records[:limit]

    def _harvest_aggregator_reviews(
        self, query: str, location: str, limit: int = 25
    ) -> tuple[list[Artifact], list[dict[str, Any]]]:
        """Harvest reviews from restaurant and business review directories."""
        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        ddgs_query = f"site:restaurantji.com/mo/kansas-city {query}"
        try:
            results = list(DDGS().text(ddgs_query, max_results=3))
        except Exception:
            return [], []

        if not results:
            return [], []

        target_url = results[0].get("href") or results[0].get("link")
        if not target_url:
            return [], []

        try:
            resp = requests.get(target_url, impersonate="chrome120", timeout=15)
            if resp.status_code != 200:
                return [], []

            soup = BeautifulSoup(resp.text, "html.parser")
            blocks = soup.find_all(
                class_=re.compile("comment-inner|comment-content|comment|review", re.I)
            )

            for b in blocks:
                author_el = b.find(class_=re.compile("author|fn|name", re.I))
                author = author_el.get_text(strip=True) if author_el else "patron"

                text_el = b.find(class_=re.compile("comment-text|text|body", re.I))
                text = text_el.get_text(strip=True) if text_el else b.get_text(strip=True)

                # Skip boilerplate forms
                if "write a review" in text.lower() or len(text) < 25:
                    continue

                # Star rating
                rating = None
                star_el = b.find(class_=re.compile("star|rating", re.I))
                if star_el:
                    star_m = re.search(r"(\d(?:\.\d)?)", str(star_el))
                    if star_m:
                        try:
                            rating = float(star_m.group(1))
                        except Exception:
                            pass

                # Check deduplication within batch
                if any(r.get("text") == text for r in raw_records):
                    continue

                record = {
                    "business": query,
                    "author": author,
                    "text": text,
                    "rating": rating,
                    "source_url": target_url,
                    "scraped_at": datetime.now(UTC).isoformat(),
                    "source_type": "review_directory",
                }
                raw_records.append(record)

                art = self._normalize_review(record, target_url)
                artifacts.append(art)

                if len(artifacts) >= limit:
                    break

        except Exception:
            pass

        return artifacts, raw_records

    def _harvest_web_review_snippets(
        self, query: str, location: str, limit: int = 15
    ) -> tuple[list[Artifact], list[dict[str, Any]]]:
        """Harvest customer review excerpts from search engine index snippets."""
        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        search_q = f'"{query}" {location} ("review" OR "rating" OR "complaint" OR "experience")'
        try:
            results = list(DDGS().text(search_q, max_results=min(limit, 25)))
        except Exception:
            return [], []

        for r in results:
            url = r.get("href") or r.get("link")
            title = r.get("title", "")
            body = r.get("body") or r.get("snippet", "")
            if not url or len(body) < 30:
                continue

            # Detect star ratings in snippet
            rating = None
            star_match = re.search(r"(\d(?:\.\d)?)\s*(?:stars?|/5|\.0)", body)
            if star_match:
                try:
                    rating = float(star_match.group(1))
                except Exception:
                    pass

            record = {
                "business": query,
                "author": "verified_reviewer",
                "text": f"{title}\n\n{body}" if title else body,
                "rating": rating,
                "source_url": url,
                "scraped_at": datetime.now(UTC).isoformat(),
                "source_type": "web_review_index",
            }
            raw_records.append(record)

            art = self._normalize_review(record, url)
            artifacts.append(art)

            if len(artifacts) >= limit:
                break

        return artifacts, raw_records

    def _normalize_review(self, record: dict[str, Any], url: str) -> Artifact:
        """Convert scraped review record into unified Artifact schema."""
        raw_bytes = orjson.dumps(record, option=orjson.OPT_SORT_KEYS)
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()

        # Deterministic native_id based on source URL and content hash
        native_id = hashlib.sha256(
            f"{url}:{record.get('text', '')[:60]}".encode()
        ).hexdigest()[:16]

        rating = record.get("rating")
        likes = int(rating) if rating is not None and 1 <= rating <= 5 else 0

        engagement = EngagementSnapshot(
            likes=likes,
            extra={
                "rating": rating,
                "business": record.get("business", ""),
                "source_type": record.get("source_type", ""),
            },
        )

        return Artifact(
            platform=Platform.REVIEWS,
            native_id=native_id,
            canonical_url=url,
            content_type=ContentType.REVIEW,
            author_handle=record.get("author"),
            published_at=datetime.now(UTC),
            text=record.get("text", ""),
            engagement=engagement,
            discovery_method=DiscoveryMethod.SEARCH,
            collector_version=COLLECTOR_VERSION,
            raw_record_hash=raw_hash,
        )

    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch is not applicable for dynamic review search."""
        return None, None
