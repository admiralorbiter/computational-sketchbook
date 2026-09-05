"""Data models for Number Field Sieve (NFS) polynomial systems and CADO-NFS integration.

Supports general two-polynomial representations of arbitrary degrees (d1, d2 >= 1),
skewness parameter, canonical CADO .poly format export/import, and CADO result metadata.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class NfsPolynomialPair(BaseModel):
    """General two-polynomial representation for Number Field Sieve (NFS).

    Represents:
        f_1(x) = sum_{i=0}^{d_1} c_i x^i   (typically algebraic side)
        f_2(x) = sum_{j=0}^{d_2} Y_j x^j   (typically rational side Y_1*x + Y_0, or algebraic)
    with a common root m modulo N: f_1(m) = f_2(m) = 0 (mod N),
    or more generally Res(f_1, f_2) = 0 (mod N).
    """

    f1_coeffs: List[int] = Field(
        ..., description="Coefficients of f1: [c_0, c_1, ..., c_{d1}] where f1(x) = sum c_i x^i"
    )
    f2_coeffs: List[int] = Field(
        ..., description="Coefficients of f2: [Y_0, Y_1, ..., Y_{d2}] where f2(x) = sum Y_j x^j"
    )
    N: Optional[int] = Field(default=None, description="Integer modulus to factor")
    m: Optional[int] = Field(default=None, description="Common root mod N (if linear/known)")
    skew: float = Field(default=1.0, description="Recommended skewness s for sieve rectangle (X = s*Y)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Auxiliary properties / comments")

    @property
    def degree1(self) -> int:
        """Degree of f1 (algebraic side)."""
        return len(self.f1_coeffs) - 1

    @property
    def degree2(self) -> int:
        """Degree of f2 (rational/second side)."""
        return len(self.f2_coeffs) - 1

    @property
    def degree(self) -> int:
        """Main degree (max of degrees)."""
        return max(self.degree1, self.degree2)

    def eval_f1(self, x: int) -> int:
        """Evaluate f_1(x) over Z."""
        res = 0
        p = 1
        for c in self.f1_coeffs:
            res += c * p
            p *= x
        return res

    def eval_f2(self, x: int) -> int:
        """Evaluate f_2(x) over Z."""
        res = 0
        p = 1
        for c in self.f2_coeffs:
            res += c * p
            p *= x
        return res

    def eval_f1_homogeneous(self, a: int, b: int) -> int:
        """Evaluate F_1(a, b) = b^{d_1} f_1(a / b) = sum c_i a^i b^{d_1 - i}."""
        d = self.degree1
        res = 0
        for i, c in enumerate(self.f1_coeffs):
            res += c * (a ** i) * (b ** (d - i))
        return res

    def eval_f2_homogeneous(self, a: int, b: int) -> int:
        """Evaluate F_2(a, b) = b^{d_2} f_2(a / b) = sum Y_j a^j b^{d_2 - j}."""
        d = self.degree2
        res = 0
        for j, c in enumerate(self.f2_coeffs):
            res += c * (a ** j) * (b ** (d - j))
        return res

    def to_cado_poly_string(self) -> str:
        """Format polynomial pair as a canonical CADO-NFS .poly file."""
        lines = []
        if self.N is not None:
            lines.append(f"n: {self.N}")
        lines.append(f"skew: {self.skew:.4f}")

        # c_i coefficients for f1 (algebraic side)
        for i, c in enumerate(self.f1_coeffs):
            lines.append(f"c{i}: {c}")

        # Y_j coefficients for f2 (rational / side 0)
        for j, c in enumerate(self.f2_coeffs):
            lines.append(f"Y{j}: {c}")

        if self.m is not None:
            lines.append(f"# m: {self.m}")

        for k, v in self.metadata.items():
            lines.append(f"# {k}: {v}")

        return "\n".join(lines) + "\n"

    def save_cado_poly_file(self, path: Union[str, Path]) -> Path:
        """Write canonical CADO .poly file to disk."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.to_cado_poly_string(), encoding="utf-8")
        return target


class CadoPolyselectResult(BaseModel):
    """Result of CADO polyselection pipeline (polyselect + ropt)."""

    pair: NfsPolynomialPair
    modulus_n: int
    degree: int
    cpu_seconds: float
    wall_seconds: float
    raw_output: str
    command: List[str]


class CadoScoreResult(BaseModel):
    """Result of CADO score --full evaluation."""

    murphy_e: float
    lognorm: Optional[float] = None
    exp_e: Optional[float] = None
    skew: Optional[float] = None
    rroots: Optional[int] = None
    alpha: Optional[float] = None
    wall_seconds: float = 0.0
    cpu_seconds: float = 0.0
    raw_output: str = ""


class CadoSieveResult(BaseModel):
    """Result of CADO makefb + las relation collection."""

    total_relations: int
    unique_relations: int
    q_start: int
    q_range: int
    wall_seconds: float
    cpu_seconds: float
    relations_per_cpu_second: float
    relations_hash: str = ""
    ab_pairs_hash: str = ""
    reported_relations_count: Optional[int] = None
    parsed_relations_count: Optional[int] = None
    conservation_checked: bool = False
    checked_with_check_rels: bool = False
    raw_output: str = ""
