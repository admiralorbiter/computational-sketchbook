from observatory.signals import SignalTournamentStore
from observatory.models import SignalConfidence, Platform

store = SignalTournamentStore()

# Signal 13: Research Foundation Harmonization
s1 = store.freeze_signal(
    phenomenon="KU Cross-Campus Research Administration Harmonization Squeeze",
    observation="Lawrence (KUCR) and KUMC RI operate under separate federal EINs, indirect cost rates, and financial systems, requiring cumbersome formal subawards for cross-campus biomedical collaboration while 'One KU' pushes operational centralization",
    hypothesis="Under 'One KU' alignment pressure or KBOR directive, KU leadership will formally initiate a consolidation or uniform overhead framework between KUCR and KUMC Research Institute within 180 days",
    evidence_artifact_ids=[
        "00d945b4e7fa68028b80a4724073de025232ac95809e70a82cc25551249894a9",
        "270e46e1a7d787e5e9c9dca7b17608146202eef7ef63f729f051e9134b28c074"
    ],
    creator_count=2,
    platforms=[Platform.WEB],
    confidence=SignalConfidence.MODERATE,
    verification_days=180
)
print(f"Frozen: {s1.signal_id} - {s1.phenomenon}")

# Signal 14: Liberty Hospital Cross-Border Challenge
s2 = store.freeze_signal(
    phenomenon="UKHS-Liberty Hospital Cross-Border Governance and Tax Exemption Litigation",
    observation="UKHS completed its acquisition of Missouri's Liberty Hospital despite opposition from MO Attorney General Bailey, creating unprecedented friction over a Kansas state public authority operating a Missouri political subdivision",
    hypothesis="A Missouri healthcare competitor (Saint Luke's/BJC or North Kansas City Hospital) or Missouri state agency will file formal litigation challenging UKHS tax exemptions or public authority jurisdiction in Clay County within 120 days",
    evidence_artifact_ids=[
        "be7cbea6c37ae0a542650f0b1021e838e121bff99775e5e801c5daabc3653f80",
        "2c6e45c586972d68c7881cd29ba923e4cf1872e392e93fddb90e21c549547d69"
    ],
    creator_count=3,
    platforms=[Platform.WEB, Platform.REDDIT],
    confidence=SignalConfidence.HIGH,
    verification_days=120
)
print(f"Frozen: {s2.signal_id} - {s2.phenomenon}")

# Signal 15: Lawrence Governance Revolt & External Audit Mandate
s3 = store.freeze_signal(
    phenomenon="KU Lawrence Faculty Governance Revolt and Gateway Athletic Audit Mandate",
    observation="Nearly 80% of faculty and staff voted 'no confidence' in Chancellor Douglas Girod and CFO Jeff DeWitt over $400M+ Gateway District stadium spending while academic programs face austerity and union contract impasses",
    hypothesis="The KU Faculty Senate, University Senate, or Kansas Board of Regents will formally commission an external forensic audit of Gateway District athletic debt and internal fund allocations within 90 days",
    evidence_artifact_ids=[
        "2764729da5bb9294b0f8d75e95c6d843b0c176cf079ca58c1cd87f2793b3ec4c",
        "85bde3474234aa8a022c1e08cedc3f4e0d6ad27ca7e418d16427004408832d16"
    ],
    creator_count=4,
    platforms=[Platform.WEB, Platform.REDDIT],
    confidence=SignalConfidence.HIGH,
    verification_days=90
)
print(f"Frozen: {s3.signal_id} - {s3.phenomenon}")
