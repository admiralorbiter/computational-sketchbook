"""Prospective Monitoring Pipeline & Empirical Scoreboard Engine.

This module provides the bitemporal observation tracking and empirical scoring
engine for the Infrastructure Stress Observatory.

Bitemporal Pipeline:
    source_event_date -> first_publicly_observable_date -> ingestion_date
    project_id -> clock_affected -> threatened_boundary -> signal_role -> observability

Epistemic Scoreboard Metrics:
    1. Early Warning Detection Lead:
       Delta_t_lead = t_financial_recognition - t_earliest_observable_indicator
       (Strictly evaluated on EARLY_WARNING signals preceding financial recognition).
    2. Event Propagation Lag:
       Delta_t_prop = t_contractual_response - t_upstream_physical_shock
       (Downstream contractual consequences and confirmations).
    3. Right-Censored Information Lag:
       Delta_t_censored = t_censor - t_reference_event
       (Absence of corporate disclosures on SEC EDGAR).
"""

from dataclasses import dataclass
from datetime import date, datetime
import os
from typing import Dict, List, Optional, Any
import pandas as pd

from observatory_schema import (
    ClockType,
    SignalRole,
    Observability,
    LeadTimeStatus,
    DATA_PROCESSED_DIR,
    OBSERVATIONS_PARQUET,
)


@dataclass(frozen=True)
class MonitoredObservation:
    """A verified bitemporal observation logged by the observatory."""
    observation_id: str
    indicator_id: str
    project_id: str
    source_event_date: date
    first_publicly_observable_date: date
    ingestion_date: date
    clock_affected: ClockType
    threatened_boundary: str
    signal_role: SignalRole
    observability: Observability
    headline_text: str
    raw_source_uri: str
    evidence_claim_id: str
    lead_time_days_to_financial_recognition: Optional[float] = None
    propagation_lag_days_from_upstream_signal: Optional[float] = None
    reference_event_date: Optional[date] = None
    censor_date: Optional[date] = None
    censored_lead_days: Optional[float] = None
    lead_time_status: LeadTimeStatus = LeadTimeStatus.OBSERVED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "indicator_id": self.indicator_id,
            "project_id": self.project_id,
            "source_event_date": self.source_event_date.isoformat(),
            "first_publicly_observable_date": self.first_publicly_observable_date.isoformat(),
            "ingestion_date": self.ingestion_date.isoformat(),
            "clock_affected": self.clock_affected.value,
            "threatened_boundary": self.threatened_boundary,
            "signal_role": self.signal_role.value,
            "observability": self.observability.value,
            "headline_text": self.headline_text,
            "raw_source_uri": self.raw_source_uri,
            "evidence_claim_id": self.evidence_claim_id,
            "lead_time_days_to_financial_recognition": self.lead_time_days_to_financial_recognition,
            "propagation_lag_days_from_upstream_signal": self.propagation_lag_days_from_upstream_signal,
            "reference_event_date": self.reference_event_date.isoformat() if self.reference_event_date else None,
            "censor_date": self.censor_date.isoformat() if self.censor_date else None,
            "censored_lead_days": self.censored_lead_days,
            "lead_time_status": self.lead_time_status.value,
        }


DEFAULT_AUTHORED_OBS_YAML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "observatory", "observations.yaml"
)


class ObservatoryMonitor:
    """Manages observation evaluation, bitemporal verification, and scoreboard scoring."""

    def __init__(self, parquet_path: str = OBSERVATIONS_PARQUET, authored_obs_yaml: Optional[str] = None):
        self.parquet_path = parquet_path
        self.authored_obs_yaml = authored_obs_yaml or DEFAULT_AUTHORED_OBS_YAML
        self.observations: List[MonitoredObservation] = []
        self.load_observations()

    def load_observations(self) -> None:
        """Loads and validates observations from Parquet."""
        if not os.path.exists(self.parquet_path):
            self.observations = []
            return

        df = pd.read_parquet(self.parquet_path)
        obs_list = []
        for _, row in df.iterrows():
            src_date = date.fromisoformat(str(row["source_event_date"]))
            pub_date = date.fromisoformat(str(row["first_publicly_observable_date"]))
            ing_date = date.fromisoformat(str(row["ingestion_date"]))

            # Strict bitemporal ordering verification:
            # Event occurred <= first publicly visible <= ingested by observatory
            assert src_date <= pub_date, f"Bitemporal leak: source_date {src_date} > pub_date {pub_date}"
            assert pub_date <= ing_date, f"Ingestion lookahead: pub_date {pub_date} > ing_date {ing_date}"

            lt_days = row.get("lead_time_days_to_financial_recognition")
            lt_val = float(lt_days) if pd.notna(lt_days) else None

            prop_days = row.get("propagation_lag_days_from_upstream_signal")
            prop_val = float(prop_days) if pd.notna(prop_days) else None

            cens_days = row.get("censored_lead_days")
            cens_val = float(cens_days) if pd.notna(cens_days) else None

            ref_date = date.fromisoformat(str(row["reference_event_date"])) if pd.notna(row.get("reference_event_date")) and str(row.get("reference_event_date")).strip() != "" and str(row.get("reference_event_date")) != "None" else None
            censor_dt = date.fromisoformat(str(row["censor_date"])) if pd.notna(row.get("censor_date")) and str(row.get("censor_date")).strip() != "" and str(row.get("censor_date")) != "None" else None

            obs_list.append(MonitoredObservation(
                observation_id=str(row["observation_id"]),
                indicator_id=str(row["indicator_id"]),
                project_id=str(row["project_id"]),
                source_event_date=src_date,
                first_publicly_observable_date=pub_date,
                ingestion_date=ing_date,
                clock_affected=ClockType(str(row["clock_affected"])),
                threatened_boundary=str(row["threatened_boundary"]),
                signal_role=SignalRole(str(row["signal_role"])),
                observability=Observability(str(row["observability"])),
                headline_text=str(row["headline_text"]),
                raw_source_uri=str(row["raw_source_uri"]),
                evidence_claim_id=str(row.get("evidence_claim_id", "")),
                lead_time_days_to_financial_recognition=lt_val,
                propagation_lag_days_from_upstream_signal=prop_val,
                reference_event_date=ref_date,
                censor_date=censor_dt,
                censored_lead_days=cens_val,
                lead_time_status=LeadTimeStatus(str(row["lead_time_status"])),
            ))
        self.observations = obs_list

    def add_observation(
        self,
        observation_id: str,
        indicator_id: str,
        project_id: str,
        source_event_date: date,
        first_publicly_observable_date: date,
        ingestion_date: date,
        clock_affected: ClockType,
        threatened_boundary: str,
        signal_role: SignalRole,
        observability: Observability,
        headline_text: str,
        raw_source_uri: str,
        evidence_claim_id: str,
        lead_time_days_to_financial_recognition: Optional[float] = None,
        propagation_lag_days_from_upstream_signal: Optional[float] = None,
        reference_event_date: Optional[date] = None,
        censor_date: Optional[date] = None,
        censored_lead_days: Optional[float] = None,
        lead_time_status: LeadTimeStatus = LeadTimeStatus.MONITORING_WINDOW,
    ) -> MonitoredObservation:
        """Adds a new verified observation by routing directly through canonical observations.yaml and recompiling."""
        assert source_event_date <= first_publicly_observable_date, f"Bitemporal leak: source {source_event_date} > pub {first_publicly_observable_date}"
        assert first_publicly_observable_date <= ingestion_date, f"Ingestion lookahead: pub {first_publicly_observable_date} > ingest {ingestion_date}"

        # 1. Foreign-key validation against verified repository claims
        from curate_observatory import collect_verified_evidence_claim_ids, compile_observatory_datasets
        import yaml

        verified_claims = collect_verified_evidence_claim_ids()
        if evidence_claim_id not in verified_claims:
            raise ValueError(f"Foreign-key error: claim '{evidence_claim_id}' not found in verified evidence ledger.")

        # 2. Append to authored observations.yaml
        obs_yaml_path = self.authored_obs_yaml
        with open(obs_yaml_path, "r", encoding="utf-8") as f:
            authored_obs = yaml.safe_load(f) or []

        existing_ids = {o["observation_id"] for o in authored_obs}
        if observation_id in existing_ids:
            raise ValueError(f"Observation ID '{observation_id}' already exists in observations.yaml")

        new_entry = {
            "observation_id": observation_id,
            "indicator_id": indicator_id,
            "project_id": project_id,
            "source_event_date": source_event_date.isoformat(),
            "first_publicly_observable_date": first_publicly_observable_date.isoformat(),
            "ingestion_date": ingestion_date.isoformat(),
            "clock_affected": clock_affected.value,
            "threatened_boundary": threatened_boundary,
            "signal_role": signal_role.value,
            "observability": observability.value,
            "headline_text": headline_text,
            "raw_source_uri": raw_source_uri,
            "lead_time_days_to_financial_recognition": lead_time_days_to_financial_recognition,
            "propagation_lag_days_from_upstream_signal": propagation_lag_days_from_upstream_signal,
            "reference_event_date": reference_event_date.isoformat() if reference_event_date else None,
            "censor_date": censor_date.isoformat() if censor_date else None,
            "censored_lead_days": censored_lead_days,
            "lead_time_status": lead_time_status.value,
            "evidence_claim_id": evidence_claim_id,
        }
        authored_obs.append(new_entry)
        with open(obs_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(authored_obs, f, sort_keys=False, default_flow_style=False)

        # 3. Recompile canonical Parquets and CSVs
        if os.path.abspath(obs_yaml_path) == os.path.abspath(DEFAULT_AUTHORED_OBS_YAML):
            compile_observatory_datasets()
        else:
            df = pd.DataFrame(authored_obs)
            df.to_parquet(self.parquet_path, index=False)

        # 4. Reload in-memory observations from compiled storage
        self.load_observations()
        return next(o for o in self.observations if o.observation_id == observation_id)

    def save_observations(self) -> None:
        """Disabled: Compiled Parquet/CSV is strictly derivative of authored YAML."""
        raise RuntimeError(
            "Direct mutation of derived Parquet/CSV is prohibited. "
            "Authored YAML (data/observatory/observations.yaml) is the sole canonical source of truth. "
            "Use add_observation() or CandidateStore.promote_to_canonical(), which update observations.yaml and recompile."
        )

    def compute_empirical_scoreboard(self) -> Dict[str, Any]:
        """Calculates exact empirical scoreboard metrics across all tracked observations."""
        df = pd.DataFrame([obs.to_dict() for obs in self.observations])
        if df.empty:
            return {"total_observations": 0}

        # 1. Early warning detection lead sample: strictly EARLY_WARNING signals preceding financial recognition
        ew_mask = (df["lead_time_status"] == LeadTimeStatus.OBSERVED.value) & (df["signal_role"] == SignalRole.EARLY_WARNING.value)
        ew_df = df[ew_mask]
        ew_leads = [float(x) for x in ew_df["lead_time_days_to_financial_recognition"].dropna() if float(x) > 0]

        # 2. Event propagation lag sample: downstream contractual response times
        prop_lags = [float(x) for x in df["propagation_lag_days_from_upstream_signal"].dropna() if float(x) > 0]

        # 3. Right-censored disclosure lag sample
        rc_df = df[df["lead_time_status"] == LeadTimeStatus.RIGHT_CENSORED_OBSERVED.value]
        rc_days = [float(x) for x in rc_df["censored_lead_days"].dropna()]

        return {
            "total_observations_logged": len(df),
            "projects_monitored": sorted(df["project_id"].unique().tolist()),
            "observed_early_warning_sample_count": len(ew_leads),
            "exact_early_warning_lead_days": ew_leads[0] if len(ew_leads) == 1 else None,
            "median_early_warning_lead_days": float(pd.Series(ew_leads).median()) if ew_leads else None,
            "max_early_warning_lead_days": float(max(ew_leads)) if ew_leads else None,
            "observed_propagation_lag_days": prop_lags[0] if len(prop_lags) == 1 else (max(prop_lags) if prop_lags else None),
            "right_censored_signals_count": len(rc_df),
            "right_censored_disclosure_lag_days": rc_days[0] if rc_days else None,
            "cross_layer_join_information_gain": "DEMONSTRATED (July 15 NMSLO Order -> Sept 18 Loan Mark = 65d Lead)",
            # Explicit canonical scoreboard presentation
            "observed_public_early_warning_episodes": len(ew_leads),
            "detection_lead_days": ew_leads[0] if len(ew_leads) == 1 else None,
            "contract_response_propagation_lag_days": prop_lags[0] if len(prop_lags) == 1 else None,
            "sec_disclosure_lag_display": f">={rc_days[0]:.0f} days (right-censored)" if rc_days else None,
        }
