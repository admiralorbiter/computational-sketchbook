"""Curate Canonical Observatory Parquet & CSV Datasets from Authored YAML.

Loads the authored canonical YAML definitions from `data/observatory/`:
    - claims.yaml
    - scenarios.yaml
    - indicators.yaml
    - observations.yaml

Enforces strict foreign-key integrity against the repository evidence claims ledger:
    - Every evidence_claim_id must exist in evidence_claims.parquet, power_claims.parquet,
      task025 jupiter claims, or observatory_claims.parquet.
    - Every indicator_id in observations must exist in indicators.yaml.
    - Bitemporal ordering: source_event_date <= first_publicly_observable_date <= ingestion_date.

Compiles into analytical representations in `data/processed/`:
    - observatory_claims.parquet / .csv
    - observatory_scenarios.parquet / .csv
    - observatory_indicators.parquet / .csv
    - observatory_observations.parquet / .csv
"""

from pathlib import Path
from typing import Set
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
OBSERVATORY_AUTHORED_DIR = REPO_ROOT / "data" / "observatory"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"


def validate_authored_claims(claims_yaml_path: Path) -> Set[str]:
    """Validates authored claims against epistemic verification rules before admitting them.

    A newly authored claim does NOT certify itself by presence alone.
    To be admitted into the verified evidence ledger, each authored claim MUST:
        1. Possess non-empty fields: claim_id, entity_id, source_type, filing_date,
           document_url, section_locator, quote_type, exact_quote, verified_by,
           verification_status, and verifier_notes.
        2. Explicitly classify quote_type in {'exact_quote', 'source_excerpt', 'analyst_summary'}.
        3. Possess verification_status in {'VERIFIED', 'VERIFIED_AUDITED'}.
        4. Anchor to a confirmed tracked entity with local filings in data/raw/sec/ or network registry.
        5. For 'exact_quote', verify contiguous verbatim substring against local cached document if present.
        6. For 'source_excerpt' or 'analyst_summary', require substantive verifier_notes documenting
           cross-references to SEC filings, exhibits, or regulatory orders.
    """
    if not claims_yaml_path.exists():
        return set()

    with open(claims_yaml_path, "r", encoding="utf-8") as f:
        authored_claims = yaml.safe_load(f) or []

    verified_ids = set()
    raw_sec_dir = REPO_ROOT / "data" / "raw" / "sec"
    valid_known_entities = {"WULF", "CORZ", "IREN", "ORCL", "OBDC", "APLD", "CRWV", "SMCI", "NVDA", "MSFT", "MDU"}

    for idx, c in enumerate(authored_claims):
        cid = c.get("claim_id")
        if not cid:
            raise ValueError(f"Authored claim at index {idx} missing 'claim_id'")

        # 1. Required fields
        required_fields = [
            "entity_id", "source_type", "filing_date", "document_url",
            "section_locator", "quote_type", "exact_quote", "verified_by",
            "verification_status", "verifier_notes"
        ]
        missing = [rf for rf in required_fields if not c.get(rf)]
        if missing:
            raise ValueError(f"Authored claim {cid} missing required verification fields: {missing}")

        # 2. Explicit quote classification
        q_type = str(c["quote_type"]).strip()
        if q_type not in {"exact_quote", "source_excerpt", "analyst_summary"}:
            raise ValueError(
                f"Authored claim {cid} has invalid quote_type '{q_type}'. "
                f"Must be one of: exact_quote, source_excerpt, analyst_summary"
            )

        # 3. Verification status
        v_status = str(c["verification_status"]).strip()
        if v_status not in {"VERIFIED", "VERIFIED_AUDITED"}:
            raise ValueError(f"Authored claim {cid} has unverified status: '{v_status}'")

        # 4. Entity provenance check
        ent_id = str(c["entity_id"]).strip()
        matching_sec = list(raw_sec_dir.glob(f"{ent_id}_submissions_*.json"))
        if not matching_sec and ent_id not in valid_known_entities:
            raise ValueError(f"Authored claim {cid} references unconfirmed entity: '{ent_id}'")

        # 5. For exact_quote with local source file, check substring
        if q_type == "exact_quote":
            quote_text = str(c["exact_quote"]).strip()
            doc_url = str(c["document_url"])
            doc_fname = Path(doc_url).name
            local_cand = raw_sec_dir / doc_fname
            if local_cand.exists():
                with open(local_cand, "r", encoding="utf-8", errors="ignore") as f_src:
                    src_content = f_src.read()
                if quote_text not in src_content:
                    raise ValueError(f"Authored claim {cid} exact_quote not found in local file {doc_fname}")

        # 6. For source_excerpt / analyst_summary, check verifier_notes length
        if q_type in {"source_excerpt", "analyst_summary"}:
            notes = str(c["verifier_notes"]).strip()
            if len(notes) < 20:
                raise ValueError(f"Authored claim {cid} ({q_type}) requires substantive verifier_notes (got: '{notes}')")

        verified_ids.add(cid)

    return verified_ids


def collect_verified_evidence_claim_ids() -> Set[str]:
    """Gathers all verified claim IDs across the repository's immutable ledgers."""
    verified_ids = set()

    # 1. Core evidence claims
    core_claims_file = PROCESSED_DIR / "evidence_claims.parquet"
    if core_claims_file.exists():
        df_core = pd.read_parquet(core_claims_file)
        if "claim_id" in df_core.columns:
            verified_ids.update(df_core["claim_id"].dropna().tolist())

    # 2. Power claims
    power_claims_file = PROCESSED_DIR / "power_claims.parquet"
    if power_claims_file.exists():
        df_pwr = pd.read_parquet(power_claims_file)
        if "claim_id" in df_pwr.columns:
            verified_ids.update(df_pwr["claim_id"].dropna().tolist())

    # 3. Task 025 Jupiter pre-event and post-event claims
    task025_dir = PROCESSED_DIR / "task025"
    if task025_dir.exists():
        for p in task025_dir.glob("*claims*.parquet"):
            df_t = pd.read_parquet(p)
            if "claim_id" in df_t.columns:
                verified_ids.update(df_t["claim_id"].dropna().tolist())
        for p in task025_dir.glob("*postevent*.parquet"):
            df_t = pd.read_parquet(p)
            if "claim_id" in df_t.columns:
                verified_ids.update(df_t["claim_id"].dropna().tolist())

    # 4. Authored observatory claims (validated independently)
    claims_yaml_path = OBSERVATORY_AUTHORED_DIR / "claims.yaml"
    if claims_yaml_path.exists():
        authored_verified = validate_authored_claims(claims_yaml_path)
        verified_ids.update(authored_verified)

    return verified_ids


def compile_observatory_datasets():
    """Validates authored YAML files and compiles canonical Parquet and CSV tables."""
    assert OBSERVATORY_AUTHORED_DIR.exists(), f"Authored directory missing: {OBSERVATORY_AUTHORED_DIR}"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    verified_claims = collect_verified_evidence_claim_ids()
    print(f"Loaded {len(verified_claims)} verified evidence claim IDs from repository ledgers.")

    # 1. Compile Claims
    claims_yaml_path = OBSERVATORY_AUTHORED_DIR / "claims.yaml"
    with open(claims_yaml_path, "r", encoding="utf-8") as f:
        claims_data = yaml.safe_load(f) or []
    df_claims = pd.DataFrame(claims_data)
    df_claims.to_parquet(PROCESSED_DIR / "observatory_claims.parquet", index=False)
    df_claims.to_csv(PROCESSED_DIR / "observatory_claims.csv", index=False)
    print(f"Compiled {len(df_claims)} claims to observatory_claims.parquet")

    # 2. Compile Scenarios
    scenarios_yaml_path = OBSERVATORY_AUTHORED_DIR / "scenarios.yaml"
    with open(scenarios_yaml_path, "r", encoding="utf-8") as f:
        scenarios_data = yaml.safe_load(f) or []

    for scn in scenarios_data:
        claim_refs = [c.strip() for c in str(scn.get("evidence_claim_ids", "")).split(",") if c.strip()]
        for cid in claim_refs:
            if cid not in verified_claims:
                raise ValueError(f"Foreign-key violation in scenario {scn.get('scenario_id')}: claim '{cid}' not found in evidence ledger.")

    df_scenarios = pd.DataFrame(scenarios_data)
    df_scenarios.to_parquet(PROCESSED_DIR / "observatory_scenarios.parquet", index=False)
    df_scenarios.to_csv(PROCESSED_DIR / "observatory_scenarios.csv", index=False)
    print(f"Compiled {len(df_scenarios)} scenarios to observatory_scenarios.parquet")

    # 3. Compile Indicators
    indicators_yaml_path = OBSERVATORY_AUTHORED_DIR / "indicators.yaml"
    with open(indicators_yaml_path, "r", encoding="utf-8") as f:
        indicators_data = yaml.safe_load(f) or []

    indicator_ids = set()
    for ind in indicators_data:
        iid = ind.get("indicator_id")
        indicator_ids.add(iid)
        claim_refs = [c.strip() for c in str(ind.get("evidence_claim_ids", "")).split(",") if c.strip()]
        for cid in claim_refs:
            if cid not in verified_claims:
                raise ValueError(f"Foreign-key violation in indicator {iid}: claim '{cid}' not found in evidence ledger.")

    df_indicators = pd.DataFrame(indicators_data)
    df_indicators.to_parquet(PROCESSED_DIR / "observatory_indicators.parquet", index=False)
    df_indicators.to_csv(PROCESSED_DIR / "observatory_indicators.csv", index=False)
    print(f"Compiled {len(df_indicators)} indicators to observatory_indicators.parquet")

    # 4. Compile Observations
    observations_yaml_path = OBSERVATORY_AUTHORED_DIR / "observations.yaml"
    with open(observations_yaml_path, "r", encoding="utf-8") as f:
        observations_data = yaml.safe_load(f) or []

    for obs in observations_data:
        oid = obs.get("observation_id")
        target_ind = obs.get("indicator_id")
        if target_ind not in indicator_ids:
            raise ValueError(f"Foreign-key violation in observation {oid}: indicator '{target_ind}' not found in indicators catalog.")

        cid = obs.get("evidence_claim_id")
        if cid and cid not in verified_claims:
            raise ValueError(f"Foreign-key violation in observation {oid}: claim '{cid}' not found in evidence ledger.")

        src_date = str(obs.get("source_event_date"))
        pub_date = str(obs.get("first_publicly_observable_date"))
        ing_date = str(obs.get("ingestion_date"))
        if src_date > pub_date:
            raise ValueError(f"Bitemporal inversion in observation {oid}: source_event_date ({src_date}) > first_publicly_observable_date ({pub_date})")
        if pub_date > ing_date:
            raise ValueError(f"Ingestion lookahead in observation {oid}: first_publicly_observable_date ({pub_date}) > ingestion_date ({ing_date})")

    df_observations = pd.DataFrame(observations_data)
    df_observations.to_parquet(PROCESSED_DIR / "observatory_observations.parquet", index=False)
    df_observations.to_csv(PROCESSED_DIR / "observatory_observations.csv", index=False)
    print(f"Compiled {len(df_observations)} observations to observatory_observations.parquet")


if __name__ == "__main__":
    compile_observatory_datasets()
