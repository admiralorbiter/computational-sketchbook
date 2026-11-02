"""Signal Tournament Engine — prospective weak signal freezing and calibration.

Enforces the core epistemic discipline:
Nominate candidate weak signals BEFORE knowing the outcome.
Freeze observation, evidence, hypothesis, confidence, and timestamp immutably.
Verify 14 or 30 days later without rewriting past embarrassments.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import polars as pl

from observatory.config import Settings, get_settings
from observatory.models import (
    FrozenSignal,
    Platform,
    SignalConfidence,
    SignalStatus,
)


class SignalTournamentStore:
    """Manages frozen weak signals and tournament scorecard tracking."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.signals_dir = self.settings.data_dir / "signals"
        self.cards_dir = self.signals_dir / "cards"
        self.signals_parquet = self.signals_dir / "signals.parquet"

        self.signals_dir.mkdir(parents=True, exist_ok=True)
        self.cards_dir.mkdir(parents=True, exist_ok=True)

    def get_next_signal_id(self, year: int | None = None) -> str:
        """Generate next sequential ID in format SIGNAL-YYYY-NNNN."""
        cur_year = year or datetime.now(UTC).year
        prefix = f"SIGNAL-{cur_year}-"

        if not self.signals_parquet.exists():
            return f"{prefix}0001"

        df = pl.read_parquet(self.signals_parquet)
        if df.height == 0 or "signal_id" not in df.columns:
            return f"{prefix}0001"

        matching = [
            sid for sid in df["signal_id"].to_list()
            if isinstance(sid, str) and sid.startswith(prefix)
        ]
        if not matching:
            return f"{prefix}0001"

        numbers = []
        for sid in matching:
            try:
                num = int(sid.split("-")[-1])
                numbers.append(num)
            except ValueError:
                continue

        next_num = max(numbers, default=0) + 1
        return f"{prefix}{next_num:04d}"

    def freeze_signal(
        self,
        phenomenon: str,
        observation: str,
        hypothesis: str,
        evidence_artifact_ids: list[str],
        *,
        creator_count: int = 1,
        platforms: list[Platform] | None = None,
        confidence: SignalConfidence = SignalConfidence.MODERATE,
        verification_days: int = 14,
        signal_id: str | None = None,
    ) -> FrozenSignal:
        """Freeze a prospective signal candidate immutably into the tournament."""
        now = datetime.now(UTC)
        sid = signal_id or self.get_next_signal_id(now.year)
        deadline = now + timedelta(days=verification_days)

        signal = FrozenSignal(
            signal_id=sid,
            phenomenon=phenomenon,
            observation=observation,
            evidence_artifact_ids=evidence_artifact_ids,
            creator_count=creator_count,
            platforms=platforms or [],
            hypothesis=hypothesis,
            confidence=confidence,
            verification_days=verification_days,
            detected_at=now,
            frozen_at=now,
            verification_deadline=deadline,
            status=SignalStatus.PENDING,
        )
        signal.freeze_hash = signal.compute_freeze_hash()

        # Save to Parquet
        self._append_or_update_parquet(signal)

        # Write human-readable Markdown card
        self._write_signal_card(signal)

        return signal

    def resolve_signal(
        self,
        signal_id: str,
        status: SignalStatus,
        notes: str,
        verifying_artifact_ids: list[str] | None = None,
    ) -> FrozenSignal:
        """Resolve a previously frozen candidate signal with empirical outcome."""
        if status == SignalStatus.PENDING:
            raise ValueError("Cannot resolve a signal to PENDING status")

        signal = self.get_signal(signal_id)
        if not signal:
            raise KeyError(f"Signal {signal_id} not found in tournament store")

        now = datetime.now(UTC)
        signal.status = status
        signal.resolved_at = now
        signal.resolution_notes = notes
        if verifying_artifact_ids:
            signal.verifying_artifact_ids = verifying_artifact_ids

        # Update in Parquet
        self._append_or_update_parquet(signal)

        # Update card
        self._write_signal_card(signal)

        return signal

    def get_signal(self, signal_id: str) -> FrozenSignal | None:
        """Fetch a specific frozen signal by ID."""
        if not self.signals_parquet.exists():
            return None

        df = pl.read_parquet(self.signals_parquet)
        matched = df.filter(pl.col("signal_id") == signal_id)
        if matched.height == 0:
            return None

        row = matched.to_dicts()[0]
        return self._dict_to_signal(row)

    def list_signals(self, status: SignalStatus | None = None) -> list[FrozenSignal]:
        """List all frozen signals, optionally filtered by status."""
        if not self.signals_parquet.exists():
            return []

        df = pl.read_parquet(self.signals_parquet)
        if df.height == 0:
            return []

        if status:
            df = df.filter(pl.col("status") == status.value)

        signals = [self._dict_to_signal(row) for row in df.to_dicts()]
        return sorted(signals, key=lambda s: s.frozen_at, reverse=True)

    def scorecard(self) -> dict[str, Any]:
        """Compute tournament performance scorecard and calibration metrics."""
        signals = self.list_signals()
        if not signals:
            return {
                "total_frozen": 0,
                "pending": 0,
                "evaluated": 0,
                "hits": 0,
                "misses": 0,
                "partials": 0,
                "unverifiable": 0,
                "hit_rate": 0.0,
                "brier_score": None,
                "mean_lead_time_hours": None,
                "confidence_breakdown": {},
            }

        counts = {
            SignalStatus.PENDING: 0,
            SignalStatus.HIT: 0,
            SignalStatus.MISS: 0,
            SignalStatus.PARTIAL: 0,
            SignalStatus.UNVERIFIABLE: 0,
        }
        for s in signals:
            counts[s.status] = counts.get(s.status, 0) + 1

        evaluated = (
            counts[SignalStatus.HIT]
            + counts[SignalStatus.MISS]
            + counts[SignalStatus.PARTIAL]
        )
        hit_points = counts[SignalStatus.HIT] + (0.5 * counts[SignalStatus.PARTIAL])
        hit_rate = (hit_points / evaluated) if evaluated > 0 else 0.0

        # Confidence breakdown & Brier score
        prob_map = {
            SignalConfidence.LOW: 0.25,
            SignalConfidence.MODERATE: 0.60,
            SignalConfidence.HIGH: 0.85,
        }
        brier_sum = 0.0
        conf_breakdown: dict[str, dict[str, Any]] = {}

        for tier in SignalConfidence:
            tier_signals = [s for s in signals if s.confidence == tier]
            tier_eval = [
                s for s in tier_signals
                if s.status in (SignalStatus.HIT, SignalStatus.MISS, SignalStatus.PARTIAL)
            ]
            t_hits = sum(1 for s in tier_eval if s.status == SignalStatus.HIT)
            t_partials = sum(1 for s in tier_eval if s.status == SignalStatus.PARTIAL)
            t_misses = sum(1 for s in tier_eval if s.status == SignalStatus.MISS)
            t_rate = ((t_hits + 0.5 * t_partials) / len(tier_eval)) if tier_eval else 0.0

            conf_breakdown[tier.value] = {
                "total": len(tier_signals),
                "evaluated": len(tier_eval),
                "hits": t_hits,
                "partials": t_partials,
                "misses": t_misses,
                "hit_rate": round(t_rate, 3),
            }

            for s in tier_eval:
                prob = prob_map.get(s.confidence, 0.5)
                if s.status == SignalStatus.HIT:
                    outcome = 1.0
                elif s.status == SignalStatus.PARTIAL:
                    outcome = 0.5
                else:
                    outcome = 0.0
                brier_sum += (prob - outcome) ** 2

        brier_score = round(brier_sum / evaluated, 4) if evaluated > 0 else None

        # Mean lead time calculation for hits
        lead_times_hours = []
        for s in signals:
            if s.status == SignalStatus.HIT and s.resolved_at:
                lt = (s.resolved_at - s.frozen_at).total_seconds() / 3600.0
                lead_times_hours.append(lt)

        mean_lt = (
            round(sum(lead_times_hours) / len(lead_times_hours), 2)
            if lead_times_hours
            else None
        )

        return {
            "total_frozen": len(signals),
            "pending": counts[SignalStatus.PENDING],
            "evaluated": evaluated,
            "hits": counts[SignalStatus.HIT],
            "misses": counts[SignalStatus.MISS],
            "partials": counts[SignalStatus.PARTIAL],
            "unverifiable": counts[SignalStatus.UNVERIFIABLE],
            "hit_rate": round(hit_rate, 3),
            "brier_score": brier_score,
            "mean_lead_time_hours": mean_lt,
            "confidence_breakdown": conf_breakdown,
        }

    def _append_or_update_parquet(self, signal: FrozenSignal) -> None:
        """Write signal record to Parquet atomically."""
        record = {
            "signal_id": signal.signal_id,
            "phenomenon": signal.phenomenon,
            "observation": signal.observation,
            "evidence_artifact_ids": signal.evidence_artifact_ids,
            "creator_count": signal.creator_count,
            "platforms": [p.value if hasattr(p, "value") else str(p) for p in signal.platforms],
            "hypothesis": signal.hypothesis,
            "confidence": signal.confidence.value,
            "verification_days": signal.verification_days,
            "detected_at": signal.detected_at.isoformat(),
            "frozen_at": signal.frozen_at.isoformat(),
            "verification_deadline": (
                signal.verification_deadline.isoformat()
                if signal.verification_deadline
                else None
            ),
            "freeze_hash": signal.freeze_hash,
            "status": signal.status.value,
            "resolved_at": signal.resolved_at.isoformat() if signal.resolved_at else None,
            "resolution_notes": signal.resolution_notes or "",
            "verifying_artifact_ids": signal.verifying_artifact_ids,
        }

        new_df = pl.DataFrame([record])

        if self.signals_parquet.exists():
            existing_df = pl.read_parquet(self.signals_parquet)
            filtered_df = existing_df.filter(pl.col("signal_id") != signal.signal_id)
            combined = pl.concat([filtered_df, new_df], how="diagonal_relaxed")
            combined.write_parquet(self.signals_parquet, compression="zstd")
        else:
            new_df.write_parquet(self.signals_parquet, compression="zstd")

    def _write_signal_card(self, signal: FrozenSignal) -> Path:
        """Write an immutable human-readable Markdown audit card."""
        card_file = self.cards_dir / f"{signal.signal_id}.md"

        platforms_str = ", ".join(
            p.value if hasattr(p, "value") else str(p) for p in signal.platforms
        ) or "None recorded"
        evidence_str = "\n".join(f"- `{aid}`" for aid in signal.evidence_artifact_ids)

        ver_str = (
            "\n".join(f"- `{aid}`" for aid in signal.verifying_artifact_ids)
            if signal.verifying_artifact_ids
            else "_None registered_"
        )

        deadline_str = (
            signal.verification_deadline.strftime("%Y-%m-%d %H:%M:%S UTC")
            if signal.verification_deadline
            else "N/A"
        )
        resolved_str = (
            signal.resolved_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            if signal.resolved_at
            else "_Pending verification_"
        )

        content = (
            f"# {signal.signal_id} — Prospective Signal Record\n\n"
            f"- **Phenomenon:** {signal.phenomenon}\n"
            f"- **Status:** `{signal.status.value.upper()}`\n"
            f"- **Confidence:** `{signal.confidence.value.upper()}`\n"
            f"- **Frozen:** {signal.frozen_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"- **Verification Deadline:** {deadline_str}\n"
            f"- **Tamper-Evident SHA-256:** `{signal.freeze_hash}`\n\n"
            f"---\n\n"
            f"### Observation\n{signal.observation}\n\n"
            f"### Hypothesis\n{signal.hypothesis}\n\n"
            f"### Empirical Evidence Frozen at Detection\n"
            f"- **Independent Creators:** {signal.creator_count}\n"
            f"- **Platforms Involved:** {platforms_str}\n"
            f"- **Artifact Evidence IDs:**\n{evidence_str}\n\n"
            f"---\n\n"
            f"### Resolution & Audit\n"
            f"- **Outcome:** `{signal.status.value.upper()}`\n"
            f"- **Resolved At:** {resolved_str}\n"
            f"- **Resolution Notes:** {signal.resolution_notes or '_No notes recorded_'}\n"
            f"- **Verifying Artifacts:**\n{ver_str}\n"
        )
        card_file.write_text(content, encoding="utf-8")
        return card_file

    def _dict_to_signal(self, row: dict[str, Any]) -> FrozenSignal:
        """Convert a Parquet dict row back into FrozenSignal model."""
        platforms = [Platform(p) for p in row.get("platforms") or []]
        return FrozenSignal(
            signal_id=row["signal_id"],
            phenomenon=row["phenomenon"],
            observation=row["observation"],
            evidence_artifact_ids=list(row.get("evidence_artifact_ids") or []),
            creator_count=row.get("creator_count", 1),
            platforms=platforms,
            hypothesis=row["hypothesis"],
            confidence=SignalConfidence(row.get("confidence", "moderate")),
            verification_days=row.get("verification_days", 14),
            detected_at=datetime.fromisoformat(row["detected_at"]),
            frozen_at=datetime.fromisoformat(row["frozen_at"]),
            verification_deadline=(
                datetime.fromisoformat(row["verification_deadline"])
                if row.get("verification_deadline")
                else None
            ),
            freeze_hash=row.get("freeze_hash", ""),
            status=SignalStatus(row.get("status", "pending")),
            resolved_at=(
                datetime.fromisoformat(row["resolved_at"])
                if row.get("resolved_at")
                else None
            ),
            resolution_notes=row.get("resolution_notes"),
            verifying_artifact_ids=list(row.get("verifying_artifact_ids") or []),
        )
