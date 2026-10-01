from observatory.signals import SignalTournamentStore
from observatory.models import SignalConfidence, Platform
import duckdb

con = duckdb.connect()
rows = con.execute("""
    SELECT artifact_id, canonical_url 
    FROM 'data/normalized/artifacts.parquet' 
    WHERE run_id = 'run_2026-10-kumed-grants-townhalls'
""").fetchall()

evidence_ids = [r[0] for r in rows[:3]]

store = SignalTournamentStore()

s4 = store.freeze_signal(
    phenomenon="Federal Research Indirect Cost (F&A) Squeeze and Congressional NIH Intervention",
    observation="KU experienced a $182M year-over-year drop in new research awards due to federal NIH disbursement bottlenecks, prompting Chancellor Girod's WSJ op-ed and Rep. Sharice Davids' 39-member congressional inquiry to HHS Secretary RFK Jr.",
    hypothesis="Congressional oversight hearings or formal HHS administrative policy revisions will mandate an expedited release of delayed NIH extramural grants and formally reject proposed caps on university F&A indirect cost recovery within 120 days",
    evidence_artifact_ids=evidence_ids,
    creator_count=3,
    platforms=[Platform.WEB],
    confidence=SignalConfidence.HIGH,
    verification_days=120
)
print(f"Frozen: {s4.signal_id} - {s4.phenomenon}")
