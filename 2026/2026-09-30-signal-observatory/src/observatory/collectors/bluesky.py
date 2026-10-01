"""Bluesky collector using the AT Protocol public AppView.

Bluesky is the observatory's primary collection platform because:
- Full public search with no authentication required
- Rich search syntax (from:, lang:, since:/until:, #hashtag)
- 3,000 requests per 5-minute window
- Complete post hydration with engagement counts
- Jetstream WebSocket for real-time streaming

All reads go through public.api.bsky.app which requires no credentials.
"""

import hashlib
from datetime import datetime
from typing import Any

import httpx
import orjson
from tenacity import retry, stop_after_attempt, wait_exponential

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Platform,
)

BSKY_PUBLIC_API = "https://public.api.bsky.app"
COLLECTOR_VERSION = "bluesky-collector-0.1.0"


class BlueskyCollector(BaseCollector):
    """Collector for Bluesky via the AT Protocol public AppView."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        from observatory.config import get_settings

        settings = get_settings()
        self._client = client or httpx.AsyncClient(
            base_url=BSKY_PUBLIC_API,
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "User-Agent": settings.user_agent,
            },
        )
        self._owns_client = client is None

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_client:
            await self._client.aclose()

    @property
    def platform(self) -> Platform:
        return Platform.BLUESKY

    @property
    def version(self) -> str:
        return COLLECTOR_VERSION

    def capabilities(self) -> CollectorCapabilities:
        return CollectorCapabilities(
            can_search=True,
            can_fetch=True,
            can_fetch_thread=True,
            can_stream=True,
            can_snapshot_engagement=True,
            supported_search_params=[
                "query",
                "limit",
                "since",
                "until",
                "cursor",
                "sort",
                "lang",
                "from",
                "domain",
                "hashtag",
            ],
            max_results_per_query=100,
            requires_auth=False,
            rate_limit_info="3,000 requests per 5-minute sliding window per IP",
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def search(
        self,
        query: str,
        *,
        limit: int = 50,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        sort: str = "latest",
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search Bluesky posts.

        Args:
            query: Search query. Supports Bluesky search syntax:
                   from:<handle>, lang:<code>, since:<ISO>, until:<ISO>, #hashtag
            limit: Max results (1-100).
            since: ISO-8601 lower time bound (also embeddable in query).
            until: ISO-8601 upper time bound (also embeddable in query).
            cursor: Pagination cursor from previous response.
            sort: "latest" or "top".

        Returns:
            Tuple of (artifacts, next_cursor, raw_records).
        """
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, 100),
            "sort": sort,
        }
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if cursor:
            params["cursor"] = cursor

        response = await self._client.get(
            "/xrpc/app.bsky.feed.searchPosts",
            params=params,
        )
        response.raise_for_status()

        data = response.json()
        raw_records = data.get("posts", [])
        next_cursor = data.get("cursor")

        artifacts = [self._normalize_post(post) for post in raw_records]

        return artifacts, next_cursor, raw_records

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch a single Bluesky post by its AT URI.

        Args:
            native_id: AT Protocol URI (at://did:plc:.../app.bsky.feed.post/...).

        Returns:
            Tuple of (artifact, raw_record) or (None, None).
        """
        # Use getPostThread to fetch a single post with context
        params: dict[str, str | int] = {"uri": native_id, "depth": 0, "parentHeight": 0}

        response = await self._client.get(
            "/xrpc/app.bsky.feed.getPostThread",
            params=params,
        )

        if response.status_code == 404:
            return None, None

        response.raise_for_status()
        data = response.json()

        thread = data.get("thread", {})
        post_data = thread.get("post")
        if not post_data:
            return None, None

        return self._normalize_post(post_data), post_data

    async def fetch_thread(self, native_id: str) -> tuple[list[Artifact], list[dict[str, Any]]]:
        """Fetch a full thread from a Bluesky post.

        Args:
            native_id: AT Protocol URI of the root or any post in the thread.

        Returns:
            Tuple of (artifacts, raw_records) for all posts in the thread.
        """
        params: dict[str, str | int] = {"uri": native_id, "depth": 6, "parentHeight": 6}

        response = await self._client.get(
            "/xrpc/app.bsky.feed.getPostThread",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        self._walk_thread(data.get("thread", {}), artifacts, raw_records)
        return artifacts, raw_records

    def _walk_thread(
        self,
        node: dict[str, Any],
        artifacts: list[Artifact],
        raw_records: list[dict[str, Any]],
    ) -> None:
        """Recursively walk a thread tree, collecting posts."""
        if node.get("$type") == "app.bsky.feed.defs#blockedPost":
            return
        if node.get("$type") == "app.bsky.feed.defs#notFoundPost":
            return

        post_data = node.get("post")
        if post_data:
            artifacts.append(self._normalize_post(post_data))
            raw_records.append(post_data)

        # Walk parent chain
        parent = node.get("parent")
        if parent and isinstance(parent, dict):
            self._walk_thread(parent, artifacts, raw_records)

        # Walk replies
        for reply in node.get("replies", []):
            if isinstance(reply, dict):
                self._walk_thread(reply, artifacts, raw_records)

    def _normalize_post(self, post_data: dict[str, Any]) -> Artifact:
        """Convert a Bluesky post view into a normalized Artifact."""
        author = post_data.get("author", {})
        record = post_data.get("record", {})

        # Build AT URI if not present
        uri = post_data.get("uri", "")

        # Extract engagement metrics
        engagement = EngagementSnapshot(
            likes=post_data.get("likeCount", 0),
            reposts=post_data.get("repostCount", 0),
            replies=post_data.get("replyCount", 0),
            extra={
                "quoteCount": post_data.get("quoteCount", 0),
            },
        )

        # Parse timestamps
        published_at = None
        created_at_str = record.get("createdAt")
        if created_at_str:
            try:
                published_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Build canonical URL
        handle = author.get("handle", "")
        rkey = uri.split("/")[-1] if uri else ""
        canonical_url = (
            f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else None
        )

        # Detect thread parent
        reply_ref = record.get("reply", {})
        thread_parent = None
        if reply_ref:
            parent_ref = reply_ref.get("parent", {})
            thread_parent = parent_ref.get("uri")

        # Extract media references
        media_refs: list[str] = []
        embed = post_data.get("embed", {})
        if embed:
            # Images
            for img in embed.get("images", []):
                if thumb := img.get("thumb"):
                    media_refs.append(thumb)
                elif fullsize := img.get("fullsize"):
                    media_refs.append(fullsize)

        # Hash the raw record for provenance
        raw_bytes = orjson.dumps(post_data, option=orjson.OPT_SORT_KEYS)
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()

        # Detect language
        langs = record.get("langs", [])
        language = langs[0] if langs else None

        return Artifact(
            platform=Platform.BLUESKY,
            native_id=uri,
            canonical_url=canonical_url,
            content_type=ContentType.POST,
            author_handle=handle,
            author_platform_id=author.get("did", ""),
            published_at=published_at,
            language=language,
            text=record.get("text"),
            media_refs=media_refs,
            thread_parent=thread_parent,
            engagement=engagement,
            discovery_method=DiscoveryMethod.SEARCH,
            collector_version=COLLECTOR_VERSION,
            raw_record_hash=raw_hash,
        )
