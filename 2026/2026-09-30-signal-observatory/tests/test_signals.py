"""Tests for the Signal Tournament engine and prospective freezing."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from observatory.config import Settings
from observatory.models import (
    Platform,
    SignalConfidence,
    SignalStatus,
)
from observatory.signals import SignalTournamentStore


@pytest.fixture
def temp_tournament(tmp_path: Path) -> SignalTournamentStore:
    settings = Settings(
        data_dir=tmp_path / "data",
        raw_dir=tmp_path / "data" / "raw",
        normalized_dir=tmp_path / "data" / "normalized",
    )
    return SignalTournamentStore(settings=settings)


class TestSignalTournament:
    """Test prospective signal freezing, verification, and scorecard calibration."""

    def test_freeze_signal_and_card(self, temp_tournament: SignalTournamentStore) -> None:
        store = temp_tournament
        signal = store.freeze_signal(
            phenomenon="Westport security scanner expansion",
            observation="Independent patrons report new metal detectors at Broadway entrance",
            hypothesis=(
                "KCPD or Westport CID will announce expanded checkpoint perimeter within 14 days"
            ),
            evidence_artifact_ids=["art_reddit_001", "art_tiktok_002"],
            creator_count=2,
            platforms=[Platform.REDDIT, Platform.TIKTOK],
            confidence=SignalConfidence.HIGH,
            verification_days=14,
        )

        assert signal.signal_id == "SIGNAL-2026-0001"
        assert signal.status == SignalStatus.PENDING
        assert signal.confidence == SignalConfidence.HIGH
        assert len(signal.freeze_hash) == 64
        assert signal.creator_count == 2
        assert Platform.REDDIT in signal.platforms
        assert Platform.TIKTOK in signal.platforms

        # Verify Markdown card was created
        card_file = store.cards_dir / f"{signal.signal_id}.md"
        assert card_file.exists()
        card_text = card_file.read_text(encoding="utf-8")
        assert "Westport security scanner expansion" in card_text
        assert signal.freeze_hash in card_text

        # Verify next ID sequential generation
        next_id = store.get_next_signal_id(2026)
        assert next_id == "SIGNAL-2026-0002"

    def test_resolve_signal_outcome(self, temp_tournament: SignalTournamentStore) -> None:
        store = temp_tournament
        sig = store.freeze_signal(
            phenomenon="Taco establishment closure rumor",
            observation="Patrons note locked doors on Tuesday during lunch hours",
            hypothesis="Formal closure announcement within 14 days",
            evidence_artifact_ids=["art_rev_101"],
            confidence=SignalConfidence.MODERATE,
        )

        # Attempt invalid resolution to PENDING
        with pytest.raises(ValueError, match="Cannot resolve a signal to PENDING"):
            store.resolve_signal(sig.signal_id, SignalStatus.PENDING, "still waiting")

        # Resolve to HIT
        resolved = store.resolve_signal(
            signal_id=sig.signal_id,
            status=SignalStatus.HIT,
            notes="Official KC Star article confirms permanent closure.",
            verifying_artifact_ids=["art_web_star_202"],
        )

        assert resolved.status == SignalStatus.HIT
        assert resolved.resolved_at is not None
        assert resolved.resolution_notes == "Official KC Star article confirms permanent closure."
        assert resolved.verifying_artifact_ids == ["art_web_star_202"]

        # Check persistence
        fetched = store.get_signal(sig.signal_id)
        assert fetched is not None
        assert fetched.status == SignalStatus.HIT
        assert fetched.verifying_artifact_ids == ["art_web_star_202"]

    def test_scorecard_and_brier_calibration(
        self, temp_tournament: SignalTournamentStore
    ) -> None:
        store = temp_tournament

        # Freeze 3 signals with different confidences
        s1 = store.freeze_signal(
            phenomenon="Event A",
            observation="Obs A",
            hypothesis="Hyp A",
            evidence_artifact_ids=["art_a"],
            confidence=SignalConfidence.HIGH,
        )
        s2 = store.freeze_signal(
            phenomenon="Event B",
            observation="Obs B",
            hypothesis="Hyp B",
            evidence_artifact_ids=["art_b"],
            confidence=SignalConfidence.MODERATE,
        )
        s3 = store.freeze_signal(
            phenomenon="Event C",
            observation="Obs C",
            hypothesis="Hyp C",
            evidence_artifact_ids=["art_c"],
            confidence=SignalConfidence.LOW,
        )
        store.freeze_signal(
            phenomenon="Event D (Pending)",
            observation="Obs D",
            hypothesis="Hyp D",
            evidence_artifact_ids=["art_d"],
            confidence=SignalConfidence.HIGH,
        )

        # Resolve s1 as HIT, s2 as PARTIAL, s3 as MISS, s4 left PENDING
        # Mock older frozen_at for s1 to test lead time
        s1.frozen_at = datetime.now(UTC) - timedelta(hours=48)
        store._append_or_update_parquet(s1)

        store.resolve_signal(s1.signal_id, SignalStatus.HIT, "Confirmed")
        store.resolve_signal(s2.signal_id, SignalStatus.PARTIAL, "Partially confirmed")
        store.resolve_signal(s3.signal_id, SignalStatus.MISS, "Did not occur")

        sc = store.scorecard()
        assert sc["total_frozen"] == 4
        assert sc["pending"] == 1
        assert sc["evaluated"] == 3
        assert sc["hits"] == 1
        assert sc["partials"] == 1
        assert sc["misses"] == 1

        # Hit rate = (1 + 0.5 * 1) / 3 = 1.5 / 3 = 0.5
        assert sc["hit_rate"] == 0.5
        assert sc["brier_score"] is not None
        assert sc["mean_lead_time_hours"] is not None
        assert sc["mean_lead_time_hours"] >= 47.0

        # Confidence breakdown check
        assert sc["confidence_breakdown"]["high"]["evaluated"] == 1
        assert sc["confidence_breakdown"]["high"]["hits"] == 1
        assert sc["confidence_breakdown"]["moderate"]["partials"] == 1
        assert sc["confidence_breakdown"]["low"]["misses"] == 1
