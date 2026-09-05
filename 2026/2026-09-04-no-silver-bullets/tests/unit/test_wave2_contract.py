"""Tests for Wave 2 Preregistration Contract and 150-modulus corpus generation."""

from pathlib import Path
import yaml

from nsb.benchmarks.corpus import (
    generate_wave2_confirmatory_corpus,
    load_public_instances,
    load_sealed_truth,
    TRIPWIRE_FILENAME,
)


def test_wave2_contract_file_exists_and_valid():
    contract_path = Path("config/contracts/r2_wave2_criteria.yaml")
    assert contract_path.is_file(), "Criteria contract file must exist"
    with open(contract_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["contract_id"] == "NSB-R2-WAVE2-B-CONFIRMATORY"
    assert data["criteria_tier"].startswith("frozen_preregistration")
    assert "claim_hierarchy" in data
    assert "replication_claim" in data["claim_hierarchy"]
    assert "search_claim" in data["claim_hierarchy"]
    assert ("sota_claim" in data["claim_hierarchy"] or "in_house_polyselect_proxy" in data["claim_hierarchy"])
    assert ("scaling_claim" in data["claim_hierarchy"] or "scaling_persistence" in data["claim_hierarchy"])

    # Also verify preserved v2.0 criteria exists for provenance audit
    v2_0_path = Path("config/contracts/r2_wave2_criteria_v2.0.yaml")
    assert v2_0_path.is_file(), "v2.0 criteria must be preserved"


def test_wave2_preregistration_doc_exists():
    doc_path = Path("docs/preregistrations/NSB-R2-WAVE2-B-CONFIRMATORY.md")
    assert doc_path.is_file(), "Preregistration markdown doc must exist"
    content = doc_path.read_text(encoding="utf-8")
    assert "NSB-R2-WAVE2-B-CONFIRMATORY" in content

    # Verify v2.1 amendment doc exists
    doc_v21_path = Path("docs/preregistrations/NSB-R2-WAVE2-B-CONFIRMATORY_v2.1.md")
    assert doc_v21_path.is_file(), "Amendment v2.1 markdown doc must exist"
    content_v21 = doc_v21_path.read_text(encoding="utf-8")
    assert "Amendment 1" in content_v21
    assert "pairwise" in content_v21.lower()


def test_wave2_corpus_generation_and_balance(tmp_path):
    manifest = generate_wave2_confirmatory_corpus(tmp_path)
    assert manifest["total_instances"] == 150
    assert manifest["benchmark_version"] == "v002_wave2"
    assert manifest["split"] == "confirmatory"
    assert manifest["master_seed"] == 20260904

    instances = load_public_instances(tmp_path, "v002_wave2", "confirmatory")
    assert len(instances) == 150

    from collections import Counter
    counts = Counter(i.bits for i in instances)
    assert counts[32] == 30
    assert counts[48] == 30
    assert counts[64] == 30
    assert counts[80] == 30
    assert counts[96] == 30

    # Verify tripwire canary in sealed directory
    sealed_dir = tmp_path / "benchmarks" / "sealed" / "v002_wave2" / "confirmatory"
    tripwire = sealed_dir / TRIPWIRE_FILENAME
    assert tripwire.is_file()

    # Verify sealed truth
    truth = load_sealed_truth(tmp_path, "v002_wave2", "confirmatory")
    assert len(truth) == 150
    for inst in instances:
        assert inst.instance_id in truth
        p = int(truth[inst.instance_id].p)
        q = int(truth[inst.instance_id].q)
        N = int(inst.N)
        assert p * q == N
        assert p < q
