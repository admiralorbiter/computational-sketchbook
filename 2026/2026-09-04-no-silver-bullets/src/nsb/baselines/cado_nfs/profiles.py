"""Parameter profiles for CADO-NFS baseline integration.

Provides:
1. CadoParameterProfile: Structured container for polynomial selection,
   scoring, and sieving parameters.
2. CADO_PARAMS_C60: Exact pinned CADO profile from parameters/factor/params.c60
   at commit 73ca6b6847118b05b15eeec27c86f45cef82a19e.
3. CANARY_PLUMBING_C60: Custom high-yield profile reserved exclusively for
   fast adapter plumbing and smoke canary verification.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class CadoParameterProfile:
    """Explicit parameters governing CADO polyselect, scoring, and sieving."""

    name: str
    target_digits: int
    degree: int
    p_val: int
    nq: int
    nrkeep: int
    ropteffort: float
    admin: int
    admax: int
    adrange: int
    incr: int
    i_param: int
    lim0: int
    lim1: int
    lpb0: int
    lpb1: int
    mfb0: int
    mfb1: int
    ncurves0: int
    ncurves1: int
    qmin: int
    qrange: int
    bf: int
    bg: int
    area: float
    sqside: int = 1
    lambda0: Optional[float] = None
    lambda1: Optional[float] = None
    keep: Optional[int] = None
    notes: str = ""

    def to_sieve_dict(self) -> Dict[str, Any]:
        """Return complete frozen dictionary of relation collection and sieving parameters."""
        d = {
            "profile_name": self.name,
            "target_digits": self.target_digits,
            "i_param": self.i_param,
            "lim0": self.lim0,
            "lim1": self.lim1,
            "lpb0": self.lpb0,
            "lpb1": self.lpb1,
            "mfb0": self.mfb0,
            "mfb1": self.mfb1,
            "ncurves0": self.ncurves0,
            "ncurves1": self.ncurves1,
            "sqside": self.sqside,
            "qmin": self.qmin,
            "qrange": self.qrange,
        }
        if self.lambda0 is not None:
            d["lambda0"] = self.lambda0
        if self.lambda1 is not None:
            d["lambda1"] = self.lambda1
        return d

    @property
    def expected_area(self) -> float:
        """Derive scoring area: 2^(2*I - 1) * qmin."""
        return float((1 << (2 * self.i_param - 1)) * self.qmin)

    @property
    def expected_bf(self) -> int:
        """Derive algebraic side bound: 2^lpb1."""
        return 1 << self.lpb1

    @property
    def expected_bg(self) -> int:
        """Derive rational side bound: 2^lpb0."""
        return 1 << self.lpb0

    def to_full_dict(self) -> Dict[str, Any]:
        """Return complete dictionary of all polyselect, scoring, and sieving parameters."""
        d = {
            "name": self.name,
            "target_digits": self.target_digits,
            "degree": self.degree,
            "p_val": self.p_val,
            "nq": self.nq,
            "nrkeep": self.nrkeep,
            "ropteffort": self.ropteffort,
            "admin": self.admin,
            "admax": self.admax,
            "adrange": self.adrange,
            "incr": self.incr,
            "i_param": self.i_param,
            "lim0": self.lim0,
            "lim1": self.lim1,
            "lpb0": self.lpb0,
            "lpb1": self.lpb1,
            "mfb0": self.mfb0,
            "mfb1": self.mfb1,
            "ncurves0": self.ncurves0,
            "ncurves1": self.ncurves1,
            "qmin": self.qmin,
            "qrange": self.qrange,
            "bf": self.bf,
            "bg": self.bg,
            "area": self.area,
            "sqside": self.sqside,
            "keep": self.keep,
            "notes": self.notes,
        }
        if self.lambda0 is not None:
            d["lambda0"] = self.lambda0
        if self.lambda1 is not None:
            d["lambda1"] = self.lambda1
        return d


# 1. Exact pinned CADO c60 profile from parameters/factor/params.c60
# Pinned git commit: 73ca6b6847118b05b15eeec27c86f45cef82a19e
# In CADO source: parameters/factor/params.c60
# Derivations:
#   Bf = 2^lpb1 = 2^19 = 524288
#   Bg = 2^lpb0 = 2^18 = 262144
#   area = 2^(2*I - 1) * qmin = 2^19 * 61961 = 32485408768
CADO_PARAMS_C60 = CadoParameterProfile(
    name="c60_pinned",
    target_digits=60,
    degree=4,
    p_val=420,
    nq=64,
    nrkeep=10,
    ropteffort=0.1,
    admin=0,
    admax=10000,
    adrange=5000,
    incr=60,
    i_param=10,
    lim0=78682,
    lim1=111342,
    lpb0=18,
    lpb1=19,
    mfb0=17,
    mfb1=38,
    ncurves0=2,
    ncurves1=2,
    qmin=61961,
    qrange=2000,
    bf=524288,      # 2^19
    bg=262144,      # 2^18
    area=32485408768.0,  # 2^19 * 61961
    sqside=1,
    notes=(
        "Exact pinned CADO-NFS c60 profile from parameters/factor/params.c60: "
        "degree=4, P=420, nq=64, ropteffort=0.1, I=10, lim0=78682, lim1=111342, "
        "lpb0=18, lpb1=19, mfb0=17, mfb1=38, ncurves0=2, ncurves1=2, qmin=61961, qrange=2000, "
        "Bf=524288 (2^19), Bg=262144 (2^18), area=32485408768 (2^19 * 61961)."
    ),
)

# 2. Custom plumbing canary profile
# Rationale: Provides artificially widened factor bases (500k/1M) and larger
# bounds for rapid short-interval relation generation during CI and environment canaries.
# Must NOT be described as seeded from params.c60.
CANARY_PLUMBING_C60 = CadoParameterProfile(
    name="canary_plumbing_c60",
    target_digits=60,
    degree=5,
    p_val=420,
    nq=1000,
    nrkeep=10,
    ropteffort=5.0,
    admin=0,
    admax=10000,
    adrange=10000,
    incr=60,
    i_param=11,
    lim0=500000,
    lim1=1000000,
    lpb0=22,
    lpb1=22,
    mfb0=44,
    mfb1=44,
    ncurves0=2,
    ncurves1=2,
    qmin=500000,
    qrange=200,
    bf=4194304,          # 2^22
    bg=4194304,          # 2^22
    area=1048576000000.0, # 2^21 * 500000
    sqside=1,
    notes="Custom widened plumbing canary profile for high relation yield on micro intervals.",
)

# 3. Exact pinned CADO c70 profile from parameters/factor/params.c70
CADO_PARAMS_C70 = CadoParameterProfile(
    name="c70_pinned",
    target_digits=70,
    degree=4,
    p_val=1800,
    nq=64,
    nrkeep=20,
    ropteffort=0.1,
    admin=0,
    admax=44000,
    adrange=22000,
    incr=60,
    i_param=11,
    lim0=343245,
    lim1=244248,
    lpb0=20,
    lpb1=21,
    mfb0=19,
    mfb1=42,
    ncurves0=16,
    ncurves1=14,
    qmin=18640,
    qrange=1000,
    bf=2097152,          # 2^21
    bg=1048576,          # 2^20
    area=39090913280.0,  # 2^21 * 18640
    sqside=1,
    notes="Exact pinned CADO-NFS c70 profile from parameters/factor/params.c70.",
)

# 4. Exact pinned CADO c80 profile from parameters/factor/params.c80
CADO_PARAMS_C80 = CadoParameterProfile(
    name="c80_pinned",
    target_digits=80,
    degree=4,
    p_val=10000,
    nq=64,
    nrkeep=20,
    ropteffort=0.1,
    admin=0,
    admax=100000,
    adrange=5000,
    incr=60,
    i_param=11,
    lim0=292877,
    lim1=339976,
    lpb0=21,
    lpb1=21,
    mfb0=41,
    mfb1=42,
    ncurves0=8,
    ncurves1=8,
    qmin=66606,
    qrange=5000,
    bf=2097152,           # 2^21
    bg=2097152,           # 2^21
    area=139682906112.0,  # 2^21 * 66606
    sqside=1,
    notes="Exact pinned CADO-NFS c80 profile from parameters/factor/params.c80.",
)

# 5. Exact pinned CADO c90 profile from parameters/factor/params.c90
CADO_PARAMS_C90 = CadoParameterProfile(
    name="c90_pinned",
    target_digits=90,
    degree=4,
    p_val=10000,
    nq=256,
    nrkeep=40,
    ropteffort=0.2,
    admin=0,
    admax=100000,
    adrange=5000,
    incr=60,
    i_param=11,
    lim0=404327,
    lim1=811066,
    lpb0=23,
    lpb1=23,
    mfb0=46,
    mfb1=46,
    ncurves0=9,
    ncurves1=10,
    qmin=200923,
    qrange=10000,
    bf=8388608,           # 2^23
    bg=8388608,           # 2^23
    area=421366071296.0,  # 2^21 * 200923
    sqside=1,
    notes="Exact pinned CADO-NFS c90 profile from parameters/factor/params.c90.",
)

# 6. Exact pinned CADO c95 profile from parameters/factor/params.c95
CADO_PARAMS_C95 = CadoParameterProfile(
    name="c95_pinned",
    target_digits=95,
    degree=4,
    p_val=11000,
    nq=65536,
    nrkeep=36,
    ropteffort=0.9,
    admin=0,
    admax=288,
    adrange=24,
    incr=12,
    i_param=11,
    lim0=450000,
    lim1=550000,
    lpb0=24,
    lpb1=25,
    mfb0=47,
    mfb1=48,
    lambda0=1.94,
    lambda1=1.91,
    ncurves0=7,
    ncurves1=8,
    qmin=100000,
    qrange=5000,
    bf=33554432,          # 2^25
    bg=16777216,          # 2^24
    area=209715200000.0,  # 2^21 * 100000
    sqside=1,
    notes="Exact pinned CADO-NFS c95 profile from parameters/factor/params.c95.",
)

# 7. Exact pinned CADO c100 profile from parameters/factor/params.c100
CADO_PARAMS_C100 = CadoParameterProfile(
    name="c100_pinned",
    target_digits=100,
    degree=5,
    p_val=7000,
    nq=15625,
    nrkeep=24,
    ropteffort=1.2,
    admin=0,
    admax=1680,
    adrange=60,
    incr=30,
    i_param=11,
    lim0=650000,
    lim1=800000,
    lpb0=25,
    lpb1=26,
    mfb0=48,
    mfb1=51,
    lambda0=1.90,
    lambda1=1.93,
    ncurves0=9,
    ncurves1=11,
    qmin=180000,
    qrange=5000,
    bf=67108864,          # 2^26
    bg=33554432,          # 2^25
    area=377487360000.0,  # 2^21 * 180000
    sqside=1,
    notes="Exact pinned CADO-NFS c100 profile from parameters/factor/params.c100.",
)

_REGISTERED_PROFILES: Dict[str, CadoParameterProfile] = {
    "c60_pinned": CADO_PARAMS_C60,
    "canary_plumbing_c60": CANARY_PLUMBING_C60,
    "c70_pinned": CADO_PARAMS_C70,
    "c80_pinned": CADO_PARAMS_C80,
    "c90_pinned": CADO_PARAMS_C90,
    "c95_pinned": CADO_PARAMS_C95,
    "c100_pinned": CADO_PARAMS_C100,
}


def get_cado_profile(name: str = "c60_pinned") -> CadoParameterProfile:
    """Retrieve registered CADO parameter profile by name."""
    if name not in _REGISTERED_PROFILES:
        raise KeyError(
            f"Unknown CADO profile '{name}'. Registered: {list(_REGISTERED_PROFILES.keys())}"
        )
    return _REGISTERED_PROFILES[name]
