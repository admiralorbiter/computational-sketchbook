"""Unit tests for Auditor engine and review packet generation."""

from nsb.auditor.engine import Auditor, AuditReport
from nsb.auditor.packet import generate_review_packet


def test_auditor_check():
    auditor = Auditor()
    report = auditor.audit(require_clean_git=False)
    assert isinstance(report, AuditReport)
    assert report.verdict in ("PASS", "FIX", "ESCALATE")
    assert len(report.checks) > 0


def test_review_packet_with_audit_report(tmp_path):
    auditor = Auditor()
    report = auditor.audit(require_clean_git=False)

    pkt_path = generate_review_packet(
        contract_id="TEST-001",
        audit_report=report,
        benchmark_version="v001_smoke",
        wave_name="TEST_WAVE",
        track_results=[],
        proposals=[],
        attestation_commit="c0ffee1234",
        output_dir=str(tmp_path),
    )

    assert pkt_path.exists()
    content = pkt_path.read_text(encoding="utf-8")
    assert f"**Evaluated Commit**: `{report.git_sha}`" in content
    assert "**Attestation Commit**: `c0ffee1234`" in content
    assert report.verdict in content
