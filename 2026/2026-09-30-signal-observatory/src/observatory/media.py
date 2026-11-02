"""Media handling, download engine, and descriptive file naming.

Supports YouTube, TikTok, Facebook public videos, and web footage using yt-dlp.
No API keys required.
"""

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from observatory.config import get_settings


def slugify(text: str, max_length: int = 40) -> str:
    """Convert arbitrary text into a clean filesystem-safe slug."""
    if not text:
        return "untitled"
    # Replace hashtag symbols and common punctuation
    s = re.sub(r"[#@\$\%&\*\+/:;=\?@\[\]\\^`\{\}\|~]", " ", text)
    # Replace non-alphanumerics with hyphens
    s = re.sub(r"[^a-zA-Z0-9\s_-]", "", s).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s)
    s = s.strip("-")
    if not s:
        return "untitled"
    return s[:max_length].rstrip("-")


def format_media_filename(
    platform: str,
    author: str | None,
    title: str | None,
    date: datetime | str | None,
    native_id: str,
    ext: str = "mp4",
) -> str:
    """Generate a clean, descriptive media filename with date, platform, author, and title.

    Example output:
        2026-09-24_tiktok_sikestreasures_todays-protest-in-dodge-city-ks_7688552651.mp4
        2026-09-24_facebook_alexander-hernandez_dodge-city-protesting-against-ice_2189391615.mp4
    """
    # 1. Format date (YYYY-MM-DD)
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d")
    elif isinstance(date, str) and len(date) >= 8:
        # Could be YYYYMMDD or ISO format
        cleaned_date = date.replace("-", "")[:8]
        if cleaned_date.isdigit() and len(cleaned_date) == 8:
            date_str = f"{cleaned_date[:4]}-{cleaned_date[4:6]}-{cleaned_date[6:8]}"
        else:
            date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    else:
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")

    # 2. Format author slug
    author_slug = slugify(author or "citizen", max_length=20)

    # 3. Format title / caption slug
    title_slug = slugify(title or "raw-footage", max_length=45)

    # 4. Clean native ID (last 10-12 chars for uniqueness)
    clean_id = re.sub(r"[^a-zA-Z0-9_-]", "", native_id)[-12:] or "vid"

    clean_platform = slugify(platform, max_length=12)

    return f"{date_str}_{clean_platform}_{author_slug}_{title_slug}_{clean_id}.{ext}"


def download_media_footage(
    url: str,
    output_dir: Path | str | None = None,
    max_height: int = 720,
    preferred_name: str | None = None,
    timeout: int = 180,
) -> tuple[Path | None, dict[str, Any]]:
    """Download video footage to disk using yt-dlp with descriptive naming.

    Args:
        url: Video URL (YouTube, TikTok, Facebook, etc.).
        output_dir: Destination folder. Defaults to configured settings.media_dir.
        max_height: Maximum resolution height (default: 720).
        preferred_name: Custom filename (without extension). If None, auto-generated.
        timeout: Subprocess timeout in seconds.

    Returns:
        Tuple of (downloaded Path or None, metadata dict).
    """
    settings = get_settings()
    dest_dir = Path(output_dir) if output_dir else settings.media_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Probe metadata first to generate descriptive name
    meta_cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    metadata: dict[str, Any] = {}
    try:
        res = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0 and res.stdout.strip():
            metadata = json.loads(res.stdout.strip().split("\n")[0])
    except Exception:
        pass

    extractor = metadata.get("extractor", "").lower()
    platform = "video"
    if "tiktok" in extractor or "tiktok" in url:
        platform = "tiktok"
    elif "facebook" in extractor or "facebook" in url:
        platform = "facebook"
    elif "youtube" in extractor or "youtube" in url:
        platform = "youtube"

    author = metadata.get("uploader") or metadata.get("channel") or metadata.get("uploader_id")
    title = metadata.get("title") or metadata.get("description", "")
    date_val = metadata.get("upload_date")
    native_id = str(metadata.get("id") or url.split("/")[-1].split("?")[0])

    if preferred_name:
        filename = (
            f"{preferred_name}.mp4" if not preferred_name.endswith(".mp4") else preferred_name
        )
    else:
        filename = format_media_filename(
            platform=platform,
            author=author,
            title=title,
            date=date_val,
            native_id=native_id,
            ext="mp4",
        )

    target_file = dest_dir / filename
    if target_file.exists():
        return target_file, metadata

    out_template = str(dest_dir / f"{filename[:-4]}.%(ext)s")

    download_cmd = [
        "yt-dlp",
        "-f",
        f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best",
        "--merge-output-format",
        "mp4",
        "-o",
        out_template,
        "--no-playlist",
        url,
    ]

    try:
        dl_res = subprocess.run(download_cmd, capture_output=True, text=True, timeout=timeout)
        if target_file.exists():
            return target_file, metadata
        # In case extension differed
        base_name = filename[:-4]
        matches = list(dest_dir.glob(f"{base_name}.*"))
        if matches:
            return matches[0], metadata
        if dl_res.returncode != 0:
            return None, metadata
        return None, metadata
    except Exception:
        return None, metadata
