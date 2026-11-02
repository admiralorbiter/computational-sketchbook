"""Tests for media formatting, downloading, and CitizenFootageCollector."""

from datetime import UTC, datetime

from observatory.collectors.footage import CitizenFootageCollector
from observatory.media import format_media_filename, slugify
from observatory.models import Platform


def test_slugify() -> None:
    assert slugify("Hello World!") == "hello-world"
    assert slugify("#DodgeCity #Kansas Protests!") == "dodgecity-kansas-protests"
    assert slugify("") == "untitled"


def test_format_media_filename() -> None:
    filename = format_media_filename(
        platform="tiktok",
        author="@sikestreasures",
        title="Today's protest in Dodge City Ks. Ice...",
        date=datetime(2026, 9, 24, tzinfo=UTC),
        native_id="7688552651616734478",
        ext="mp4",
    )
    assert filename.startswith("2026-09-24_tiktok_sikestreasures_todays-protest-in-dodge-city-ks")
    assert filename.endswith(".mp4")
    assert "651616734478" in filename


def test_citizen_footage_collector_capabilities() -> None:
    collector = CitizenFootageCollector()
    caps = collector.capabilities()
    assert caps.can_search is True
    assert caps.can_fetch is True
    assert caps.requires_auth is False
    assert collector.platform == Platform.CITIZEN
