"""Web and community forum collector using open search and trafilatura.

No API keys required. Enables the observatory to:
1. Search across open web sources, local blogs, Reddit threads, and community forums.
2. Extract full-text content, author metadata, and publication timestamps using trafilatura.
3. Normalize articles and discussion threads into the unified Artifact model.
"""

import hashlib
from datetime import datetime
from typing import Any

import orjson
import trafilatura
from ddgs import DDGS

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    Platform,
)

COLLECTOR_VERSION = "web-collector-0.1.0"


class WebCollector(BaseCollector):
    """Collector for open web articles, neighborhood blogs, and forum discussions."""

    @property
    def platform(self) -> Platform:
        return Platform.WEB

    @property
    def version(self) -> str:
        return COLLECTOR_VERSION

    def capabilities(self) -> CollectorCapabilities:
        return CollectorCapabilities(
            can_search=True,
            can_fetch=True,
            can_fetch_thread=False,
            can_stream=False,
            can_snapshot_engagement=False,
            supported_search_params=["query", "limit", "region"],
            max_results_per_query=25,
            requires_auth=False,
            rate_limit_info="Polite search query delays (no official quota)",
        )

    async def search(
        self,
        query: str,
        *,
        limit: int = 15,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search the web for community discussions, local reporting, and forum posts.

        Args:
            query: Search query string (e.g. 'site:reddit.com/r/kansascity dollar store').
            limit: Maximum search results to retrieve and extract.

        Returns:
            Tuple of (normalized Artifacts, next_cursor, raw search result dicts).
        """
        raw_results: list[dict[str, Any]] = []
        artifacts: list[Artifact] = []

        try:
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=min(limit, 25)))
        except Exception:
            return [], None, []

        for r in results:
            url = r.get("href") or r.get("link")
            title = r.get("title", "")
            snippet = r.get("body") or r.get("snippet", "")
            if not url:
                continue

            raw_results.append(r)

            # Determine platform type from URL
            platform_type = Platform.WEB
            if "reddit.com" in url:
                platform_type = Platform.REDDIT

            # Extract full text using trafilatura
            full_text = snippet
            author = None
            date_published = None

            try:
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    extracted = trafilatura.extract(
                        downloaded,
                        include_comments=True,
                        include_tables=True,
                        output_format="txt",
                    )
                    metadata = trafilatura.extract_metadata(downloaded)
                    if extracted and len(extracted) > len(snippet):
                        full_text = f"{title}\n\n{extracted}"
                    if metadata:
                        author = metadata.author
                        if metadata.date:
                            try:
                                date_published = datetime.fromisoformat(metadata.date)
                            except Exception:
                                pass
            except Exception:
                pass

            raw_bytes = orjson.dumps(r, option=orjson.OPT_SORT_KEYS)
            raw_hash = hashlib.sha256(raw_bytes).hexdigest()
            clean_native_id = url.split("?")[0].rstrip("/")

            c_type = ContentType.ARTICLE if platform_type == Platform.WEB else ContentType.THREAD
            artifact = Artifact(
                platform=platform_type,
                native_id=clean_native_id,
                canonical_url=url,
                content_type=c_type,
                author_handle=author or "web_source",
                published_at=date_published,
                text=full_text,
                discovery_method=DiscoveryMethod.SEARCH,
                collector_version=COLLECTOR_VERSION,
                raw_record_hash=raw_hash,
            )
            artifacts.append(artifact)

        return artifacts, None, raw_results

    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch and extract an article or forum thread from a direct URL.

        Args:
            native_id: Full web URL.

        Returns:
            Tuple of (normalized Artifact, raw metadata dict).
        """
        url = native_id
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None, None

            extracted = trafilatura.extract(
                downloaded,
                include_comments=True,
                include_tables=True,
                output_format="txt",
            )
            metadata = trafilatura.extract_metadata(downloaded)

            title = metadata.title if metadata and metadata.title else url
            author = metadata.author if metadata and metadata.author else "web_source"
            date_published = None
            if metadata and metadata.date:
                try:
                    date_published = datetime.fromisoformat(metadata.date)
                except Exception:
                    pass

            text = f"{title}\n\n{extracted}" if extracted else title
            raw_record = {
                "url": url,
                "title": title,
                "author": author,
                "date": str(date_published),
                "text_length": len(text),
            }

            raw_bytes = orjson.dumps(raw_record, option=orjson.OPT_SORT_KEYS)
            raw_hash = hashlib.sha256(raw_bytes).hexdigest()

            platform_type = Platform.REDDIT if "reddit.com" in url else Platform.WEB

            artifact = Artifact(
                platform=platform_type,
                native_id=url.split("?")[0].rstrip("/"),
                canonical_url=url,
                content_type=ContentType.ARTICLE,
                author_handle=author,
                published_at=date_published,
                text=text,
                discovery_method=DiscoveryMethod.MANUAL,
                collector_version=COLLECTOR_VERSION,
                raw_record_hash=raw_hash,
            )
            return artifact, raw_record
        except Exception:
            return None, None
