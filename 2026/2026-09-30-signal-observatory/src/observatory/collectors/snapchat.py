"""Snapchat Spotlight and public story collector.

Discovers, extracts, and normalizes public Snapchat Spotlight videos,
creator stories, and local geographic snaps without requiring API keys or mobile credentials.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any

import requests
from ddgs import DDGS

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Platform,
)

COLLECTOR_VERSION = "snapchat-collector-0.1.0"


class SnapchatCollector(BaseCollector):
    """Collector for public Snapchat Spotlight videos and creator stories."""

    def __init__(self, request_delay_seconds: float = 1.0) -> None:
        super().__init__()
        self.request_delay_seconds = request_delay_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    @property
    def platform(self) -> Platform:
        return Platform.SNAPCHAT

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
        )

    def _extract_page_props(self, html_text: str) -> dict[str, Any] | None:
        """Extract Next.js props JSON from a Snapchat HTML page."""
        match = re.search(r'<script[^>]*>(\{"props":\{.*?)</script>', html_text, re.DOTALL)
        if not match:
            match = re.search(
                r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.DOTALL
            )
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("props", {}).get("pageProps", {})
            except Exception:
                return None
        return None

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
        """Search for Snapchat Spotlight videos matching a query.

        Args:
            query: Topic or location to search (e.g. 'Kansas City', 'Westport', 'rave').
            limit: Maximum items to collect.
            since: Lower time bound.
            until: Upper time bound.
            cursor: Pagination cursor.
            **kwargs: Extra arguments.

        Returns:
            Tuple of (artifacts, next_cursor, raw_records).
        """
        raw_records: list[dict[str, Any]] = []
        artifacts: list[Artifact] = []
        discovered_urls: list[str] = []

        search_queries = [
            f"site:snapchat.com/spotlight {query}",
            f'site:snapchat.com/spotlight "{query}"',
            f"site:snapchat.com {query} spotlight",
            f'site:snapchat.com "{query}"',
        ]

        try:
            ddgs = DDGS()
            for sq in search_queries:
                if len(discovered_urls) >= limit:
                    break
                try:
                    results = list(ddgs.text(sq, max_results=limit))
                    for r in results:
                        href = r.get("href") or ""
                        if "snapchat.com" in href and href not in discovered_urls:
                            discovered_urls.append(href)
                            raw_records.append(r)
                except Exception:
                    continue
        except Exception:
            pass

        for url in discovered_urls[:limit]:
            art, raw = await self.fetch(url)
            if art:
                artifacts.append(art)
                if raw:
                    raw_records.append(raw)

        return artifacts, None, raw_records

    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch and normalize a single Snapchat Spotlight video by URL or ID.

        Args:
            native_id: Full snapchat.com URL or spotlight snap ID.

        Returns:
            Tuple of (Artifact, raw_data_dict) or (None, None).
        """
        url = (
            native_id
            if native_id.startswith("http")
            else f"https://www.snapchat.com/spotlight/{native_id}"
        )
        snap_id = native_id.split("/")[-1].split("?")[0]

        try:
            resp = self.session.get(url, timeout=12)
            if resp.status_code != 200:
                return None, None

            page_props = self._extract_page_props(resp.text)
            raw_record: dict[str, Any] = {
                "url": url,
                "native_id": snap_id,
                "fetched_at": datetime.now(UTC).isoformat(),
                "page_props": page_props or {},
            }

            title = ""
            description = ""
            author_handle = "citizen"
            likes = 0
            views = 0
            shares = 0
            replies = 0
            published_dt: datetime | None = None
            media_urls: list[str] = []

            if page_props:
                # Video metadata block
                vmeta = page_props.get("videoMetadata") or {}
                if isinstance(vmeta, dict):
                    title = vmeta.get("name") or ""
                    description = vmeta.get("description") or ""
                    creator = vmeta.get("creator", {}).get("personCreator", {})
                    if creator:
                        user_val = creator.get("username") or creator.get("name")
                        author_handle = user_val or author_handle
                    upload_ms = vmeta.get("uploadDateMs")
                    if upload_ms:
                        try:
                            published_dt = datetime.fromtimestamp(int(upload_ms) / 1000, tz=UTC)
                        except Exception:
                            pass
                    if vmeta.get("contentUrl"):
                        media_urls.append(vmeta["contentUrl"])

                # Spotlight stories feed block
                spotlight_stories = page_props.get("spotlightFeed", {}).get("spotlightStories", [])
                if spotlight_stories:
                    st = spotlight_stories[0]
                    smeta = st.get("metadata", {})
                    eng = smeta.get("engagementStats", {})
                    if eng:
                        views = int(eng.get("viewCount") or 0)
                        shares = int(eng.get("shareCount") or 0)
                        replies = int(eng.get("commentCount") or 0)
                        likes = int(eng.get("boostCount") or eng.get("recommendCount") or 0)

                    story_obj = st.get("story", {})
                    snaps = story_obj.get("snapList", [])
                    if snaps:
                        snap_item = snaps[0]
                        sec = snap_item.get("timestampInSec", {}).get("value")
                        if sec and not published_dt:
                            try:
                                published_dt = datetime.fromtimestamp(int(sec), tz=UTC)
                            except Exception:
                                pass
                        surls = snap_item.get("snapUrls", {})
                        if surls.get("mediaUrl") and surls["mediaUrl"] not in media_urls:
                            media_urls.append(surls["mediaUrl"])

                    # Context and tags
                    llm_desc = smeta.get("llmDescription") or ""
                    hashtags = " ".join(smeta.get("hashtags") or [])
                    keywords = ", ".join(smeta.get("textMetadataKeywords") or [])

                    full_text = "\n\n".join(
                        part
                        for part in [
                            title,
                            description,
                            f"Hashtags: {hashtags}" if hashtags else "",
                            f"AI Content Description: {llm_desc}" if llm_desc else "",
                            f"Keywords: {keywords}" if keywords else "",
                        ]
                        if part
                    ).strip()
                else:
                    full_text = f"{title}\n\n{description}".strip()

            else:
                # Fallback: extract title from HTML
                title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE)
                if title_match:
                    full_text = title_match.group(1).strip()
                else:
                    full_text = f"Snapchat Video {snap_id}"

            eng_snapshot = EngagementSnapshot(
                likes=likes,
                reposts=shares,
                replies=replies,
                views=views if views > 0 else None,
            )

            raw_bytes = json.dumps(raw_record, sort_keys=True).encode("utf-8")
            raw_hash = hashlib.sha256(raw_bytes).hexdigest()

            artifact = Artifact(
                platform=Platform.SNAPCHAT,
                native_id=snap_id,
                canonical_url=url,
                content_type=ContentType.VIDEO,
                author_handle=author_handle,
                published_at=published_dt or datetime.now(UTC),
                text=full_text or f"Snapchat video by @{author_handle}",
                media_refs=media_urls,
                discovery_method=DiscoveryMethod.SEARCH,
                collector_version=self.version,
                raw_record_hash=raw_hash,
                engagement=eng_snapshot,
            )

            return artifact, raw_record

        except Exception:
            return None, None
