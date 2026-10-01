"""Corpus store — DuckDB/Parquet-backed evidence repository.

The corpus provides append-only storage for artifacts and annotations.
Raw API responses are stored as JSONL files; normalized records are
written to Parquet for analytical querying via DuckDB.

Design principles:
- Raw data is immutable once written
- Artifacts deduplicate naturally via deterministic IDs
- Annotations are always attributed and stored separately
- DuckDB reads Parquet directly — no import step needed
"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import orjson
import polars as pl

from observatory.config import Settings, get_settings
from observatory.models import Annotation, Artifact


class CorpusStore:
    """Manages the evidence corpus on disk.

    Provides methods to:
    - Store raw API responses (immutable JSONL)
    - Store normalized artifacts (Parquet, deduplicating)
    - Store annotations (Parquet, append-only)
    - Query the corpus via DuckDB SQL
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.settings.ensure_directories()

    def store_raw(
        self,
        records: list[dict[str, Any]],
        *,
        platform: str,
        query_id: str,
    ) -> Path:
        """Store raw API responses as immutable JSONL.

        Args:
            records: Raw API response records.
            platform: Platform name for directory organization.
            query_id: Query identifier for filename.

        Returns:
            Path to the written JSONL file.
        """
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        raw_dir = self.settings.raw_dir / platform / today
        raw_dir.mkdir(parents=True, exist_ok=True)

        filepath = raw_dir / f"query_{query_id}.jsonl"

        with open(filepath, "ab") as f:
            for record in records:
                f.write(orjson.dumps(record))
                f.write(b"\n")

        return filepath

    def store_artifacts(self, artifacts: list[Artifact]) -> int:
        """Store normalized artifacts to Parquet, deduplicating by artifact_id.

        Args:
            artifacts: List of normalized Artifact objects.

        Returns:
            Number of new artifacts added (after dedup).
        """
        if not artifacts:
            return 0

        # Convert to records
        records = []
        eng_snapshots = []
        for a in artifacts:
            record = a.model_dump(mode="json")
            record["artifact_id"] = a.artifact_id
            record["published_at_quality"] = (
                a.published_at_quality.value
                if hasattr(a, "published_at_quality")
                else "unknown"
            )
            # Flatten engagement for Parquet compatibility
            eng = record.pop("engagement", None) or {}
            record["engagement_likes"] = eng.get("likes", 0)
            record["engagement_reposts"] = eng.get("reposts", 0)
            record["engagement_replies"] = eng.get("replies", 0)
            record["engagement_views"] = eng.get("views")
            records.append(record)

            if a.engagement is not None:
                snap_id = hashlib.sha256(
                    f"{a.artifact_id}:{a.engagement.observed_at.isoformat()}".encode()
                ).hexdigest()[:16]
                eng_snapshots.append(
                    {
                        "snapshot_id": snap_id,
                        "artifact_id": a.artifact_id,
                        "platform": a.platform.value,
                        "observed_at": a.engagement.observed_at.isoformat(),
                        "likes": a.engagement.likes,
                        "reposts": a.engagement.reposts,
                        "replies": a.engagement.replies,
                        "views": a.engagement.views,
                    }
                )

        if eng_snapshots:
            self.store_engagement_snapshots(eng_snapshots)

        new_df = pl.DataFrame(records)

        artifacts_path = self.settings.normalized_dir / "artifacts.parquet"

        if artifacts_path.exists():
            existing_df = pl.read_parquet(artifacts_path)
            existing_ids = set(existing_df["artifact_id"].to_list())
            new_df = new_df.filter(~pl.col("artifact_id").is_in(existing_ids))

            if new_df.height == 0:
                return 0

            combined = pl.concat([existing_df, new_df], how="diagonal_relaxed")
            combined.write_parquet(artifacts_path, compression="zstd")
            return new_df.height
        else:
            new_df.write_parquet(artifacts_path, compression="zstd")
            return new_df.height

    def store_engagement_snapshots(self, records: list[dict[str, Any]]) -> int:
        """Append point-in-time engagement observations to snapshots Parquet.

        Args:
            records: List of raw snapshot record dictionaries.

        Returns:
            Number of snapshots recorded.
        """
        if not records:
            return 0

        new_df = pl.DataFrame(records)
        snap_path = self.settings.normalized_dir / "engagement_snapshots.parquet"

        if snap_path.exists():
            existing_df = pl.read_parquet(snap_path)
            existing_ids = set(existing_df["snapshot_id"].to_list())
            new_df = new_df.filter(~pl.col("snapshot_id").is_in(existing_ids))
            if new_df.height == 0:
                return 0
            combined = pl.concat([existing_df, new_df], how="diagonal_relaxed")
            combined.write_parquet(snap_path, compression="zstd")
            return new_df.height
        else:
            new_df.write_parquet(snap_path, compression="zstd")
            return new_df.height

    def calculate_virality_physics(self, artifact_id: str) -> dict[str, Any]:
        """Compute engagement velocity and acceleration for an artifact.

        Velocity: v(t) = Delta engagement / Delta t (hours)
        Acceleration: a(t) = Delta v / Delta t
        """
        snap_path = self.settings.normalized_dir / "engagement_snapshots.parquet"
        if not snap_path.exists():
            return {"artifact_id": artifact_id, "snapshots": 0}

        df = pl.read_parquet(snap_path)
        filtered = df.filter(pl.col("artifact_id") == artifact_id).sort("observed_at")
        if filtered.height == 0:
            return {"artifact_id": artifact_id, "snapshots": 0}

        records = filtered.to_dicts()
        if len(records) == 1:
            return {
                "artifact_id": artifact_id,
                "snapshots": 1,
                "current_likes": records[0]["likes"],
                "current_views": records[0]["views"],
                "velocity_engagement_per_hour": 0.0,
                "acceleration_engagement": 0.0,
            }

        velocities = []
        for i in range(1, len(records)):
            t0 = datetime.fromisoformat(records[i - 1]["observed_at"])
            t1 = datetime.fromisoformat(records[i]["observed_at"])
            dt_hours = max((t1 - t0).total_seconds() / 3600.0, 0.001)

            v0 = records[i - 1].get("views") or records[i - 1].get("likes") or 0
            v1 = records[i].get("views") or records[i].get("likes") or 0
            vel = (v1 - v0) / dt_hours
            velocities.append((dt_hours, vel))

        latest_vel = velocities[-1][1]
        accel = 0.0
        if len(velocities) >= 2:
            dt = velocities[-1][0]
            accel = (velocities[-1][1] - velocities[-2][1]) / dt

        return {
            "artifact_id": artifact_id,
            "snapshots": len(records),
            "current_likes": records[-1]["likes"],
            "current_views": records[-1]["views"],
            "velocity_engagement_per_hour": round(latest_vel, 2),
            "acceleration_engagement": round(accel, 2),
            "history": records,
        }

    def store_annotations(self, annotations: list[Annotation]) -> int:
        """Append annotations to the annotations Parquet file.

        Args:
            annotations: List of Annotation objects.

        Returns:
            Number of annotations stored.
        """
        if not annotations:
            return 0

        records = [a.model_dump(mode="json") for a in annotations]
        new_df = pl.DataFrame(records)

        annotations_path = self.settings.derived_dir / "annotations.parquet"

        if annotations_path.exists():
            existing_df = pl.read_parquet(annotations_path)
            combined = pl.concat([existing_df, new_df], how="diagonal_relaxed")
            combined.write_parquet(annotations_path, compression="zstd")
        else:
            new_df.write_parquet(annotations_path, compression="zstd")

        return len(annotations)

    def query(self, sql: str) -> pl.DataFrame:
        """Execute a DuckDB SQL query against the corpus.

        The query can reference Parquet files using glob patterns.
        Common table aliases are set up automatically.

        Args:
            sql: SQL query string.

        Returns:
            Query results as a Polars DataFrame.
        """
        con = duckdb.connect()

        # Register common paths as views for convenience
        artifacts_path = self.settings.normalized_dir / "artifacts.parquet"
        annotations_path = self.settings.derived_dir / "annotations.parquet"

        if artifacts_path.exists():
            con.execute(f"CREATE VIEW artifacts AS SELECT * FROM '{artifacts_path}'")
        if annotations_path.exists():
            con.execute(f"CREATE VIEW annotations AS SELECT * FROM '{annotations_path}'")

        result = con.execute(sql).pl()
        con.close()
        return result

    def corpus_stats(self) -> dict[str, Any]:
        """Get summary statistics for the corpus.

        Returns:
            Dictionary with counts and metadata about the corpus.
        """
        stats: dict[str, Any] = {
            "artifacts": 0,
            "annotations": 0,
            "platforms": [],
            "date_range": None,
        }

        artifacts_path = self.settings.normalized_dir / "artifacts.parquet"
        if artifacts_path.exists():
            df = pl.read_parquet(artifacts_path)
            stats["artifacts"] = df.height
            stats["platforms"] = df["platform"].unique().sort().to_list()
            if "published_at" in df.columns:
                dates = df["published_at"].drop_nulls()
                if dates.len() > 0:
                    stats["date_range"] = {
                        "earliest": str(dates.min()),
                        "latest": str(dates.max()),
                    }

        annotations_path = self.settings.derived_dir / "annotations.parquet"
        if annotations_path.exists():
            df = pl.read_parquet(annotations_path)
            stats["annotations"] = df.height

        return stats
