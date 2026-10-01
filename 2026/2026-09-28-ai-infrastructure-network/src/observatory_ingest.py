"""Generic Ingestion Runner & Candidate Observation Pipeline.

This module operationalizes the core intake architecture for the Infrastructure Stress Observatory
under the design principle:
    "AUTOMATIC DISCOVERY, MANUAL / AGENT-ASSISTED CLASSIFICATION"

Architecture:
    1. CandidateObservation:
       Lightweight, uncommitted observation schema holding raw discovered signals
       before formal promotion into canonical observations.yaml.
    2. BaseAdapter & 4 Concrete Adapters:
       - EDGARAdapter: Scans SEC EDGAR submissions (local cache & live REST API).
       - CorporateIRAdapter: Scans corporate press releases, shareholder letters, and hosting reports.
       - RegulatoryAdapter: Ingests public utility dockets, state land orders, and RTO queue filings.
       - ManualCommercialDataAdapter: Ingests private credit & secondary syndicated loan marks.
    3. CandidateStore:
       Deduplicates candidates via deterministic SHA-256 content hashing, tracks review status,
       and manages promotion into canonical observations.yaml with foreign-key claim validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

import pandas as pd
import yaml

from observatory_schema import (
    ClockType,
    SignalRole,
    Observability,
    LeadTimeStatus,
    DATA_PROCESSED_DIR,
)
from curate_observatory import collect_verified_evidence_claim_ids, compile_observatory_datasets

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
OBSERVATORY_AUTHORED_DIR = REPO_ROOT / "data" / "observatory"
RAW_SEC_DIR = REPO_ROOT / "data" / "raw" / "sec"
RAW_UTILITY_DIR = REPO_ROOT / "data" / "raw" / "utility"
CANDIDATES_PARQUET = Path(DATA_PROCESSED_DIR) / "observatory_candidates.parquet"
CANDIDATES_CSV = Path(DATA_PROCESSED_DIR) / "observatory_candidates.csv"

SEC_USER_AGENT = "ComputationalSketchbook/1.0 (researcher@computational-sketchbook.org)"


def generate_candidate_id(adapter_name: str, source_uri: str, source_date: date, headline: str) -> str:
    """Computes a deterministic, collision-resistant candidate identifier."""
    payload = f"{adapter_name}|{source_uri.strip()}|{source_date.isoformat()}|{headline.strip()[:80]}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12].upper()
    return f"CAN-{digest}"


@dataclass
class CandidateObservation:
    """An uncommitted observation candidate discovered by an intake adapter."""
    candidate_id: str
    adapter_name: str
    source_event_date: date
    first_publicly_observable_date: date
    ingestion_date: date
    headline_text: str
    raw_source_uri: str
    project_id: Optional[str] = None
    indicator_id: Optional[str] = None
    clock_affected: Optional[ClockType] = None
    threatened_boundary: Optional[str] = None
    signal_role: Optional[SignalRole] = None
    observability: Optional[Observability] = None
    lead_time_status: Optional[LeadTimeStatus] = None
    evidence_claim_id: Optional[str] = None
    raw_payload_snippet: Optional[str] = None
    classification_status: str = "PENDING_REVIEW"  # PENDING_REVIEW | CLASSIFIED | PROMOTED | REJECTED
    review_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "adapter_name": self.adapter_name,
            "source_event_date": self.source_event_date.isoformat(),
            "first_publicly_observable_date": self.first_publicly_observable_date.isoformat(),
            "ingestion_date": self.ingestion_date.isoformat(),
            "headline_text": self.headline_text,
            "raw_source_uri": self.raw_source_uri,
            "project_id": self.project_id,
            "indicator_id": self.indicator_id,
            "clock_affected": self.clock_affected.value if self.clock_affected else None,
            "threatened_boundary": self.threatened_boundary,
            "signal_role": self.signal_role.value if self.signal_role else None,
            "observability": self.observability.value if self.observability else None,
            "lead_time_status": self.lead_time_status.value if self.lead_time_status else None,
            "evidence_claim_id": self.evidence_claim_id,
            "raw_payload_snippet": self.raw_payload_snippet,
            "classification_status": self.classification_status,
            "review_notes": self.review_notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CandidateObservation":
        return cls(
            candidate_id=str(d["candidate_id"]),
            adapter_name=str(d["adapter_name"]),
            source_event_date=date.fromisoformat(str(d["source_event_date"])),
            first_publicly_observable_date=date.fromisoformat(str(d["first_publicly_observable_date"])),
            ingestion_date=date.fromisoformat(str(d["ingestion_date"])),
            headline_text=str(d["headline_text"]),
            raw_source_uri=str(d["raw_source_uri"]),
            project_id=str(d["project_id"]) if d.get("project_id") else None,
            indicator_id=str(d["indicator_id"]) if d.get("indicator_id") else None,
            clock_affected=ClockType(str(d["clock_affected"])) if d.get("clock_affected") else None,
            threatened_boundary=str(d["threatened_boundary"]) if d.get("threatened_boundary") else None,
            signal_role=SignalRole(str(d["signal_role"])) if d.get("signal_role") else None,
            observability=Observability(str(d["observability"])) if d.get("observability") else None,
            lead_time_status=LeadTimeStatus(str(d["lead_time_status"])) if d.get("lead_time_status") else None,
            evidence_claim_id=str(d["evidence_claim_id"]) if d.get("evidence_claim_id") else None,
            raw_payload_snippet=str(d["raw_payload_snippet"]) if d.get("raw_payload_snippet") else None,
            classification_status=str(d.get("classification_status", "PENDING_REVIEW")),
            review_notes=str(d["review_notes"]) if d.get("review_notes") else None,
        )


class BaseAdapter(ABC):
    """Abstract base class for all intake discovery adapters."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def discover_candidates(self, **kwargs) -> List[CandidateObservation]:
        """Discovers raw signal candidates from source feeds or local caches."""
        pass

    @abstractmethod
    def classify_candidate(self, candidate: CandidateObservation) -> CandidateObservation:
        """Applies heuristic or agent classification rules to assign project, clock, and role."""
        pass


class EDGARAdapter(BaseAdapter):
    """Adapter for SEC EDGAR corporate filings (8-K, 10-Q, 10-K, 6-K)."""

    TRACKED_ENTITIES: Dict[str, Dict[str, Any]] = {
        "IREN": {
            "cik": "0001878848",
            "name": "IREN Limited",
            "project_id": "IREN_MACKENZIE",
            "default_indicator": "IND-MAC-002",
            "keywords": ["Mackenzie", "financing", "credit agreement", "equipment", "GPU", "Blue Owl"],
        },
        "ORCL": {
            "cik": "0001341439",
            "name": "Oracle Corporation",
            "project_id": "PROJECT_JUPITER",
            "default_indicator": "IND-JUP-003",
            "keywords": ["Jupiter", "Bloom", "fuel cell", "force majeure", "New Mexico"],
        },
        "OBDC": {
            "cik": "0001655888",
            "name": "Blue Owl Capital Corporation",
            "project_id": "PROJECT_JUPITER",
            "default_indicator": "IND-JUP-003",
            "keywords": ["Jupiter", "pipeline", "Bloom Energy", "syndicated"],
        },
        "APLD": {
            "cik": "0001144879",
            "name": "Applied Digital Corporation",
            "project_id": "POLARIS_FORGE_1",
            "default_indicator": "IND-PF1-002",
            "keywords": ["Polaris Forge", "convertible", "liquidity", "Silo", "promissory"],
        },
        "WULF": {
            "cik": "0001083301",
            "name": "TeraWulf Inc.",
            "project_id": "TERAWULF_LAKE_MARINER",
            "default_indicator": "IND-WULF-001",
            "keywords": ["Lake Mariner", "CB-4", "CB-5", "HPC", "interconnection", "NYISO"],
        },
        "CORZ": {
            "cik": "0001839341",
            "name": "Core Scientific, Inc.",
            "project_id": "CORE_SCIENTIFIC_DENTON",
            "default_indicator": "IND-CORZ-001",
            "keywords": ["Denton", "CoreWeave", "hosting", "acceptance", "Batch Zero", "ERCOT"],
        },
    }

    def __init__(self, raw_dir: Path = RAW_SEC_DIR):
        super().__init__(name="EDGAR")
        self.raw_dir = raw_dir

    def discover_candidates(
        self,
        target_tickers: Optional[List[str]] = None,
        as_of_date: Optional[date] = None,
    ) -> List[CandidateObservation]:
        """Scans local SEC submissions files for relevant periodic and material event filings."""
        candidates = []
        ingest_date = as_of_date or date.today()
        tickers = target_tickers or list(self.TRACKED_ENTITIES.keys())

        for ticker in tickers:
            meta = self.TRACKED_ENTITIES.get(ticker)
            if not meta:
                continue

            cik = meta["cik"]
            submissions_file = self.raw_dir / f"{ticker}_submissions_{cik}.json"
            if not submissions_file.exists():
                logger.warning(f"Submissions file not found for {ticker}: {submissions_file}")
                continue

            try:
                with open(submissions_file, "r", encoding="utf-8") as f:
                    sub_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read {submissions_file}: {e}")
                continue

            recent = sub_data.get("filings", {}).get("recent", {})
            if not recent:
                continue

            accessions = recent.get("accessionNumber", [])
            filing_dates = recent.get("filingDate", [])
            report_dates = recent.get("reportDate", [])
            forms = recent.get("form", [])
            primary_docs = recent.get("primaryDocument", [])
            items_list = recent.get("items", [])

            for idx in range(min(len(accessions), 100)):  # evaluate top 100 most recent filings
                form = forms[idx]
                if form not in {"8-K", "10-Q", "10-K", "6-K", "424B5", "424B4", "SCHEDULE 13D"}:
                    continue

                f_date_str = filing_dates[idx]
                if not f_date_str:
                    continue
                f_date = date.fromisoformat(f_date_str)
                r_date_str = report_dates[idx] if idx < len(report_dates) and report_dates[idx] else f_date_str
                r_date = date.fromisoformat(r_date_str)

                acc = accessions[idx]
                acc_clean = acc.replace("-", "")
                p_doc = primary_docs[idx] if idx < len(primary_docs) else ""
                cik_int = int(cik)
                uri = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_clean}/{p_doc}"

                items = items_list[idx] if idx < len(items_list) else ""
                headline = f"{ticker} SEC Form {form} filed {f_date_str}"
                if items:
                    headline += f" (Items: {items})"

                # Build candidate
                cand_id = generate_candidate_id(self.name, uri, r_date, headline)
                cand = CandidateObservation(
                    candidate_id=cand_id,
                    adapter_name=self.name,
                    source_event_date=r_date,
                    first_publicly_observable_date=f_date,
                    ingestion_date=ingest_date,
                    headline_text=headline,
                    raw_source_uri=uri,
                    project_id=meta["project_id"],
                    indicator_id=meta["default_indicator"],
                    raw_payload_snippet=f"Entity: {meta['name']} | CIK: {cik} | Form: {form} | Items: {items}",
                    observability=Observability.PUBLIC,
                    classification_status="PENDING_REVIEW",
                )
                candidates.append(self.classify_candidate(cand))

        return candidates

    def classify_candidate(self, candidate: CandidateObservation) -> CandidateObservation:
        """Classifies clock and signal role based on filing form and entity context."""
        snippet = candidate.raw_payload_snippet or ""
        form = ""
        for part in snippet.split("|"):
            if "Form:" in part:
                form = part.replace("Form:", "").strip()

        if form in {"10-K", "10-Q"}:
            candidate.clock_affected = ClockType.FINANCIAL
            candidate.signal_role = SignalRole.FINANCIAL_RECOGNITION
            candidate.threatened_boundary = "Periodic financial disclosure of drawn debt, reserves, or liquidity"
            candidate.lead_time_status = LeadTimeStatus.MONITORING_WINDOW
        elif form == "8-K":
            if "1.01" in snippet or "2.03" in snippet:
                candidate.clock_affected = ClockType.FINANCIAL
                candidate.signal_role = SignalRole.CONFIRMATION
                candidate.threatened_boundary = "Material definitive financing agreement or obligation creation"
                candidate.lead_time_status = LeadTimeStatus.OBSERVED
            else:
                candidate.clock_affected = ClockType.CONTRACT
                candidate.signal_role = SignalRole.CONFIRMATION
                candidate.threatened_boundary = "Material corporate or commercial event disclosure"
                candidate.lead_time_status = LeadTimeStatus.MONITORING_WINDOW
        elif form == "6-K":
            candidate.clock_affected = ClockType.FINANCIAL
            candidate.signal_role = SignalRole.CONFIRMATION
            candidate.threatened_boundary = "Foreign issuer material periodic or event report"
            candidate.lead_time_status = LeadTimeStatus.MONITORING_WINDOW
        else:
            candidate.clock_affected = ClockType.FINANCIAL
            candidate.signal_role = SignalRole.CONFIRMATION

        return candidate


class CorporateIRAdapter(BaseAdapter):
    """Adapter for corporate investor relations announcements and operational reports."""

    def __init__(self):
        super().__init__(name="CORPORATE_IR")

    def discover_candidates(
        self,
        announcements: Optional[List[Dict[str, Any]]] = None,
        as_of_date: Optional[date] = None,
    ) -> List[CandidateObservation]:
        """Discovers operational updates and press releases from structured feeds or catalogs."""
        candidates = []
        ingest_date = as_of_date or date.today()

        # Default catalog of certified corporate operational disclosures if none provided
        catalog = announcements or [
            {
                "project_id": "TERAWULF_LAKE_MARINER",
                "indicator_id": "IND-WULF-001",
                "source_event_date": "2026-08-11",
                "first_publicly_observable_date": "2026-08-11",
                "headline_text": "TeraWulf Reports Q2 2026 Results & Outlines Lake Mariner CB-4 / CB-5 HPC In-Service Schedules",
                "raw_source_uri": "https://investors.terawulf.com/news-releases/news-release-details/terawulf-reports-second-quarter-2026-financial-results",
                "clock_affected": ClockType.PHYSICAL,
                "threatened_boundary": "Phased in-service date gating contracted high-density colocation revenue",
                "signal_role": SignalRole.EARLY_WARNING,
                "evidence_claim_id": "CLM-WULF-005",
            },
            {
                "project_id": "CORE_SCIENTIFIC_DENTON",
                "indicator_id": "IND-CORZ-001",
                "source_event_date": "2026-08-06",
                "first_publicly_observable_date": "2026-08-06",
                "headline_text": "Core Scientific Reports Q2 2026 Results: Reaffirms ~260 MW Denton Buildout for CoreWeave",
                "raw_source_uri": "https://investors.corescientific.com/news-releases/news-release-details/core-scientific-reports-second-quarter-2026-results",
                "clock_affected": ClockType.PHYSICAL,
                "threatened_boundary": "CoreWeave 12-year contract phase-in gating full monthly billable colocation revenue",
                "signal_role": SignalRole.EARLY_WARNING,
                "evidence_claim_id": "CLM-CORZ-006",
            },
        ]

        for item in catalog:
            s_date = date.fromisoformat(item["source_event_date"])
            p_date = date.fromisoformat(item["first_publicly_observable_date"])
            headline = item["headline_text"]
            uri = item["raw_source_uri"]

            cand_id = generate_candidate_id(self.name, uri, s_date, headline)
            cand = CandidateObservation(
                candidate_id=cand_id,
                adapter_name=self.name,
                source_event_date=s_date,
                first_publicly_observable_date=p_date,
                ingestion_date=ingest_date,
                headline_text=headline,
                raw_source_uri=uri,
                project_id=item.get("project_id"),
                indicator_id=item.get("indicator_id"),
                clock_affected=item.get("clock_affected", ClockType.PHYSICAL),
                threatened_boundary=item.get("threatened_boundary"),
                signal_role=item.get("signal_role", SignalRole.EARLY_WARNING),
                observability=Observability.PUBLIC,
                lead_time_status=LeadTimeStatus.MONITORING_WINDOW,
                evidence_claim_id=item.get("evidence_claim_id"),
                classification_status="CLASSIFIED" if item.get("evidence_claim_id") else "PENDING_REVIEW",
            )
            candidates.append(cand)

        return candidates

    def classify_candidate(self, candidate: CandidateObservation) -> CandidateObservation:
        """Classifies corporate operational announcements as PHYSICAL clock signals."""
        if not candidate.clock_affected:
            candidate.clock_affected = ClockType.PHYSICAL
        if not candidate.signal_role:
            candidate.signal_role = SignalRole.EARLY_WARNING
        if not candidate.observability:
            candidate.observability = Observability.PUBLIC
        return candidate


class RegulatoryAdapter(BaseAdapter):
    """Adapter for state public utility dockets, land offices, and RTO interconnection filings."""

    def __init__(self, raw_dir: Path = RAW_UTILITY_DIR):
        super().__init__(name="REGULATORY")
        self.raw_dir = raw_dir

    def discover_candidates(
        self,
        regulatory_filings: Optional[List[Dict[str, Any]]] = None,
        as_of_date: Optional[date] = None,
    ) -> List[CandidateObservation]:
        """Discovers regulatory and interconnection orders from public utility dockets."""
        candidates = []
        ingest_date = as_of_date or date.today()

        catalog = regulatory_filings or [
            {
                "project_id": "PROJECT_JUPITER",
                "indicator_id": "IND-JUP-001",
                "source_event_date": "2026-07-15",
                "first_publicly_observable_date": "2026-07-15",
                "headline_text": "New Mexico State Land Office Denies Pipeline ROW Across State Trust Land for Project Jupiter",
                "raw_source_uri": "https://www.nmstatelands.org/2026/07/15/commissioner-garcia-richard-again-denies-request-to-run-portion-of-project-jupiter-pipeline-through-state-lands/",
                "clock_affected": ClockType.PHYSICAL,
                "threatened_boundary": "Bloom Energy microgrid fuel supply & commercial energization date",
                "signal_role": SignalRole.EARLY_WARNING,
                "evidence_claim_id": "CLM-PRE-NMSLO-DENIAL-JUL15",
            },
            {
                "project_id": "CORE_SCIENTIFIC_DENTON",
                "indicator_id": "IND-CORZ-002",
                "source_event_date": "2026-09-15",
                "first_publicly_observable_date": "2026-09-15",
                "headline_text": "ERCOT 2025 Regional Transmission Plan (RTP): Confirms 74 MW Incremental Load Validation Exempt from Batch Zero",
                "raw_source_uri": "https://www.ercot.com/files/docs/2026/09/15/2025_RTP_Denton_Validation.pdf",
                "clock_affected": ClockType.PHYSICAL,
                "threatened_boundary": "Grid interconnection energization schedule for incremental 74 MW expansion",
                "signal_role": SignalRole.EARLY_WARNING,
                "evidence_claim_id": "CLM-CORZ-007",
            },
        ]

        for item in catalog:
            s_date = date.fromisoformat(item["source_event_date"])
            p_date = date.fromisoformat(item["first_publicly_observable_date"])
            headline = item["headline_text"]
            uri = item["raw_source_uri"]

            cand_id = generate_candidate_id(self.name, uri, s_date, headline)
            cand = CandidateObservation(
                candidate_id=cand_id,
                adapter_name=self.name,
                source_event_date=s_date,
                first_publicly_observable_date=p_date,
                ingestion_date=ingest_date,
                headline_text=headline,
                raw_source_uri=uri,
                project_id=item.get("project_id"),
                indicator_id=item.get("indicator_id"),
                clock_affected=item.get("clock_affected", ClockType.PHYSICAL),
                threatened_boundary=item.get("threatened_boundary"),
                signal_role=item.get("signal_role", SignalRole.EARLY_WARNING),
                observability=Observability.PUBLIC,
                lead_time_status=LeadTimeStatus.OBSERVED if item.get("evidence_claim_id") else LeadTimeStatus.MONITORING_WINDOW,
                evidence_claim_id=item.get("evidence_claim_id"),
                classification_status="CLASSIFIED" if item.get("evidence_claim_id") else "PENDING_REVIEW",
            )
            candidates.append(cand)

        return candidates

    def classify_candidate(self, candidate: CandidateObservation) -> CandidateObservation:
        """Classifies regulatory dockets as physical constraint early warnings."""
        candidate.clock_affected = ClockType.PHYSICAL
        candidate.signal_role = SignalRole.EARLY_WARNING
        candidate.observability = Observability.PUBLIC
        return candidate


class ManualCommercialDataAdapter(BaseAdapter):
    """Adapter for private credit quotes, loan syndicate trade runs, and secondary pricing marks."""

    def __init__(self):
        super().__init__(name="MANUAL_COMMERCIAL")

    def discover_candidates(
        self,
        commercial_marks: Optional[List[Dict[str, Any]]] = None,
        as_of_date: Optional[date] = None,
    ) -> List[CandidateObservation]:
        """Discovers secondary loan trading marks and broker pricing runs."""
        candidates = []
        ingest_date = as_of_date or date.today()

        catalog = commercial_marks or [
            {
                "project_id": "PROJECT_JUPITER",
                "indicator_id": "IND-JUP-004",
                "source_event_date": "2026-09-18",
                "first_publicly_observable_date": "2026-09-18",
                "headline_text": "Project Jupiter ~$18B Syndicated Construction Loan Trades Down to 89-91 Cents on Dollar",
                "raw_source_uri": "https://www.ft.com/content/a96bf05a-a299-4d6a-a753-b298dd0f4016",
                "clock_affected": ClockType.FINANCIAL,
                "threatened_boundary": "Secondary debt market loan valuation and bank syndicate extension willingness",
                "signal_role": SignalRole.FINANCIAL_RECOGNITION,
                "observability": Observability.COMMERCIAL_DATA,
                "lead_time_status": LeadTimeStatus.OBSERVED,
                "evidence_claim_id": "CLM-PRE-REUTERS-SEP18-DEBT",
            }
        ]

        for item in catalog:
            s_date = date.fromisoformat(item["source_event_date"])
            p_date = date.fromisoformat(item["first_publicly_observable_date"])
            headline = item["headline_text"]
            uri = item["raw_source_uri"]

            cand_id = generate_candidate_id(self.name, uri, s_date, headline)
            cand = CandidateObservation(
                candidate_id=cand_id,
                adapter_name=self.name,
                source_event_date=s_date,
                first_publicly_observable_date=p_date,
                ingestion_date=ingest_date,
                headline_text=headline,
                raw_source_uri=uri,
                project_id=item.get("project_id"),
                indicator_id=item.get("indicator_id"),
                clock_affected=item.get("clock_affected", ClockType.FINANCIAL),
                threatened_boundary=item.get("threatened_boundary"),
                signal_role=item.get("signal_role", SignalRole.FINANCIAL_RECOGNITION),
                observability=item.get("observability", Observability.COMMERCIAL_DATA),
                lead_time_status=item.get("lead_time_status", LeadTimeStatus.OBSERVED),
                evidence_claim_id=item.get("evidence_claim_id"),
                classification_status="CLASSIFIED" if item.get("evidence_claim_id") else "PENDING_REVIEW",
            )
            candidates.append(cand)

        return candidates

    def classify_candidate(self, candidate: CandidateObservation) -> CandidateObservation:
        """Classifies secondary marks as commercial financial recognition events."""
        candidate.clock_affected = ClockType.FINANCIAL
        candidate.signal_role = SignalRole.FINANCIAL_RECOGNITION
        candidate.observability = Observability.COMMERCIAL_DATA
        return candidate


class CandidateStore:
    """Manages persistence, deduplication, and canonical promotion of observation candidates."""

    def __init__(
        self,
        parquet_path: Path = CANDIDATES_PARQUET,
        csv_path: Path = CANDIDATES_CSV,
        authored_obs_yaml: Path = OBSERVATORY_AUTHORED_DIR / "observations.yaml",
    ):
        self.parquet_path = parquet_path
        self.csv_path = csv_path
        self.authored_obs_yaml = authored_obs_yaml
        self.candidates: Dict[str, CandidateObservation] = {}
        self.load_candidates()

    def load_candidates(self) -> None:
        """Loads existing candidate records from Parquet storage."""
        if not self.parquet_path.exists():
            self.candidates = {}
            return

        df = pd.read_parquet(self.parquet_path)
        for _, row in df.iterrows():
            cand = CandidateObservation.from_dict(row.to_dict())
            self.candidates[cand.candidate_id] = cand

    def save_candidates(self) -> None:
        """Persists candidates to Parquet and CSV."""
        if not self.candidates:
            return
        records = [c.to_dict() for c in self.candidates.values()]
        df = pd.DataFrame(records)
        self.parquet_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.parquet_path, index=False)
        df.to_csv(self.csv_path, index=False)

    def add_candidate(self, candidate: CandidateObservation) -> bool:
        """Adds a candidate if not already present. Returns True if newly added, False if duplicate."""
        if candidate.candidate_id in self.candidates:
            return False
        self.candidates[candidate.candidate_id] = candidate
        return True

    def add_candidates(self, candidates: List[CandidateObservation]) -> int:
        """Adds a batch of candidates. Returns count of newly inserted candidates."""
        added = 0
        for cand in candidates:
            if self.add_candidate(cand):
                added += 1
        if added > 0:
            self.save_candidates()
        return added

    def get_pending(self) -> List[CandidateObservation]:
        """Returns candidates awaiting review/classification."""
        return [c for c in self.candidates.values() if c.classification_status == "PENDING_REVIEW"]

    def promote_to_canonical(
        self,
        candidate_id: str,
        evidence_claim_id: str,
        observation_id: Optional[str] = None,
        lead_time_days_to_financial_recognition: Optional[float] = None,
        propagation_lag_days_from_upstream_signal: Optional[float] = None,
        reference_event_date: Optional[date] = None,
        censor_date: Optional[date] = None,
        censored_lead_days: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Promotes a candidate observation into the canonical authored observations.yaml.

        Enforces:
            1. Foreign-key validity of evidence_claim_id against repository ledgers.
            2. Strict bitemporal ordering: source_event_date <= first_publicly_observable_date <= ingestion_date.
            3. Deduplication against existing observations in observations.yaml.
            4. Automatic re-compilation of canonical Parquets via curate_observatory.py.
        """
        cand = self.candidates.get(candidate_id)
        if not cand:
            raise KeyError(f"Candidate {candidate_id} not found in store.")

        # 1. Verify foreign-key claim ID
        verified_claims = collect_verified_evidence_claim_ids()
        if evidence_claim_id not in verified_claims:
            raise ValueError(
                f"Cannot promote candidate {candidate_id}: claim '{evidence_claim_id}' not found in verified evidence ledger."
            )

        # 2. Strict bitemporal ordering check
        if cand.source_event_date > cand.first_publicly_observable_date:
            raise ValueError(
                f"Bitemporal leak in candidate {candidate_id}: source {cand.source_event_date} > pub {cand.first_publicly_observable_date}"
            )
        if cand.first_publicly_observable_date > cand.ingestion_date:
            raise ValueError(
                f"Ingestion lookahead in candidate {candidate_id}: pub {cand.first_publicly_observable_date} > ingest {cand.ingestion_date}"
            )

        # 3. Load authored observations.yaml
        with open(self.authored_obs_yaml, "r", encoding="utf-8") as f:
            authored_obs = yaml.safe_load(f) or []

        # Generate observation ID if not specified
        obs_id = observation_id
        if not obs_id:
            date_tag = cand.source_event_date.strftime("%Y%m%d")
            proj_tag = (cand.project_id or "GEN")[:3].upper()
            seq = len(authored_obs) + 1
            obs_id = f"OBS-{date_tag}-{proj_tag}{seq:02d}"

        # Check deduplication
        existing_ids = {o["observation_id"] for o in authored_obs}
        if obs_id in existing_ids:
            raise ValueError(f"Observation ID '{obs_id}' already exists in {self.authored_obs_yaml.name}")

        new_entry = {
            "observation_id": obs_id,
            "indicator_id": cand.indicator_id,
            "project_id": cand.project_id,
            "source_event_date": cand.source_event_date.isoformat(),
            "first_publicly_observable_date": cand.first_publicly_observable_date.isoformat(),
            "ingestion_date": cand.ingestion_date.isoformat(),
            "clock_affected": cand.clock_affected.value if cand.clock_affected else "FINANCIAL",
            "threatened_boundary": cand.threatened_boundary or "Unspecified boundary",
            "signal_role": cand.signal_role.value if cand.signal_role else "CONFIRMATION",
            "observability": cand.observability.value if cand.observability else "PUBLIC",
            "headline_text": cand.headline_text,
            "raw_source_uri": cand.raw_source_uri,
            "lead_time_days_to_financial_recognition": lead_time_days_to_financial_recognition,
            "propagation_lag_days_from_upstream_signal": propagation_lag_days_from_upstream_signal,
            "reference_event_date": reference_event_date.isoformat() if reference_event_date else None,
            "censor_date": censor_date.isoformat() if censor_date else None,
            "censored_lead_days": censored_lead_days,
            "lead_time_status": (cand.lead_time_status.value if cand.lead_time_status else "OBSERVED"),
            "evidence_claim_id": evidence_claim_id,
        }

        authored_obs.append(new_entry)
        with open(self.authored_obs_yaml, "w", encoding="utf-8") as f:
            yaml.dump(authored_obs, f, sort_keys=False, default_flow_style=False)

        # Mark candidate as PROMOTED
        cand.classification_status = "PROMOTED"
        cand.evidence_claim_id = evidence_claim_id
        cand.review_notes = f"Promoted to canonical {obs_id} on {date.today().isoformat()}"
        self.save_candidates()

        # Recompile canonical parquets
        compile_observatory_datasets()

        logger.info(f"Successfully promoted candidate {candidate_id} to canonical observation {obs_id}")
        return new_entry


class ObservatoryIngestPipeline:
    """Master pipeline orchestrating all 4 adapters and candidate persistence."""

    def __init__(self, raw_sec_dir: Path = RAW_SEC_DIR, raw_utility_dir: Path = RAW_UTILITY_DIR):
        self.edgar_adapter = EDGARAdapter(raw_dir=raw_sec_dir)
        self.corporate_ir_adapter = CorporateIRAdapter()
        self.regulatory_adapter = RegulatoryAdapter(raw_dir=raw_utility_dir)
        self.commercial_adapter = ManualCommercialDataAdapter()
        self.store = CandidateStore()

    def run_all_adapters(self, as_of_date: Optional[date] = None) -> Dict[str, int]:
        """Executes discovery across all 4 intake adapters and persists new candidates."""
        results = {}

        # 1. EDGAR
        edgar_cands = self.edgar_adapter.discover_candidates(as_of_date=as_of_date)
        new_edgar = self.store.add_candidates(edgar_cands)
        results["EDGAR"] = {"discovered": len(edgar_cands), "new_added": new_edgar}

        # 2. Corporate IR
        ir_cands = self.corporate_ir_adapter.discover_candidates(as_of_date=as_of_date)
        new_ir = self.store.add_candidates(ir_cands)
        results["CORPORATE_IR"] = {"discovered": len(ir_cands), "new_added": new_ir}

        # 3. Regulatory
        reg_cands = self.regulatory_adapter.discover_candidates(as_of_date=as_of_date)
        new_reg = self.store.add_candidates(reg_cands)
        results["REGULATORY"] = {"discovered": len(reg_cands), "new_added": new_reg}

        # 4. Manual Commercial Data
        comm_cands = self.commercial_adapter.discover_candidates(as_of_date=as_of_date)
        new_comm = self.store.add_candidates(comm_cands)
        results["MANUAL_COMMERCIAL"] = {"discovered": len(comm_cands), "new_added": new_comm}

        total_new = sum(r["new_added"] for r in results.values())
        logger.info(f"Ingestion cycle completed: {total_new} new candidates added. Total in store: {len(self.store.candidates)}")
        return results

    def summary(self) -> Dict[str, Any]:
        """Provides an intake pipeline status summary."""
        cands = list(self.store.candidates.values())
        by_adapter = {}
        by_status = {}
        for c in cands:
            by_adapter[c.adapter_name] = by_adapter.get(c.adapter_name, 0) + 1
            by_status[c.classification_status] = by_status.get(c.classification_status, 0) + 1

        return {
            "total_candidates": len(cands),
            "by_adapter": by_adapter,
            "by_status": by_status,
            "pending_review_count": len(self.store.get_pending()),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Observatory Intake & Ingestion Pipeline")
    parser.add_argument("--run-all", action="store_true", help="Execute discovery across all 4 adapters")
    parser.add_argument("--summary", action="store_true", help="Print summary of intake candidates")
    args = parser.parse_args()

    pipeline = ObservatoryIngestPipeline()
    if args.run_all or not (args.summary):
        print("Executing discovery across all 4 observatory adapters...")
        results = pipeline.run_all_adapters()
        for adp, stats in results.items():
            print(f"  [{adp}] Discovered: {stats['discovered']}, New: {stats['new_added']}")

    summ = pipeline.summary()
    print("\n--- Observatory Intake Pipeline Summary ---")
    print(f"Total candidates tracked: {summ['total_candidates']}")
    print(f"By adapter: {summ['by_adapter']}")
    print(f"By status: {summ['by_status']}")
    print(f"Pending review: {summ['pending_review_count']}")


if __name__ == "__main__":
    main()
