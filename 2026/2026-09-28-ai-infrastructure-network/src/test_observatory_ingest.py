"""Unit tests for Observatory Ingestion Runner and Adapters."""

from datetime import date
import os
from pathlib import Path
import tempfile
import pytest
import yaml

from observatory_schema import ClockType, SignalRole, Observability, LeadTimeStatus
import observatory_ingest as ing


def test_candidate_observation_roundtrip():
    """Verify CandidateObservation serialization and deserialization."""
    cand = ing.CandidateObservation(
        candidate_id="CAN-TEST123456",
        adapter_name="EDGAR",
        source_event_date=date(2026, 8, 25),
        first_publicly_observable_date=date(2026, 8, 28),
        ingestion_date=date(2026, 9, 30),
        headline_text="Test filing announcement",
        raw_source_uri="https://www.sec.gov/test",
        project_id="IREN_MACKENZIE",
        indicator_id="IND-MAC-002",
        clock_affected=ClockType.FINANCIAL,
        threatened_boundary="Facility commitment cliff",
        signal_role=SignalRole.FINANCIAL_RECOGNITION,
        observability=Observability.PUBLIC,
        lead_time_status=LeadTimeStatus.MONITORING_WINDOW,
        evidence_claim_id="CLM-IREN-001",
        raw_payload_snippet="Form: 10-K | Item 1.01",
        classification_status="CLASSIFIED",
        review_notes="Auto-classified by EDGARAdapter",
    )
    d = cand.to_dict()
    assert d["candidate_id"] == "CAN-TEST123456"
    assert d["clock_affected"] == "FINANCIAL"
    assert d["signal_role"] == "FINANCIAL_RECOGNITION"

    restored = ing.CandidateObservation.from_dict(d)
    assert restored.candidate_id == cand.candidate_id
    assert restored.clock_affected == ClockType.FINANCIAL
    assert restored.signal_role == SignalRole.FINANCIAL_RECOGNITION
    assert restored.source_event_date == date(2026, 8, 25)


def test_candidate_id_determinism():
    """Verify candidate ID hashing is deterministic and reproducible."""
    id1 = ing.generate_candidate_id("EDGAR", "https://sec.gov/test1", date(2026, 8, 25), "Filing Headline")
    id2 = ing.generate_candidate_id("EDGAR", "https://sec.gov/test1", date(2026, 8, 25), "Filing Headline")
    id3 = ing.generate_candidate_id("EDGAR", "https://sec.gov/test2", date(2026, 8, 25), "Filing Headline")

    assert id1.startswith("CAN-")
    assert id1 == id2
    assert id1 != id3


def test_all_adapters_discovery():
    """Verify that all 4 intake adapters discover candidates."""
    edgar_adp = ing.EDGARAdapter()
    cands_edgar = edgar_adp.discover_candidates(target_tickers=["IREN", "WULF"])
    assert len(cands_edgar) > 0
    assert any(c.project_id == "IREN_MACKENZIE" for c in cands_edgar)
    assert any(c.project_id == "TERAWULF_LAKE_MARINER" for c in cands_edgar)

    ir_adp = ing.CorporateIRAdapter()
    cands_ir = ir_adp.discover_candidates()
    assert len(cands_ir) >= 2
    assert any(c.project_id == "TERAWULF_LAKE_MARINER" for c in cands_ir)

    reg_adp = ing.RegulatoryAdapter()
    cands_reg = reg_adp.discover_candidates()
    assert len(cands_reg) >= 2
    assert any(c.project_id == "PROJECT_JUPITER" for c in cands_reg)

    comm_adp = ing.ManualCommercialDataAdapter()
    cands_comm = comm_adp.discover_candidates()
    assert len(cands_comm) >= 1
    assert cands_comm[0].project_id == "PROJECT_JUPITER"
    assert cands_comm[0].observability == Observability.COMMERCIAL_DATA


def test_candidate_store_deduplication():
    """Verify CandidateStore prevents duplicate candidate insertions."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_pq = Path(tmp_dir) / "test_candidates.parquet"
        tmp_csv = Path(tmp_dir) / "test_candidates.csv"
        store = ing.CandidateStore(parquet_path=tmp_pq, csv_path=tmp_csv)

        cand = ing.CandidateObservation(
            candidate_id="CAN-DEDUP-001",
            adapter_name="EDGAR",
            source_event_date=date(2026, 8, 25),
            first_publicly_observable_date=date(2026, 8, 28),
            ingestion_date=date(2026, 9, 30),
            headline_text="Duplicate test",
            raw_source_uri="https://www.sec.gov/test_dup",
        )

        assert store.add_candidate(cand) is True
        assert store.add_candidate(cand) is False  # Duplicate insertion rejected
        store.save_candidates()

        # Reload from disk
        store2 = ing.CandidateStore(parquet_path=tmp_pq, csv_path=tmp_csv)
        assert len(store2.candidates) == 1
        assert "CAN-DEDUP-001" in store2.candidates


def test_candidate_store_promotion_foreign_key_guard():
    """Verify that promoting a candidate with an unverified claim ID raises ValueError."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_pq = Path(tmp_dir) / "test_candidates.parquet"
        tmp_csv = Path(tmp_dir) / "test_candidates.csv"
        tmp_obs = Path(tmp_dir) / "test_observations.yaml"
        with open(tmp_obs, "w", encoding="utf-8") as f:
            yaml.dump([], f)

        store = ing.CandidateStore(parquet_path=tmp_pq, csv_path=tmp_csv, authored_obs_yaml=tmp_obs)
        cand = ing.CandidateObservation(
            candidate_id="CAN-PROMOTE-001",
            adapter_name="EDGAR",
            source_event_date=date(2026, 8, 25),
            first_publicly_observable_date=date(2026, 8, 28),
            ingestion_date=date(2026, 9, 30),
            headline_text="Promotion test",
            raw_source_uri="https://www.sec.gov/test_promote",
            project_id="IREN_MACKENZIE",
            indicator_id="IND-MAC-002",
        )
        store.add_candidate(cand)

        with pytest.raises(ValueError, match="not found in verified evidence ledger"):
            store.promote_to_canonical(
                candidate_id="CAN-PROMOTE-001",
                evidence_claim_id="CLM-FAKE-CLAIM-9999",
            )
