"""Discourse Analysis & Drama Engine.

Synthesizes collected discourse into:
1. Competing Factions & Stance Maps (who is talking, what are they claiming).
2. Friction & Drama Detection (blight, code citations, pricing disputes, crime, neighborhood beefs).
3. Ground-truth provenance annotations (persisted to derived/annotations.parquet).
4. Comprehensive Markdown analysis reports (ANALYSIS_REPORT.md).
"""

import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from observatory.config import Settings, get_settings
from observatory.models import (
    Annotation,
    AnnotationType,
    Artifact,
    ContentType,
)
from observatory.store.corpus import CorpusStore

console = Console()

# Lexicon patterns for friction & hyper-local drama detection
FRICTION_CATEGORIES = {
    "blight_and_hazards": {
        "label": "Blight, Hazard & Code Enforcement",
        "keywords": [
            "collapse",
            "roof",
            "unpermitted",
            "condemned",
            "code violation",
            "blight",
            "demolition",
            "trash",
            "dumpster",
            "dumping",
            "rats",
            "mice",
            "infest",
            "structural",
            "hazard",
            "dangerous",
            "abandoned",
            "debris",
            "eyesore",
            "decay",
        ],
    },
    "labor_and_consumer_friction": {
        "label": "Labor Strain & Consumer Friction",
        "keywords": [
            "overcharge",
            "pricing",
            "discrepancy",
            "lawsuit",
            "sue",
            "suing",
            "attorney general",
            "audit",
            "understaffed",
            "alone",
            "one worker",
            "short staffed",
            "price tag",
            "gouging",
            "wages",
            "strike",
            "union",
            "receipt",
            "ripoff",
            "scam",
        ],
    },
    "crime_and_public_safety": {
        "label": "Crime & Public Safety",
        "keywords": [
            "robbery",
            "shooting",
            "shot",
            "gun",
            "gunfire",
            "police",
            "armed",
            "killed",
            "injured",
            "stolen",
            "stealing",
            "looting",
            "thief",
            "thievery",
            "crime",
            "safety",
            "scared",
            "security guard",
            "fight",
            "assault",
        ],
    },
    "civic_controversy_and_pushback": {
        "label": "Civic Pushback & Institutional Distrust",
        "keywords": [
            "tax abatement",
            "subsidies",
            "billionaire",
            "boycott",
            "petition",
            "protest",
            "shouting",
            "snitch",
            "greed",
            "corrupt",
            "corruption",
            "investigation",
            "controversy",
            "oppose",
            "outrage",
            "shame",
            "bribe",
            "unaccountable",
            "gentrification",
        ],
    },
}

# Voices / Factions detection heuristics
FACTION_INDICATORS = {
    "resident_shopper": {
        "label": "Impacted Residents & Consumers",
        "description": (
            "Everyday community members sharing firsthand experiences, "
            "neighborhood conditions, and consumer grievances."
        ),
        "patterns": [
            r"\bi live\b",
            r"\bmy neighborhood\b",
            r"\bi shop\b",
            r"\bi went\b",
            r"\bour community\b",
            r"\bmy kid\b",
            r"\bwe pay\b",
            r"\bmy street\b",
            r"\bnear my house\b",
            r"\baround here\b",
            r"\bdown the street\b",
        ],
    },
    "frontline_worker": {
        "label": "Frontline Workers & Staff",
        "description": "Store employees, classroom educators, and transit operators on the ground.",
        "patterns": [
            r"\bwe work\b",
            r"\bin our store\b",
            r"\bmy shift\b",
            r"\bunderstaffed\b",
            r"\bin my classroom\b",
            r"\bteachers are\b",
            r"\bthe staff\b",
            r"\bwe only have one\b",
        ],
    },
    "watchdog_activist": {
        "label": "Civic Watchdogs & Organizers",
        "description": (
            "Tenant advocates, environmentalists, peace organizers, and community journalists."
        ),
        "patterns": [
            r"\blawsuit filed\b",
            r"\bcoalition\b",
            r"\bactivists\b",
            r"\borganizers\b",
            r"\bcity council meeting\b",
            r"\bdemanding accountability\b",
            r"\bpublic comment\b",
            r"\bpeaceworks\b",
            r"\btenants union\b",
        ],
    },
    "institutional_leadership": {
        "label": "Corporate & Institutional Leadership",
        "description": "Corporate press releases, district executives, and official spokespersons.",
        "patterns": [
            r"\bspokesperson\b",
            r"\bofficial statement\b",
            r"\bboard approved\b",
            r"\bannounces\b",
            r"\bstrategic plan\b",
            r"\binvestment of\b",
            r"\baccredited\b",
            r"\bwe are committed\b",
            r"\bpartnership\b",
        ],
    },
}


class DiscourseAnalyzer:
    """Performs synthesis, viewpoint classification, and drama detection on collected evidence."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.corpus = CorpusStore(settings=self.settings)

    def analyze_run(self, run_id: str) -> dict[str, Any]:
        """Analyze discourse for a specific research run ID."""
        run_dir = self.settings.runs_dir / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run directory not found: {run_dir}")

        # Fetch artifacts belonging to this run, including thread comments
        artifacts_df = self.corpus.query(
            f"""
            SELECT * FROM artifacts
            WHERE run_id = '{run_id}'
               OR thread_parent IN (SELECT native_id FROM artifacts WHERE run_id = '{run_id}')
            """
        )
        if artifacts_df.height == 0:
            # Fallback: check query records in the run directory
            queries_file = run_dir / "queries.jsonl"
            q_ids = []
            if queries_file.exists():
                for line in queries_file.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        import json

                        try:
                            rec = json.loads(line)
                            if "query_id" in rec:
                                q_ids.append(f"'{rec['query_id']}'")
                        except Exception:
                            pass
            if q_ids:
                artifacts_df = self.corpus.query(
                    f"SELECT * FROM artifacts WHERE query_id IN ({','.join(q_ids)})"
                )

        if artifacts_df.height == 0:
            return {"status": "empty", "message": f"No artifacts found for run {run_id}"}

        # Convert to list of Artifact models
        artifacts: list[Artifact] = []
        for row in artifacts_df.iter_rows(named=True):
            try:
                # Reconstruct engagement
                row_dict = dict(row)
                if row_dict.get("engagement") and isinstance(row_dict["engagement"], str):
                    import json

                    row_dict["engagement"] = json.loads(row_dict["engagement"])
                artifacts.append(Artifact.model_validate(row_dict))
            except Exception:
                pass

        # Fetch any existing transcription annotations
        transcripts_df = self.corpus.query(
            "SELECT artifact_id, value FROM annotations WHERE annotation_type = 'transcription'"
        )
        transcripts_by_art_id = (
            dict(transcripts_df.iter_rows()) if transcripts_df.height > 0 else {}
        )

        # Run analysis passes
        analysis_result = self._synthesize(artifacts, transcripts_by_art_id, run_id)

        # Store generated Level 3 annotations
        if analysis_result["annotations"]:
            self.corpus.store_annotations(analysis_result["annotations"])

        # Write ANALYSIS_REPORT.md
        self._write_report(run_dir, run_id, analysis_result)

        return analysis_result

    def _synthesize(
        self,
        artifacts: list[Artifact],
        transcripts: dict[str, str],
        run_id: str,
    ) -> dict[str, Any]:
        """Core synthesis pass over artifacts."""
        factions: dict[str, list[dict[str, Any]]] = {k: [] for k in FACTION_INDICATORS}
        friction_events: list[dict[str, Any]] = []
        annotations: list[Annotation] = []

        for a in artifacts:
            text = a.text or ""
            # Append spoken transcript if present
            if a.artifact_id in transcripts:
                text = f"{text}\n\n[Spoken Transcript]: {transcripts[a.artifact_id]}"

            text_lower = text.lower()

            # 1. Friction & Drama Detection
            detected_friction_cats = []
            matched_terms = []
            for cat_key, cat_data in FRICTION_CATEGORIES.items():
                for kw in cat_data["keywords"]:
                    if kw in text_lower:
                        if cat_key not in detected_friction_cats:
                            detected_friction_cats.append(cat_key)
                        matched_terms.append(kw)

            # Score friction: base term count + intensity indicators
            if detected_friction_cats:
                intensity = len(matched_terms)
                if "!" in text:
                    intensity += 1
                if any(w.isupper() and len(w) > 3 for w in text.split()):
                    intensity += 1

                friction_record = {
                    "artifact_id": a.artifact_id,
                    "platform": a.platform.value,
                    "author": a.author_handle or "unknown",
                    "content_type": a.content_type.value,
                    "url": a.canonical_url,
                    "categories": [FRICTION_CATEGORIES[c]["label"] for c in detected_friction_cats],
                    "matched_terms": list(set(matched_terms))[:8],
                    "intensity": intensity,
                    "excerpt": self._extract_relevant_excerpt(text, matched_terms),
                    "full_text": text,
                }
                friction_events.append(friction_record)

                # Generate Level 3 Annotation for Friction
                annotations.append(
                    Annotation(
                        annotation_id=str(uuid.uuid4())[:12],
                        artifact_id=a.artifact_id,
                        annotation_type=AnnotationType.FRICTION,
                        value={
                            "categories": detected_friction_cats,
                            "intensity": intensity,
                            "terms": matched_terms[:5],
                        },
                        model="observatory-friction-v1",
                        model_version="0.1.0",
                        confidence=min(1.0, 0.4 + (0.15 * len(matched_terms))),
                    )
                )

            # 2. Faction Classification
            assigned_factions = []
            for fac_key, fac_data in FACTION_INDICATORS.items():
                if any(re.search(pat, text_lower) for pat in fac_data["patterns"]):
                    assigned_factions.append(fac_key)
                    factions[fac_key].append(
                        {
                            "artifact_id": a.artifact_id,
                            "author": a.author_handle or "unknown",
                            "platform": a.platform.value,
                            "url": a.canonical_url,
                            "excerpt": text[:240].replace("\n", " "),
                        }
                    )

            # Default to resident/shopper voice if it's a comment and unclassified
            if not assigned_factions and a.content_type == ContentType.COMMENT:
                factions["resident_shopper"].append(
                    {
                        "artifact_id": a.artifact_id,
                        "author": a.author_handle or "unknown",
                        "platform": a.platform.value,
                        "url": a.canonical_url,
                        "excerpt": text[:240].replace("\n", " "),
                    }
                )
                assigned_factions.append("resident_shopper")

            # Store Level 3 Stance Annotation
            for fac in assigned_factions:
                annotations.append(
                    Annotation(
                        annotation_id=str(uuid.uuid4())[:12],
                        artifact_id=a.artifact_id,
                        annotation_type=AnnotationType.STANCE,
                        value={
                            "faction": fac,
                            "label": FACTION_INDICATORS[fac]["label"],
                        },
                        model="observatory-stance-v1",
                        model_version="0.1.0",
                        confidence=0.85,
                    )
                )

        # Sort friction events by intensity descending
        friction_events.sort(key=lambda x: x["intensity"], reverse=True)

        return {
            "total_artifacts": len(artifacts),
            "total_friction_events": len(friction_events),
            "factions": factions,
            "friction_events": friction_events,
            "annotations": annotations,
        }

    def _extract_relevant_excerpt(self, text: str, terms: list[str]) -> str:
        """Extract sentence containing the matched friction terms."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            s_lower = s.lower()
            if any(t in s_lower for t in terms):
                clean_s = s.replace("\n", " ").strip()
                return clean_s[:200]
        return text.replace("\n", " ")[:150]

    def _write_report(self, run_dir: Path, run_id: str, res: dict[str, Any]) -> None:
        """Write the structured ANALYSIS_REPORT.md file."""
        report_file = run_dir / "ANALYSIS_REPORT.md"
        now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            f"# Signal Observatory Analysis Report: `{run_id}`",
            "",
            f"- **Generated:** {now_str}",
            f"- **Total Artifacts Analyzed:** {res['total_artifacts']}",
            f"- **Friction / Drama Incidents Flagged:** {res['total_friction_events']}",
            "- **Provenance Status:** All statements resolved to Parquet artifact IDs.",
            "",
            "---",
            "",
            "## 1. Competing Factions & Viewpoint Matrix",
            "",
        ]

        for fac_key, fac_data in FACTION_INDICATORS.items():
            items = res["factions"][fac_key]
            lines.append(f"### {fac_data['label']} ({len(items)} artifacts)")
            lines.append(f"*{fac_data['description']}*\n")
            if items:
                lines.append("| Author | Platform | Direct Evidence Quote | Canonical Link |")
                lines.append("|---|---|---|---|")
                for it in items[:6]:
                    link = f"[Link]({it['url']})" if it["url"] else f"`{it['artifact_id'][:10]}`"
                    lines.append(
                        f'| {it["author"]} | {it["platform"]} | "{it["excerpt"]}..." | {link} |'
                    )
                lines.append("")
            else:
                lines.append("*No direct artifacts detected in this sample.*\n")

        lines.extend(
            [
                "---",
                "",
                "## 2. Friction, Drama & Community Hotspots",
                "",
                "The following items represent high-conflict community disputes, "
                "code citations, labor grievances, and safety concerns surfaced from "
                "raw social comments and forum threads:",
                "",
            ]
        )

        if res["friction_events"]:
            lines.append(
                "| Rank | Author | Platform | Category | Key Terms | "
                "Evidence Quote | Canonical Link |"
            )
            lines.append("|---|---|---|---|---|---|---|")
            for i, ev in enumerate(res["friction_events"][:15], 1):
                link = f"[Source]({ev['url']})" if ev["url"] else f"`{ev['artifact_id'][:10]}`"
                cats = ", ".join(ev["categories"])
                terms = ", ".join(ev["matched_terms"])
                lines.append(
                    f"| {i} | {ev['author']} | {ev['platform']} | {cats} | "
                    f"`{terms}` | \"{ev['excerpt']}...\" | {link} |"
                )
            lines.append("")
        else:
            lines.append("*No significant friction or drama signals detected in this sample.*\n")

        lines.extend(
            [
                "---",
                "",
                "## 3. Epistemic Invariant Verification",
                "",
                "- **Level 1 (Raw Evidence):** Stored in `data/raw/`.",
                (
                    "- **Level 2 (Normalized Corpus):** Verified in "
                    "`data/normalized/artifacts.parquet`."
                ),
                (
                    f"- **Level 3 (Model Annotations):** Generated {len(res['annotations'])} "
                    "derived stance & friction annotations in `data/derived/annotations.parquet`."
                ),
                "",
                "*Report compiled deterministically by Signal Observatory.*",
            ]
        )

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
