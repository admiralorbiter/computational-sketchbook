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

    # 4. Authored observatory claims
    claims_yaml_path = OBSERVATORY_AUTHORED_DIR / "claims.yaml"
    if claims_yaml_path.exists():
        with open(claims_yaml_path, "r", encoding="utf-8") as f:
            authored_claims = yaml.safe_load(f) or []
        for c in authored_claims:
            if "claim_id" in c:
                verified_ids.add(c["claim_id"])

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
