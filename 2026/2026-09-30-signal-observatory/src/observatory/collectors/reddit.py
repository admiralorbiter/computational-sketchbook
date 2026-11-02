"""Reddit collector using direct web scraping.

No API keys or OAuth required. This collector scrapes old.reddit.com
which provides more parseable HTML than the modern Reddit interface.

Uses httpx for HTTP requests and BeautifulSoup for HTML parsing.
Respects rate limiting through self-imposed delays.

Note: Reddit may block aggressive scraping. This collector uses
polite request delays and a descriptive user-agent.
"""

import asyncio
import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import httpx
import orjson
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.config import get_settings
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Platform,
)

COLLECTOR_VERSION = "reddit-collector-0.1.0"
OLD_REDDIT_BASE = "https://old.reddit.com"


class RedditCollector(BaseCollector):
    """Collector for Reddit via old.reddit.com web scraping.

    Scrapes the old Reddit interface which renders server-side HTML
    that is straightforward to parse. No API key or OAuth required.
    """

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        request_delay: float | None = None,
    ) -> None:
        settings = get_settings()
        delay = settings.request_delay_seconds
        self._request_delay = request_delay if request_delay is not None else delay
        self._client = client or httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
        )
        self._owns_client = client is None

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_client:
            await self._client.aclose()

    @property
    def platform(self) -> Platform:
        return Platform.REDDIT

    @property
    def version(self) -> str:
        return COLLECTOR_VERSION

    def capabilities(self) -> CollectorCapabilities:
        return CollectorCapabilities(
            can_search=True,
            can_fetch=True,
            can_fetch_thread=True,
            can_stream=False,
            can_snapshot_engagement=True,
            supported_search_params=[
                "query",
                "limit",
                "sort",
                "time_filter",
                "subreddit",
            ],
            max_results_per_query=25,
            requires_auth=False,
            rate_limit_info="Self-throttled; ~1 request/second to be respectful",
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=3, max=60),
        reraise=True,
    )
    async def search(
        self,
        query: str,
        *,
        limit: int = 25,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        subreddit: str | None = None,
        sort: str = "relevance",
        time_filter: str = "all",
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search Reddit for posts matching a query.

        Scrapes old.reddit.com search results page.

        Args:
            query: Search query string.
            limit: Maximum results (capped at 25 per page on old Reddit).
            since: Not directly supported; use time_filter instead.
            until: Not directly supported; use time_filter instead.
            cursor: 'after' token for pagination (Reddit fullname, e.g. t3_abc123).
            subreddit: Optional subreddit to search within (without r/ prefix).
            sort: Sort order: relevance, hot, top, new, comments.
            time_filter: Time filter: hour, day, week, month, year, all.

        Returns:
            Tuple of (artifacts, next_cursor, raw_records).
        """
        params: dict[str, str] = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": str(min(limit, 25)),
        }
        if cursor:
            params["after"] = cursor

        if subreddit:
            sub = subreddit.removeprefix("r/")
            url = f"{OLD_REDDIT_BASE}/r/{sub}/search?{urlencode(params)}&restrict_sr=on"
        else:
            url = f"{OLD_REDDIT_BASE}/search?{urlencode(params)}"

        response = await self._client.get(url)
        response.raise_for_status()

        await asyncio.sleep(self._request_delay)

        soup = BeautifulSoup(response.text, "html.parser")

        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        # Parse search result entries
        things = soup.find_all("div", class_="thing", attrs={"data-fullname": True})

        for thing in things:
            if not isinstance(thing, Tag):
                continue
            record = self._extract_thing_data(thing)
            if record:
                raw_records.append(record)
                artifacts.append(self._normalize_post(record))

        # Find next page cursor
        next_cursor = None
        next_button = soup.find("span", class_="next-button")
        if next_button and isinstance(next_button, Tag):
            next_link = next_button.find("a")
            if next_link and isinstance(next_link, Tag):
                href = next_link.get("href", "")
                if isinstance(href, str) and "after=" in href:
                    next_cursor = href.split("after=")[1].split("&")[0]

        # Fallback to search index (DuckDuckGo) if direct old.reddit
        # returned an unauthenticated splash wall
        if not artifacts:
            try:
                from datetime import UTC

                from ddgs import DDGS

                sub_filter = (
                    f"site:reddit.com/r/{subreddit.removeprefix('r/')}"
                    if subreddit
                    else "site:reddit.com"
                )
                ddgs_query = f"{sub_filter} {query}"
                ddgs = DDGS()
                results = list(ddgs.text(ddgs_query, max_results=min(limit, 25)))
                for r in results:
                    href = r.get("href") or r.get("link")
                    title = r.get("title", "")
                    body = r.get("body") or r.get("snippet", "")
                    if not href or "reddit.com" not in href:
                        continue

                    # Extract post ID and subreddit
                    sub = subreddit or "all"
                    post_id = href
                    if "/r/" in href:
                        parts = href.split("/r/")[1].split("/")
                        if len(parts) > 0:
                            sub = parts[0]
                        if len(parts) > 2 and parts[1] == "comments":
                            post_id = parts[2]

                    record = {
                        "fullname": f"t3_{post_id}" if not post_id.startswith("http") else post_id,
                        "title": title,
                        "url": href,
                        "permalink": href,
                        "subreddit": sub,
                        "author": "reddit_community",
                        "score": 0,
                        "num_comments": 0,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "domain": "reddit.com",
                        "selftext": body,
                        "discovery_source": "ddgs_reddit_fallback",
                    }
                    raw_records.append(record)
                    artifacts.append(self._normalize_post(record))
            except Exception:
                pass

        return artifacts, next_cursor, raw_records

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=3, max=60),
        reraise=True,
    )
    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch a single Reddit post by its URL or fullname.

        Args:
            native_id: Reddit post URL or fullname (e.g. t3_abc123).

        Returns:
            Tuple of (artifact, raw_record) or (None, None).
        """
        if native_id.startswith("http"):
            url = native_id
            if "old.reddit.com" not in url:
                url = url.replace("www.reddit.com", "old.reddit.com")
                url = url.replace("reddit.com", "old.reddit.com")
        else:
            # Assume it's a fullname like t3_abc123, construct a search
            url = f"{OLD_REDDIT_BASE}/by_id/{native_id}"

        response = await self._client.get(url)
        if response.status_code == 404:
            return None, None
        response.raise_for_status()

        await asyncio.sleep(self._request_delay)

        soup = BeautifulSoup(response.text, "html.parser")
        thing = soup.find("div", class_="thing", attrs={"data-fullname": True})

        if not thing or not isinstance(thing, Tag):
            return None, None

        record = self._extract_thing_data(thing)
        if not record:
            return None, None

        # Try to get the selftext/body from the post page
        expando = soup.find("div", class_="expando")
        if expando and isinstance(expando, Tag):
            usertext = expando.find("div", class_="usertext-body")
            if usertext and isinstance(usertext, Tag):
                record["selftext"] = usertext.get_text(strip=True)

        return self._normalize_post(record), record

    async def fetch_thread(self, native_id: str) -> tuple[list[Artifact], list[dict[str, Any]]]:
        """Fetch a Reddit post and its comments.

        Args:
            native_id: Reddit post URL.

        Returns:
            Tuple of (artifacts, raw_records) for the post and top comments.
        """
        if native_id.startswith("http"):
            url = native_id
            if "old.reddit.com" not in url:
                url = url.replace("www.reddit.com", "old.reddit.com")
                url = url.replace("reddit.com", "old.reddit.com")
        else:
            url = f"{OLD_REDDIT_BASE}/by_id/{native_id}"

        response = await self._client.get(url)
        response.raise_for_status()

        await asyncio.sleep(self._request_delay)

        soup = BeautifulSoup(response.text, "html.parser")

        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        # Get the main post
        post_thing = soup.find("div", class_="thing", attrs={"data-fullname": True})
        if post_thing and isinstance(post_thing, Tag):
            post_record = self._extract_thing_data(post_thing)
            if post_record:
                # Get selftext
                expando = soup.find("div", class_="expando")
                if expando and isinstance(expando, Tag):
                    usertext = expando.find("div", class_="usertext-body")
                    if usertext and isinstance(usertext, Tag):
                        post_record["selftext"] = usertext.get_text(strip=True)

                raw_records.append(post_record)
                artifacts.append(self._normalize_post(post_record))

                # Get comments
                comment_area = soup.find("div", class_="commentarea")
                if comment_area and isinstance(comment_area, Tag):
                    comments = comment_area.find_all(
                        "div", class_="thing", attrs={"data-fullname": True}
                    )
                    for comment in comments[:50]:  # Cap at 50 comments
                        if not isinstance(comment, Tag):
                            continue
                        comment_record = self._extract_comment_data(
                            comment, parent_fullname=post_record.get("fullname", "")
                        )
                        if comment_record:
                            raw_records.append(comment_record)
                            artifacts.append(self._normalize_comment(comment_record))

        return artifacts, raw_records

    def _extract_thing_data(self, thing: Tag) -> dict[str, Any] | None:
        """Extract structured data from an old.reddit.com 'thing' div.

        Old Reddit embeds most metadata as data-* attributes on the
        containing div, making it relatively easy to parse.
        """
        fullname = thing.get("data-fullname", "")
        if not fullname:
            return None

        # Extract title
        title_elem = thing.find("a", class_="title")
        title = ""
        if title_elem and isinstance(title_elem, Tag):
            title = title_elem.get_text(strip=True)

        # Extract URL
        url = ""
        if title_elem and isinstance(title_elem, Tag):
            href = title_elem.get("href", "")
            if isinstance(href, str):
                url = href if href.startswith("http") else f"{OLD_REDDIT_BASE}{href}"

        # Extract metadata from data attributes
        subreddit = str(thing.get("data-subreddit", ""))
        author = str(thing.get("data-author", ""))
        score = thing.get("data-score", "0")
        comments_count = thing.get("data-comments-count", "0")

        # Extract timestamp
        time_elem = thing.find("time")
        timestamp = None
        if time_elem and isinstance(time_elem, Tag):
            dt = time_elem.get("datetime", "")
            if isinstance(dt, str) and dt:
                timestamp = dt

        # Extract domain/link flair
        domain_elem = thing.find("span", class_="domain")
        domain = domain_elem.get_text(strip=True).strip("()") if domain_elem else ""

        post_id = str(fullname).replace("t3_", "")
        return {
            "fullname": str(fullname),
            "title": title,
            "url": url,
            "permalink": f"{OLD_REDDIT_BASE}/r/{subreddit}/comments/{post_id}/",
            "subreddit": subreddit,
            "author": author,
            "score": int(score) if str(score).lstrip("-").isdigit() else 0,
            "num_comments": int(comments_count) if str(comments_count).isdigit() else 0,
            "timestamp": timestamp,
            "domain": domain,
            "selftext": "",
        }

    def _extract_comment_data(
        self, comment: Tag, parent_fullname: str = ""
    ) -> dict[str, Any] | None:
        """Extract data from a comment div."""
        fullname = comment.get("data-fullname", "")
        if not fullname:
            return None

        author = str(comment.get("data-author", "[deleted]"))

        # Get comment body
        body_elem = comment.find("div", class_="usertext-body")
        body = body_elem.get_text(strip=True) if body_elem and isinstance(body_elem, Tag) else ""

        # Get score
        score_elem = comment.find("span", class_="score")
        score_text = score_elem.get_text(strip=True) if score_elem else "0"
        # Parse "42 points" format
        score = 0
        if score_text:
            parts = score_text.split()
            if parts and parts[0].lstrip("-").isdigit():
                score = int(parts[0])

        # Get timestamp
        time_elem = comment.find("time")
        timestamp = None
        if time_elem and isinstance(time_elem, Tag):
            dt = time_elem.get("datetime", "")
            if isinstance(dt, str) and dt:
                timestamp = dt

        return {
            "fullname": str(fullname),
            "author": author,
            "body": body,
            "score": score,
            "timestamp": timestamp,
            "parent_fullname": parent_fullname,
        }

    def _normalize_post(self, record: dict[str, Any]) -> Artifact:
        """Convert scraped Reddit post data into a normalized Artifact."""
        fullname = record.get("fullname", "")

        # Combine title and selftext
        title = record.get("title", "")
        selftext = record.get("selftext", "")
        text_parts = [title]
        if selftext:
            text_parts.append(selftext)
        text = "\n\n".join(text_parts)

        engagement = EngagementSnapshot(
            likes=record.get("score", 0),
            replies=record.get("num_comments", 0),
            extra={
                "subreddit": record.get("subreddit", ""),
                "domain": record.get("domain", ""),
            },
        )

        published_at = None
        ts = record.get("timestamp")
        if ts:
            try:
                published_at = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, TypeError, AttributeError):
                pass

        raw_bytes = orjson.dumps(record, option=orjson.OPT_SORT_KEYS)
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()

        permalink = record.get("permalink", "")

        return Artifact(
            platform=Platform.REDDIT,
            native_id=fullname,
            canonical_url=permalink,
            content_type=ContentType.POST,
            author_handle=record.get("author"),
            published_at=published_at,
            text=text,
            engagement=engagement,
            discovery_method=DiscoveryMethod.SEARCH,
            collector_version=COLLECTOR_VERSION,
            raw_record_hash=raw_hash,
        )

    def _normalize_comment(self, record: dict[str, Any]) -> Artifact:
        """Convert scraped Reddit comment data into a normalized Artifact."""
        fullname = record.get("fullname", "")

        engagement = EngagementSnapshot(
            likes=record.get("score", 0),
        )

        published_at = None
        ts = record.get("timestamp")
        if ts:
            try:
                published_at = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, TypeError, AttributeError):
                pass

        raw_bytes = orjson.dumps(record, option=orjson.OPT_SORT_KEYS)
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()

        return Artifact(
            platform=Platform.REDDIT,
            native_id=fullname,
            content_type=ContentType.COMMENT,
            author_handle=record.get("author"),
            published_at=published_at,
            text=record.get("body", ""),
            thread_parent=record.get("parent_fullname"),
            engagement=engagement,
            discovery_method=DiscoveryMethod.THREAD_EXPANSION,
            collector_version=COLLECTOR_VERSION,
            raw_record_hash=raw_hash,
        )
