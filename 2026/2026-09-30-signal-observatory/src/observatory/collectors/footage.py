"""Citizen and on-the-ground video footage collector.

Zero API keys required. Uncovers raw phone footage, citizen livestreams,
and eyewitness recordings across TikTok, Facebook public videos,
and independent YouTube uploads.
"""

import hashlib
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import orjson
from ddgs import DDGS

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.config import get_settings
from observatory.media import download_media_footage
from observatory.models import (
    Artifact,
    ContentType,
    DiscoveryMethod,
    EngagementSnapshot,
    Platform,
)

COLLECTOR_VERSION = "citizen-footage-0.1.0"


class CitizenFootageCollector(BaseCollector):
    """Collector for raw citizen phone video, eyewitness clips, and social livestreams."""

    @property
    def platform(self) -> Platform:
        return Platform.CITIZEN

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
            supported_search_params=["query", "limit", "download", "output_dir"],
            max_results_per_query=30,
            requires_auth=False,
            rate_limit_info="Respects polite upstream search delays",
        )

    async def search(
        self,
        query: str,
        *,
        limit: int = 15,
        download: bool = False,
        output_dir: Path | str | None = None,
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search for citizen on-the-ground video footage across TikTok, Facebook, and YouTube.

        Args:
            query: Search terms (e.g. 'Dodge City ICE protest', 'redadas Kansas').
            limit: Maximum video artifacts to return.
            download: Whether to immediately download raw MP4 files to disk.
            output_dir: Directory where footage will be saved (defaults to settings.media_dir).

        Returns:
            Tuple of (artifacts, next_cursor, raw_records).
        """
        urls: list[str] = []
        ddgs = DDGS()

        # 1. Surface TikTok citizen video URLs
        try:
            tiktok_q = f"site:tiktok.com {query}"
            t_res = list(ddgs.text(tiktok_q, max_results=max(limit // 2, 5)))
            for r in t_res:
                href = r.get("href") or r.get("link") or ""
                if "uddg=" in href:
                    href = unquote(href.split("uddg=")[1].split("&")[0])
                if "/video/" in href and href not in urls:
                    urls.append(href)
        except Exception:
            pass

        # 2. Surface Facebook public videos
        try:
            fb_q = f"site:facebook.com {query} video"
            fb_res = list(ddgs.text(fb_q, max_results=max(limit // 2, 5)))
            for r in fb_res:
                href = r.get("href") or r.get("link") or ""
                if "uddg=" in href:
                    href = unquote(href.split("uddg=")[1].split("&")[0])
                if ("/videos/" in href or "/watch/" in href) and href not in urls:
                    urls.append(href)
        except Exception:
            pass

        # 3. Surface independent YouTube clips (filtering out major news corporations)
        try:
            yt_q = f"site:youtube.com/watch {query} -KSN -KMBC -KAKE -News -TV"
            yt_res = list(ddgs.text(yt_q, max_results=max(limit // 3, 4)))
            for r in yt_res:
                href = r.get("href") or r.get("link") or ""
                if "uddg=" in href:
                    href = unquote(href.split("uddg=")[1].split("&")[0])
                if "watch?v=" in href and href not in urls:
                    urls.append(href)
        except Exception:
            pass

        artifacts: list[Artifact] = []
        raw_records: list[dict[str, Any]] = []

        for video_url in urls[:limit]:
            artifact, raw = await self.fetch(
                video_url, download=download, output_dir=output_dir
            )
            if artifact:
                artifacts.append(artifact)
                if raw:
                    raw_records.append(raw)

        return artifacts, None, raw_records

    async def fetch(
        self,
        url_or_id: str,
        *,
        download: bool = False,
        output_dir: Path | str | None = None,
    ) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch metadata and optionally download raw footage for a video URL."""
        # Probe metadata using yt-dlp
        meta_cmd = ["yt-dlp", "--dump-json", "--no-download", url_or_id]
        try:
            res = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=30)
            if res.returncode != 0 or not res.stdout.strip():
                return None, None
            data = orjson.loads(res.stdout.strip().split("\n")[0])
        except Exception:
            return None, None

        extractor = data.get("extractor", "").lower()
        if "tiktok" in extractor or "tiktok" in url_or_id:
            platform = Platform.TIKTOK
        elif "facebook" in extractor or "facebook" in url_or_id:
            platform = Platform.FACEBOOK
        else:
            platform = Platform.YOUTUBE

        video_id = str(data.get("id") or url_or_id.split("/")[-1].split("?")[0])
        title = data.get("title", "")
        description = data.get("description", "")
        author = data.get("uploader") or data.get("channel") or data.get("uploader_id") or "citizen"

        text_content = f"{title}\n\n{description}".strip() if description else title

        # Parse upload date (YYYYMMDD)
        upload_date = None
        ud = data.get("upload_date")
        if ud and len(ud) == 8 and ud.isdigit():
            try:
                upload_date = datetime.strptime(ud, "%Y%m%d").replace(tzinfo=UTC)
            except Exception:
                pass
        if not upload_date:
            upload_date = datetime.now(UTC)

        media_refs: list[str] = []
        local_path_str = None

        # Download raw footage if requested
        if download:
            target_dir = output_dir or get_settings().media_dir
            local_path, _ = download_media_footage(
                url_or_id, output_dir=target_dir, max_height=720
            )
            if local_path and local_path.exists():
                local_path_str = str(local_path)
                media_refs.append(local_path_str)

        engagement = EngagementSnapshot(
            likes=data.get("like_count") or 0,
            views=data.get("view_count"),
            replies=data.get("comment_count") or 0,
            reposts=data.get("repost_count") or 0,
            extra={
                "duration": data.get("duration"),
                "uploader": author,
                "local_file": local_path_str,
            },
        )

        raw_bytes = orjson.dumps(data, option=orjson.OPT_SORT_KEYS)
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()

        artifact = Artifact(
            platform=platform,
            native_id=video_id,
            canonical_url=data.get("webpage_url", url_or_id),
            content_type=ContentType.FOOTAGE,
            author_handle=author,
            author_platform_id=data.get("channel_id") or data.get("uploader_id", ""),
            published_at=upload_date,
            text=text_content,
            media_refs=media_refs,
            engagement=engagement,
            discovery_method=DiscoveryMethod.SEARCH,
            collector_version=COLLECTOR_VERSION,
            raw_record_hash=raw_hash,
        )

        return artifact, data
