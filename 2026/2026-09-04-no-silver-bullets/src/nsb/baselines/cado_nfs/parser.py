"""Parsers for CADO-NFS file formats and command outputs.

Handles:
1. Canonical CADO .poly file parsing into NfsPolynomialPair.
2. CADO score (--full) stdout parsing into CadoScoreResult.
3. CADO las lattice-siever stdout parsing into CadoSieveResult.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from nsb.baselines.cado_nfs.models import (
    CadoScoreResult,
    CadoSieveResult,
    NfsPolynomialPair,
)


def parse_cado_poly_blocks(content_or_path: Union[str, Path]) -> List[NfsPolynomialPair]:
    """Parse multiple polynomial candidate blocks from CADO-NFS polyselect output.

    Handles multiple candidate blocks emitted by `polyselect -admin ... -admax ...`.
    Each block contains:
        n: ...
        skew: ...
        c0: ... / c5: ... or poly0: ...
        Y0: ... / Y1: ... or poly1: ...
    """
    if isinstance(content_or_path, Path) or (isinstance(content_or_path, str) and "\n" not in content_or_path and Path(content_or_path).is_file()):
        text = Path(content_or_path).read_text(encoding="utf-8")
    else:
        text = str(content_or_path)

    blocks: List[NfsPolynomialPair] = []

    # Current block state
    n_val: Optional[int] = None
    skew_val: float = 1.0
    m_val: Optional[int] = None
    c_coeffs: Dict[int, int] = {}
    y_coeffs: Dict[int, int] = {}
    metadata: Dict[str, Any] = {}

    def flush_block():
        nonlocal n_val, skew_val, m_val, c_coeffs, y_coeffs, metadata
        if not c_coeffs or not y_coeffs:
            return

        max_c = max(c_coeffs.keys())
        max_y = max(y_coeffs.keys())
        f1_list = [c_coeffs.get(i, 0) for i in range(max_c + 1)]
        f2_list = [y_coeffs.get(j, 0) for j in range(max_y + 1)]

        # If f2 is linear Y1*x + Y0 and m is None, derive m
        derived_m = m_val
        if derived_m is None and len(f2_list) == 2 and f2_list[1] != 0 and n_val is not None:
            try:
                import gmpy2
                y0 = f2_list[0]
                y1 = f2_list[1]
                inv_y1 = int(gmpy2.invert(y1, n_val))
                derived_m = int((-y0 * inv_y1) % n_val)
            except Exception:
                pass

        pair = NfsPolynomialPair(
            f1_coeffs=f1_list,
            f2_coeffs=f2_list,
            N=n_val,
            m=derived_m,
            skew=skew_val,
            metadata=dict(metadata),
        )
        blocks.append(pair)

        # Reset block
        c_coeffs = {}
        y_coeffs = {}
        m_val = None
        skew_val = 1.0
        metadata = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if c_coeffs and y_coeffs:
                flush_block()
            continue

        if line.startswith("#"):
            comment = line.lstrip("#").strip()
            # Check for rank like "# 0-th best polynomial found" or "# 1-th best..."
            m_rank = re.search(r"(\d+)-(?:th|st|nd|rd)\s+best\s+polynomial\s+found", comment, re.IGNORECASE)
            if m_rank:
                rank_val = int(m_rank.group(1))
                metadata["best_rank"] = rank_val
                if rank_val == 0:
                    metadata["is_best"] = True

            # Check for embedded properties like "# lognorm 50.12, exp_E 48.25"
            # Support MurphyE(...) = ..., Murphy_E = ..., Murphy_E: ...
            m_score = re.search(r"Murphy_?E(?:\s*\([^)]*\))?\s*[:=]\s*([0-9.eE+-]+)", comment, re.IGNORECASE)
            if m_score:
                try:
                    metadata["murphy_e"] = float(m_score.group(1))
                except ValueError:
                    pass
            m_exp = re.search(r"\bexp_E\s*[:= ]\s*([0-9.eE+-]+)", comment, re.IGNORECASE)
            if m_exp:
                try:
                    metadata["exp_e"] = float(m_exp.group(1))
                except ValueError:
                    pass
            m_ln = re.search(r"\blognorm\s*[:= ]\s*([0-9.eE+-]+)", comment, re.IGNORECASE)
            if m_ln:
                try:
                    metadata["lognorm"] = float(m_ln.group(1))
                except ValueError:
                    pass
            m_sk = re.search(r"\bskew\s*[:= ]\s*([0-9.eE+-]+)", comment, re.IGNORECASE)
            if m_sk:
                try:
                    skew_val = float(m_sk.group(1))
                except ValueError:
                    pass

            if ":" in comment:
                k, v = comment.split(":", 1)
                k = k.strip()
                v = v.strip()
                if k == "m":
                    try:
                        m_val = int(v)
                    except ValueError:
                        pass
                elif k.lower() in ("exp_e", "murphy_e", "lognorm"):
                    try:
                        metadata[k.lower()] = float(v)
                    except ValueError:
                        metadata[k] = v
                else:
                    metadata[k] = v
            continue

        if ":" not in line:
            continue

        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()

        if key == "n":
            # If we encounter a new modulus or block marker while having full coeffs
            if c_coeffs and y_coeffs:
                flush_block()
            try:
                n_val = int(val)
            except ValueError:
                pass
        elif key == "skew":
            try:
                skew_val = float(val)
            except ValueError:
                pass
        elif key.startswith("c") and key[1:].isdigit():
            c_coeffs[int(key[1:])] = int(val)
        elif key.startswith("Y") and key[1:].isdigit():
            y_coeffs[int(key[1:])] = int(val)
        elif key == "poly0":
            # Modern CADO poly0: c0,c1,c2...
            parts = [int(p.strip()) for p in val.split(",") if p.strip()]
            for i, p in enumerate(parts):
                c_coeffs[i] = p
        elif key == "poly1":
            # Modern CADO poly1: Y0,Y1...
            parts = [int(p.strip()) for p in val.split(",") if p.strip()]
            for j, p in enumerate(parts):
                y_coeffs[j] = p
        else:
            metadata[key] = val

    # Flush final block
    if c_coeffs and y_coeffs:
        flush_block()

    return blocks


def parse_cado_poly_file(content_or_path: Union[str, Path]) -> NfsPolynomialPair:
    """Parse a CADO-NFS .poly format string or file into an NfsPolynomialPair.

    If multiple candidate blocks are present, selects the best candidate
    (by Murphy-E or lognorm if available, or the first block).
    """
    blocks = parse_cado_poly_blocks(content_or_path)
    if not blocks:
        raise ValueError(f"No valid polynomial blocks found in CADO poly input")

    if len(blocks) == 1:
        return blocks[0]

    # Select best candidate if metadata contains Murphy-E or lognorm
    best = blocks[0]
    best_score = -1.0
    for b in blocks:
        if "murphy_e" in b.metadata:
            score = float(b.metadata["murphy_e"])
            if score > best_score:
                best_score = score
                best = b

    return best


def parse_cado_score_output(stdout_text: str) -> CadoScoreResult:
    """Parse output from CADO-NFS `score --full`.

    Expected patterns in real CADO score output:
    - `# exp_E 48.25, lognorm 50.12, skew 2.34, 3 rroots`
    - `# MurphyE(Bf=1000000, Bg=500000, area=1.00e+07) = 1.2345e-11`
    - Or whitespace-separated / colon-separated formats.
    """
    murphy_e: Optional[float] = None
    lognorm: Optional[float] = None
    exp_e: Optional[float] = None
    skew: Optional[float] = None
    rroots: Optional[int] = None
    alpha: Optional[float] = None

    for line in stdout_text.splitlines():
        # Match MurphyE: "MurphyE(...) = 1.2345e-11" or "MurphyE(...)=1.2345e-11"
        m_e = re.search(r"MurphyE\s*\([^)]*\)\s*=\s*([0-9.eE+-]+)", line)
        if m_e:
            murphy_e = float(m_e.group(1))

        if murphy_e is None:
            m_e2 = re.search(r"Murphy[- ]?E\s*[:= ]\s*([0-9.eE+-]+)", line, re.IGNORECASE)
            if m_e2:
                murphy_e = float(m_e2.group(1))

        # Match lognorm: either "lognorm = 48.2" or "lognorm 48.2"
        m_ln = re.search(r"\blognorm\s*[:= ]\s*([0-9.eE+-]+)", line)
        if m_ln:
            lognorm = float(m_ln.group(1))

        # Match exp_E: either "exp_E = 46.5" or "exp_E 46.5"
        m_exp = re.search(r"\bexp_E\s*[:= ]\s*([0-9.eE+-]+)", line)
        if m_exp:
            exp_e = float(m_exp.group(1))

        # Match skew: either "skew = 2.45" or "skew 2.45"
        m_skew = re.search(r"\bskew\s*[:= ]\s*([0-9.eE+-]+)", line)
        if m_skew:
            skew = float(m_skew.group(1))

        # Match rroots: "3 rroots" or "rroots 3" or "rroots: 3"
        m_rr = re.search(r"(?:(\d+)\s+rroots|\brroots\s*[:= ]\s*(\d+))", line)
        if m_rr:
            rroots = int(m_rr.group(1) or m_rr.group(2))

        # Optional alpha if present
        m_alpha = re.search(r"\balpha\s*[:= ]\s*([0-9.eE+-]+)", line)
        if m_alpha:
            alpha = float(m_alpha.group(1))

    if murphy_e is None:
        # Fallback: look for the last scientific number associated with E
        m_any_e = re.search(r"\bE\s*[:=]\s*([0-9.eE+-]+)", stdout_text)
        if m_any_e:
            murphy_e = float(m_any_e.group(1))

    if murphy_e is None:
        raise ValueError(f"Could not parse Murphy-E from CADO score output:\n{stdout_text[:500]}")

    if lognorm is None and exp_e is not None:
        lognorm = exp_e

    return CadoScoreResult(
        murphy_e=murphy_e,
        lognorm=lognorm,
        exp_e=exp_e,
        skew=skew,
        rroots=rroots,
        alpha=alpha,
        raw_output=stdout_text,
    )


def parse_las_output(stdout_text: str, enforce_conservation: bool = True) -> CadoSieveResult:
    """Parse relation output and timings from CADO-NFS `las`.

    In CADO las:
    - Relations are lines matching `a,b:p1,p2...:q1,q2...` or lines without `#` containing colon separators.
    - Reports lines: `# Total <N> reports` or `# Total <N> relations`
    - Timing lines: `# Total cpu time: <sec>s` or `# Total cpu: <sec>s`
    - Special-q line: `# special-q ...`
    """
    total_parsed_lines = 0
    reported_count: Optional[int] = None
    relations_records_set: Set[str] = set()
    ab_pairs_set: Set[Tuple[int, int]] = set()

    cpu_sec = 0.0
    wall_sec = 0.0
    q_start = 0
    q_range = 0

    for line in stdout_text.splitlines():
        line = line.strip()
        if not line:
            continue

        if not line.startswith("#"):
            # Check for relation format "a,b:..."
            parts = line.split(":")
            if len(parts) >= 3 and "," in parts[0]:
                try:
                    a_str, b_str = parts[0].split(",", 1)
                    a = int(a_str)
                    b = int(b_str)
                    ab_pairs_set.add((a, b))

                    # Normalize factors on each side: trim and sort
                    side0_factors = sorted([f.strip() for f in parts[1].split(",") if f.strip()])
                    side1_factors = sorted([f.strip() for f in parts[2].split(",") if f.strip()])
                    normalized_rec = f"{a},{b}:{','.join(side0_factors)}:{','.join(side1_factors)}"
                    relations_records_set.add(normalized_rec)
                    total_parsed_lines += 1
                except ValueError:
                    pass
            continue

        # Comment line parsing
        # Special-q info: "# Sieve special-q: 50000000..50001000" or similar
        m_q = re.search(r"special-q[:\s]+(\d+)\.\.(\d+)", line)
        if m_q:
            q0 = int(m_q.group(1))
            q1 = int(m_q.group(2))
            q_start = q0
            q_range = q1 - q0

        # Reported relations count: "# Total 1234 reports" or "# Total 1234 relations"
        m_rep = re.search(r"#\s*Total\s+(\d+)\s+(?:reports|relations)", line, re.IGNORECASE)
        if m_rep:
            reported_count = int(m_rep.group(1))

        # CPU time: "# Total cpu time: 12.34s" or "# Total cpu: 12.34"
        m_cpu = re.search(r"#\s*Total\s+cpu(?:\s+time)?\s*[:=]\s*([0-9.]+)", line, re.IGNORECASE)
        if m_cpu:
            cpu_sec = float(m_cpu.group(1))

        # Wall time: "# Total elapsed time: 5.67s" or "# Total wall: 5.67"
        m_wall = re.search(r"#\s*Total\s+(?:elapsed|wall)(?:\s+time)?\s*[:=]\s*([0-9.]+)", line, re.IGNORECASE)
        if m_wall:
            wall_sec = float(m_wall.group(1))

    # Parser conservation check:
    # reported relations in comment line must match parsed non-comment relation lines fail-closed
    conservation_checked = False
    if enforce_conservation:
        if reported_count is None:
            raise ValueError(
                "Relation conservation failure: LAS output missing '# Total <n> reports' summary line; "
                "cannot verify relation count conservation fail-closed."
            )
        if reported_count != total_parsed_lines:
            raise ValueError(
                f"Parser conservation failure: reported {reported_count} relations in las comment, "
                f"but parsed {total_parsed_lines} relation lines"
            )
        conservation_checked = True
    elif reported_count is not None:
        conservation_checked = (reported_count == total_parsed_lines)

    total_relations = reported_count if reported_count is not None else total_parsed_lines
    unique_relations = len(relations_records_set) if relations_records_set else total_relations
    rel_per_cpu = unique_relations / cpu_sec if cpu_sec > 0 else 0.0

    # 1. Canonical complete normalized relation records SHA-256 hash
    import hashlib
    sorted_records = sorted(list(relations_records_set))
    h_rec = hashlib.sha256()
    for rec in sorted_records:
        h_rec.update(f"{rec}\n".encode("utf-8"))
    rel_hash = h_rec.hexdigest() if sorted_records else ""

    # 2. Canonical (a, b) pair invariant SHA-256 hash
    sorted_ab = sorted(list(ab_pairs_set))
    h_ab = hashlib.sha256()
    for a, b in sorted_ab:
        h_ab.update(f"{a},{b}\n".encode("utf-8"))
    ab_hash = h_ab.hexdigest() if sorted_ab else ""

    return CadoSieveResult(
        total_relations=total_relations,
        unique_relations=unique_relations,
        q_start=q_start,
        q_range=q_range,
        wall_seconds=wall_sec,
        cpu_seconds=cpu_sec,
        relations_per_cpu_second=round(rel_per_cpu, 4),
        relations_hash=rel_hash,
        ab_pairs_hash=ab_hash,
        reported_relations_count=reported_count,
        parsed_relations_count=total_parsed_lines,
        conservation_checked=conservation_checked,
        raw_output=stdout_text,
    )
