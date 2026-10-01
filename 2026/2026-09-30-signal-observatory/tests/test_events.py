"""Tests for Living Event Ledger."""

from pathlib import Path

from observatory.events import EventLedger, EventMilestone


def test_event_lifecycle(tmp_path: Path):
    ledger = EventLedger(storage_dir=tmp_path)

    # 1. Create event
    ev = ledger.create_event(
        event_id="2026-test-crisis",
        title="Test Event Crisis",
        category="civil_action",
        location="Kansas City",
        summary="A test event timeline.",
        date_start="2026-09-01",
    )
    assert ev.id == "2026-test-crisis"
    assert ev.title == "Test Event Crisis"

    # 2. Add milestones
    m1 = EventMilestone(
        timestamp="2026-09-01 10:00",
        headline="Initial Rumors on TikTok",
        description="Videos begin surfacing from downtown.",
        author="citizen1",
        platform="tiktok",
        media_path="C:/videos/test.mp4",
        artifact_id="art123",
    )
    ev.add_milestone(m1)

    m2 = EventMilestone(
        timestamp="2026-09-02 14:00",
        headline="Official Statement",
        description="Authorities issue a response.",
        author="kcpd",
        platform="web",
        source_url="https://example.com/press",
    )
    ev.add_milestone(m2)
    ledger.save_event(ev)

    # 3. Reload from ledger
    reloaded = ledger.get_event("2026-test-crisis")
    assert reloaded is not None
    assert len(reloaded.milestones) == 2
    assert reloaded.milestones[0].headline == "Initial Rumors on TikTok"
    assert "C:/videos/test.mp4" in reloaded.media_files
    assert "art123" in reloaded.artifact_ids

    # 4. Generate markdown timeline
    md = ledger.generate_timeline_markdown("2026-test-crisis")
    assert "# Event History: Test Event Crisis" in md
    assert "Initial Rumors on TikTok" in md
    assert "Official Statement" in md
