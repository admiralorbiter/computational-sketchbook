"""SQLite ledger storage implementation for experiments, runs, metrics, and tamper-evident events."""

import datetime
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    track TEXT NOT NULL,
    contract_id TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    config_sha256 TEXT NOT NULL,
    benchmark_version TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    instance_id TEXT NOT NULL,
    seed INTEGER,
    bit_length INTEGER NOT NULL,
    method TEXT NOT NULL,
    exit_code INTEGER NOT NULL,
    wall_seconds REAL NOT NULL,
    cpu_seconds REAL NOT NULL,
    peak_rss_mb REAL NOT NULL,
    timeout INTEGER NOT NULL,
    result_path TEXT NOT NULL,
    stdout_path TEXT,
    stderr_path TEXT,
    FOREIGN KEY(experiment_id) REFERENCES experiments(id)
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    metric_unit TEXT NOT NULL,
    metric_version TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    experiment_id TEXT,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_runs_experiment ON runs(experiment_id);
CREATE INDEX IF NOT EXISTS idx_metrics_run ON metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_events_experiment ON events(experiment_id);
"""


class LedgerDB:
    """Manages SQLite connection and operations for the immutable experimental ledger."""

    def __init__(self, db_path: Union[str, Path]):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self.conn:
            self.conn.executescript(SCHEMA_SQL)

    def close(self) -> None:
        """Close connection."""
        self.conn.close()

    def get_latest_event_hash(self) -> str:
        """Return the hash of the latest event or genesis zero hash."""
        cur = self.conn.cursor()
        cur.execute("SELECT event_hash FROM events ORDER BY event_id DESC LIMIT 1")
        row = cur.fetchone()
        return row["event_hash"] if row else "0" * 64

    def record_event(
        self,
        actor: str,
        event_type: str,
        payload: Dict[str, Any],
        experiment_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> str:
        """Append a tamper-evident event to the ledger."""
        ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        prev_hash = self.get_latest_event_hash()

        # Compute SHA-256 of chained event
        h = hashlib.sha256()
        h.update(prev_hash.encode("utf-8"))
        h.update(ts.encode("utf-8"))
        h.update(actor.encode("utf-8"))
        h.update(event_type.encode("utf-8"))
        h.update(payload_str.encode("utf-8"))
        event_hash = h.hexdigest()

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO events (timestamp, actor, experiment_id, event_type, payload_json, previous_hash, event_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (ts, actor, experiment_id, event_type, payload_str, prev_hash, event_hash),
            )
        return event_hash

    def insert_experiment(
        self,
        exp_id: str,
        track: str,
        contract_id: str,
        commit_sha: str,
        config_sha256: str,
        benchmark_version: str,
        status: str = "IDLE",
        parent_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        """Record a new experiment."""
        ts = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO experiments (id, parent_id, track, contract_id, commit_sha, config_sha256, benchmark_version, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (exp_id, parent_id, track, contract_id, commit_sha, config_sha256, benchmark_version, status, ts),
            )

    def update_experiment_status(
        self,
        exp_id: str,
        status: str,
        verdict: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> None:
        """Update status and verdict of an experiment."""
        updates = ["status = ?"]
        params = [status]
        if verdict is not None:
            updates.append("verdict = ?")
            params.append(verdict)
        if started_at is not None:
            updates.append("started_at = ?")
            params.append(started_at)
        if completed_at is not None:
            updates.append("completed_at = ?")
            params.append(completed_at)
        params.append(exp_id)

        query = f"UPDATE experiments SET {', '.join(updates)} WHERE id = ?"
        with self.conn:
            self.conn.execute(query, params)

    def insert_run(
        self,
        run_id: str,
        experiment_id: str,
        instance_id: str,
        bit_length: int,
        method: str,
        exit_code: int = 0,
        wall_seconds: float = 0.0,
        cpu_seconds: float = 0.0,
        peak_rss_mb: float = 0.0,
        timeout: bool = False,
        seed: Optional[int] = None,
        result_path: str = "",
        stdout_path: Optional[str] = None,
        stderr_path: Optional[str] = None,
    ) -> None:
        """Record an individual execution run in the ledger."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO runs (run_id, experiment_id, instance_id, seed, bit_length, method, exit_code, wall_seconds, cpu_seconds, peak_rss_mb, timeout, result_path, stdout_path, stderr_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    experiment_id,
                    instance_id,
                    seed,
                    bit_length,
                    method,
                    exit_code,
                    wall_seconds,
                    cpu_seconds,
                    peak_rss_mb,
                    1 if timeout else 0,
                    result_path,
                    stdout_path,
                    stderr_path,
                ),
            )

    def insert_metric(
        self,
        run_id: str,
        metric_name: str,
        metric_value: Optional[float],
        metric_unit: str = "count",
        metric_version: str = "v1.0",
    ) -> None:
        """Record a primary or secondary scientific metric for a run."""
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO metrics (run_id, metric_name, metric_value, metric_unit, metric_version)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, metric_name, metric_value, metric_unit, metric_version),
            )


ExperimentLedger = LedgerDB

