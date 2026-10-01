from observatory.collectors.snapchat import SnapchatCollector
from observatory.models import Platform


def test_snapchat_collector_capabilities():
    collector = SnapchatCollector()
    assert collector.platform == Platform.SNAPCHAT
    caps = collector.capabilities()
    assert caps.can_search is True
    assert caps.can_fetch is True
    assert caps.can_snapshot_engagement is True


def test_extract_page_props():
    collector = SnapchatCollector()
    sample_html = """
    <html>
      <head>
        <script id="__NEXT_DATA__" type="application/json">
          {"props": {"pageProps": {"videoMetadata": {"name": "Test Snap"}}}}
        </script>
      </head>
    </html>
    """
    props = collector._extract_page_props(sample_html)
    assert props is not None
    assert props.get("videoMetadata", {}).get("name") == "Test Snap"


def test_snapchat_fetch_offline_fallback():
    import asyncio

    collector = SnapchatCollector()
    # Invalid URL returns None, None without crashing
    art, raw = asyncio.run(
        collector.fetch("https://www.snapchat.com/spotlight/invalid_nonexistent_id_12345")
    )
    assert art is None
    assert raw is None
