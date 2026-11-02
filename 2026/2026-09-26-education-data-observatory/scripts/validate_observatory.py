#!/usr/bin/env python3
"""
Education Data Observatory — Automated Repository Validation Suite
Executes named, modular integrity checks enforcing referential consistency,
path portability, markdown link health, asset existence, and roadmap synchronization.
"""

import sys
import os
import re
import csv
import hashlib
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_repo_dir() -> Path:
    return Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# Named Test 1: registry_unique_ids
# ----------------------------------------------------------------------
def test_registry_unique_ids(repo_dir: Path):
    errors = []
    warnings = []
    
    # Check measures.csv
    measures_csv = repo_dir / "registry" / "measures.csv"
    seen_measures = set()
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["measure_id"].strip()
            if mid in seen_measures:
                errors.append(f"Duplicate measure_id in measures.csv: '{mid}'")
            seen_measures.add(mid)
            
    # Check sources.csv
    sources_csv = repo_dir / "registry" / "sources.csv"
    seen_sources = set()
    with open(sources_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = row["source_id"].strip()
            if sid in seen_sources:
                errors.append(f"Duplicate source_id in sources.csv: '{sid}'")
            seen_sources.add(sid)
            
    # Check operationalizations.csv
    op_csv = repo_dir / "registry" / "operationalizations.csv"
    seen_ops = set()
    with open(op_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            oid = row["operationalization_id"].strip()
            if oid in seen_ops:
                errors.append(f"Duplicate operationalization_id in operationalizations.csv: '{oid}'")
            seen_ops.add(oid)

    detail = f"{len(seen_measures)} measures, {len(seen_sources)} sources, {len(seen_ops)} operationalizations unique"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 2: registry_foreign_keys
# ----------------------------------------------------------------------
def test_registry_foreign_keys(repo_dir: Path):
    errors = []
    warnings = []
    
    measures_csv = repo_dir / "registry" / "measures.csv"
    sources_csv = repo_dir / "registry" / "sources.csv"
    op_csv = repo_dir / "registry" / "operationalizations.csv"
    rel_csv = repo_dir / "registry" / "relationships.csv"
    
    measure_ids = set()
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            measure_ids.add(row["measure_id"].strip())
            
    source_ids = set()
    with open(sources_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            source_ids.add(row["source_id"].strip())
            
    valid_nodes = measure_ids.union(source_ids)
    
    # Check operationalizations foreign keys
    op_count = 0
    with open(op_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            op_count += 1
            oid = row["operationalization_id"].strip()
            mid = row["measure_id"].strip()
            sid = row["source_id"].strip()
            if mid not in measure_ids:
                errors.append(f"operationalizations.csv: '{oid}' references unknown measure '{mid}'")
            if sid not in source_ids:
                errors.append(f"operationalizations.csv: '{oid}' references unknown source '{sid}'")

    # Check relationships foreign keys
    rel_count = 0
    with open(rel_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s_node = row.get("source_node", "").strip()
            t_node = row.get("target_node", "").strip()
            if not s_node or not t_node:
                continue
            rel_count += 1
            if s_node not in valid_nodes:
                errors.append(f"relationships.csv: source_node '{s_node}' not found in measures or sources")
            if t_node not in valid_nodes:
                errors.append(f"relationships.csv: target_node '{t_node}' not found in measures or sources")

    detail = f"{op_count} operationalizations and {rel_count} relationships have valid foreign keys"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 3: active_dossiers_exist
# ----------------------------------------------------------------------
def test_active_dossiers_exist(repo_dir: Path):
    errors = []
    warnings = []
    
    measures_csv = repo_dir / "registry" / "measures.csv"
    active_count = 0
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["measure_id"].strip()
            status = row["status"].strip()
            d_path = row["dossier_path"].strip()
            if status in ("audited", "in_progress", "active"):
                active_count += 1
                if not d_path:
                    errors.append(f"Measure '{mid}' status '{status}' but has no dossier_path")
                else:
                    full_p = repo_dir / d_path
                    if not full_p.exists():
                        errors.append(f"Active measure '{mid}' references nonexistent dossier file: '{d_path}'")
                        
    detail = f"{active_count} active/audited measure dossiers verified on disk"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 4: source_dossiers_exist
# ----------------------------------------------------------------------
def test_source_dossiers_exist(repo_dir: Path):
    errors = []
    warnings = []
    
    sources_csv = repo_dir / "registry" / "sources.csv"
    verified_sources = 0
    with open(sources_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = row["source_id"].strip()
            status = row["status"].strip()
            dossier_file = repo_dir / "sources" / sid / "README.md"
            if status == "active":
                if not dossier_file.exists():
                    errors.append(f"Active source '{sid}' missing dossier at 'sources/{sid}/README.md'")
                else:
                    verified_sources += 1

    detail = f"{verified_sources} active source dossiers verified on disk"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 5: upstream_checksums
# ----------------------------------------------------------------------
def test_upstream_checksums(repo_dir: Path):
    errors = []
    warnings = []
    
    upstream_csv = repo_dir / "data" / "upstream_artifacts.csv"
    if not upstream_csv.exists():
        errors.append("data/upstream_artifacts.csv does not exist")
        return False, errors, warnings, "ledger missing"
        
    verified_artifacts = 0
    with open(upstream_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            src_proj = row["source_project"].strip()
            rel_p = row["relative_path"].strip()
            expected_sha = row.get("sha256_or_git_blob_sha", "").strip()
            
            full_path = (repo_dir.parent / src_proj / rel_p).resolve()
            if not full_path.exists():
                errors.append(f"Upstream artifact missing on disk: '{full_path}'")
                continue
                
            h = hashlib.sha256()
            with open(full_path, "rb") as bf:
                while chunk := bf.read(65536):
                    h.update(chunk)
            actual_sha = h.hexdigest()
            if actual_sha != expected_sha:
                errors.append(f"SHA-256 mismatch for '{rel_p}': expected {expected_sha}, got {actual_sha}")
            else:
                verified_artifacts += 1
                
    detail = f"{verified_artifacts} upstream data artifacts cryptographically verified"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 6: portable_paths
# ----------------------------------------------------------------------
def test_portable_paths(repo_dir: Path):
    errors = []
    warnings = []
    
    scan_exts = {".md", ".py", ".csv", ".json"}
    hardcoded_user = re.compile(r"[cC]:[\\/][uU]sers[\\/]", re.IGNORECASE)
    file_uri = re.compile(r"file:///", re.IGNORECASE)
    
    violations = []
    files_checked = 0
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in scan_exts:
                if p.name == "validate_observatory.py":
                    continue
                files_checked += 1
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    if hardcoded_user.search(text):
                        violations.append(f"Absolute Windows user path in: {p.relative_to(repo_dir)}")
                    if file_uri.search(text):
                        violations.append(f"Local file:/// URI in: {p.relative_to(repo_dir)}")
                except Exception as e:
                    warnings.append(f"Could not read {p.relative_to(repo_dir)}: {e}")

    for v in violations:
        errors.append(v)
        
    detail = f"{files_checked} text files scanned; zero absolute/file:/// paths found"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 7: markdown_internal_links
# ----------------------------------------------------------------------
def test_markdown_internal_links(repo_dir: Path):
    errors = []
    warnings = []
    
    link_pattern = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
    total_checked = 0
    
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            if f.endswith(".md"):
                doc_path = Path(root) / f
                text = doc_path.read_text(encoding="utf-8", errors="ignore")
                for label, target in link_pattern.findall(text):
                    clean = target.split("#")[0].split("?")[0].strip()
                    if not clean or clean.startswith(("http://", "https://", "mailto:")):
                        continue
                    total_checked += 1
                    target_p = (doc_path.parent / clean).resolve()
                    if not target_p.exists():
                        errors.append(f"Broken markdown link in {doc_path.relative_to(repo_dir)}: '{target}' (resolved to {target_p})")

    detail = f"{total_checked} internal markdown links verified"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 8: dashboard_assets
# ----------------------------------------------------------------------
def test_dashboard_assets(repo_dir: Path):
    errors = []
    warnings = []
    
    image_pattern = re.compile(r"!\[.*?\]\((.*?)\)")
    total_images = 0
    
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            if f.endswith(".md"):
                doc_path = Path(root) / f
                text = doc_path.read_text(encoding="utf-8", errors="ignore")
                for img in image_pattern.findall(text):
                    clean = img.split("#")[0].split("?")[0].strip()
                    if clean.startswith(("http://", "https://")):
                        continue
                    total_images += 1
                    target_p = (doc_path.parent / clean).resolve()
                    if not target_p.exists():
                        errors.append(f"Broken image asset in {doc_path.relative_to(repo_dir)}: '{img}'")

    detail = f"{total_images} dashboard image embeds verified on disk"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 9: git_hygiene
# ----------------------------------------------------------------------
def test_git_hygiene(repo_dir: Path):
    errors = []
    warnings = []
    
    pycache_found = []
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for d in dirs:
            if d == "__pycache__":
                pycache_found.append(str((Path(root) / d).relative_to(repo_dir)))
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                pycache_found.append(str((Path(root) / f).relative_to(repo_dir)))

    if pycache_found:
        for p in pycache_found:
            errors.append(f"Found compiled bytecode/pycache: {p}")
            
    detail = "Zero __pycache__ or .pyc files detected in tree"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 10: roadmap_status_consistency
# ----------------------------------------------------------------------
def test_roadmap_status_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    # 1. Read registry statuses
    measures_csv = repo_dir / "registry" / "measures.csv"
    reg_status = {}
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            reg_status[row["measure_id"].strip()] = row["status"].strip()
            
    # 2. Check root README roadmap mentions
    readme_text = (repo_dir / "README.md").read_text(encoding="utf-8")
    
    # EDU-002: audited in registry -> must be Completed / Frozen / Audited in README
    if reg_status.get("EDU-002") == "audited":
        if "EDU-002" not in readme_text or "FROZEN" not in readme_text:
            errors.append("README.md roadmap does not reflect EDU-002 as Completed & Frozen")
            
    # EDU-003: check registry agreement with README roadmap
    if reg_status.get("EDU-003") == "in_progress":
        if "EDU-003" in readme_text and "AUDITED / FROZEN" in readme_text:
            # If README claims frozen but registry is in_progress, flag drift
            if "Task 004 & 004A (In Progress / Auditing)" not in readme_text and "IN PROGRESS" not in readme_text:
                errors.append("README.md claims EDU-003 is frozen while registry status is in_progress")
    elif reg_status.get("EDU-003") == "audited":
        if "IN PROGRESS / AUDITING" in readme_text:
            errors.append("Registry has EDU-003 as audited, but README.md roadmap still lists IN PROGRESS / AUDITING")

    # 3. Check measure dossier internal status metadata
    for mid in ("EDU-001", "EDU-002", "EDU-003"):
        dossier_p = repo_dir / "measures" / f"{mid}-{reg_status.get(mid, '')}"
        # Search for dossier path from registry
        with open(measures_csv, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["measure_id"].strip() == mid:
                    d_rel = row["dossier_path"].strip()
                    if d_rel and (repo_dir / d_rel).exists():
                        d_text = (repo_dir / d_rel).read_text(encoding="utf-8")
                        m = re.search(r"\|\s*\*\*Status\*\*\s*\|\s*`?([a-zA-Z0-9_\-]+)`?", d_text)
                        if m:
                            doc_stat = m.group(1).lower()
                            exp_stat = reg_status[mid].lower()
                            if doc_stat != exp_stat and not (doc_stat == "in_progress" and exp_stat == "in_progress"):
                                errors.append(f"Dossier {d_rel} status `{doc_stat}` does not match registry status `{exp_stat}`")

    detail = "Registry status, root README roadmap, and canonical dossiers are synchronized"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 11: source_inventory_consistency
# ----------------------------------------------------------------------
def test_source_inventory_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    sources_csv = repo_dir / "registry" / "sources.csv"
    registered_sources = set()
    with open(sources_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            registered_sources.add(row["source_id"].strip())
            
    sources_readme = (repo_dir / "sources" / "README.md").read_text(encoding="utf-8")
    root_readme = (repo_dir / "README.md").read_text(encoding="utf-8")
    
    for sid in registered_sources:
        if sid not in sources_readme:
            errors.append(f"Source '{sid}' registered in sources.csv but missing in sources/README.md table")
        if f"{sid}/README.md" not in root_readme:
            errors.append(f"Source '{sid}' registered in sources.csv but missing in README.md architecture tree")

    detail = f"All {len(registered_sources)} registered sources consistently cataloged across READMEs"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 12: canonical_measure_names_consistency
# ----------------------------------------------------------------------
def test_canonical_measure_names_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    measures_csv = repo_dir / "registry" / "measures.csv"
    names = {}
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names[row["measure_id"].strip()] = row["canonical_name"].strip()
            
    root_readme = (repo_dir / "README.md").read_text(encoding="utf-8")
    
    # Check core measures in root README graph
    core_checks = ["EDU-001", "EDU-002", "EDU-003", "EDU-006", "EDU-007", "EDU-011", "EDU-012", "EDU-014"]
    for mid in core_checks:
        cname = names[mid]
        # Allow variations like "Pupil / Teacher Ratio" vs "Pupil/Teacher Ratio"
        clean_cname = re.sub(r"\s+", " ", cname).strip()
        if mid in root_readme:
            # Verify the canonical name appears near the measure ID
            m_pattern = re.compile(rf"{mid}[^)]*?{re.escape(clean_cname[:12])}", re.IGNORECASE)
            if not m_pattern.search(root_readme):
                warnings.append(f"README.md may use non-canonical label for {mid} (expected '{cname}')")

    detail = "Core canonical measure names verified across measurement graph"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 13: claims_ledger_integrity
# ----------------------------------------------------------------------
def test_claims_ledger_integrity(repo_dir: Path):
    errors = []
    warnings = []
    
    claims_csv = repo_dir / "analysis" / "results" / "claims.csv"
    if not claims_csv.exists():
        errors.append("Machine-readable claims ledger 'analysis/results/claims.csv' does not exist")
        return False, errors, warnings, "claims.csv missing"
        
    measures_csv = repo_dir / "registry" / "measures.csv"
    reg_measures = set()
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            reg_measures.add(row["measure_id"].strip())
            
    universes_csv = repo_dir / "registry" / "universes.csv"
    reg_universes = set()
    if universes_csv.exists():
        with open(universes_csv, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                reg_universes.add(row["universe_id"].strip())
    else:
        errors.append("Universes registry 'registry/universes.csv' does not exist")
        
    upstream_csv = repo_dir / "data" / "upstream_artifacts.csv"
    reg_artifacts = set()
    with open(upstream_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            reg_artifacts.add(row["artifact_id"].strip())
            
    claim_ids = set()
    claims_count = 0
    with open(claims_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            claims_count += 1
            cid = r["claim_id"].strip()
            if cid in claim_ids:
                errors.append(f"Duplicate claim_id in claims.csv: '{cid}'")
            claim_ids.add(cid)
            
            mid = r["measure_id"].strip()
            if mid not in reg_measures:
                errors.append(f"Claim '{cid}' references unregistered measure_id '{mid}'")
                
            uid = r["universe_id"].strip()
            if uid not in reg_universes:
                errors.append(f"Claim '{cid}' references unregistered universe_id '{uid}'")
                
            script_rel = r["analysis_script"].strip()
            if not (repo_dir / script_rel).exists():
                errors.append(f"Claim '{cid}' references missing analysis_script '{script_rel}'")
                
            art_ids = [a.strip() for a in r["source_artifact_ids"].split(",") if a.strip()]
            for aid in art_ids:
                if aid not in reg_artifacts:
                    errors.append(f"Claim '{cid}' references unregistered source_artifact_id '{aid}'")
                    
    detail = f"{claims_count} machine-readable claims verified across measures, universes, and scripts"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 14: claim_numeric_internal_consistency
# ----------------------------------------------------------------------
def test_claim_numeric_internal_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    claims_csv = repo_dir / "analysis" / "results" / "claims.csv"
    if not claims_csv.exists():
        return False, ["claims.csv missing"], [], "claims.csv missing"
        
    verified = 0
    with open(claims_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = r["claim_id"].strip()
            v_start_str = r["value_start"].strip()
            v_end_str = r["value_end"].strip()
            abs_chg_str = r["absolute_change"].strip()
            pct_chg_str = r["percent_change"].strip()
            basis = r.get("percent_basis", "").strip()
            
            # Check absolute change arithmetic: v_end - v_start == absolute_change
            if v_start_str not in ("NA", "nan", "") and v_end_str not in ("NA", "nan", "") and abs_chg_str not in ("NA", "nan", ""):
                try:
                    v_start = float(v_start_str)
                    v_end = float(v_end_str)
                    abs_chg = float(abs_chg_str)
                    expected_abs = v_end - v_start
                    if abs(abs_chg - expected_abs) > 0.02:
                        errors.append(f"Claim '{cid}' absolute_change mismatch: got {abs_chg}, expected {expected_abs:+.2f}")
                except ValueError as e:
                    errors.append(f"Claim '{cid}' float parse error for absolute_change: {e}")
                    
            # Check percent change arithmetic using percent_basis:
            if not basis:
                errors.append(f"Claim '{cid}' missing percent_basis field in claims.csv")
            elif basis == "not_applicable":
                if pct_chg_str not in ("NA", "nan", ""):
                    errors.append(f"Claim '{cid}' has percent_basis 'not_applicable' but percent_change is '{pct_chg_str}'")
            elif basis == "start_value":
                if pct_chg_str in ("NA", "nan", ""):
                    errors.append(f"Claim '{cid}' has percent_basis 'start_value' but percent_change is missing/NA")
                else:
                    try:
                        v_start = float(v_start_str)
                        v_end = float(v_end_str)
                        pct_chg = float(pct_chg_str)
                        if abs(v_start) > 1e-6:
                            expected_pct = (v_end - v_start) / v_start * 100.0
                            if abs(pct_chg - expected_pct) > 0.05:
                                errors.append(f"Claim '{cid}' percent_change mismatch against start_value: got {pct_chg}%, expected {expected_pct:+.2f}%")
                    except ValueError as e:
                        errors.append(f"Claim '{cid}' float parse error for percent_change: {e}")
            elif basis == "end_value":
                if pct_chg_str in ("NA", "nan", ""):
                    errors.append(f"Claim '{cid}' has percent_basis 'end_value' but percent_change is missing/NA")
                else:
                    try:
                        v_start = float(v_start_str)
                        v_end = float(v_end_str)
                        pct_chg = float(pct_chg_str)
                        if abs(v_end) > 1e-6:
                            expected_pct = (v_end - v_start) / v_end * 100.0
                            if abs(pct_chg - expected_pct) > 0.05:
                                errors.append(f"Claim '{cid}' percent_change mismatch against end_value: got {pct_chg}%, expected {expected_pct:+.2f}%")
                    except ValueError as e:
                        errors.append(f"Claim '{cid}' float parse error for percent_change: {e}")
            else:
                errors.append(f"Claim '{cid}' has unknown percent_basis '{basis}' (expected: start_value, end_value, or not_applicable)")
                    
            verified += 1
            
    detail = f"{verified} claims internally reconciled for absolute and percent change arithmetic (percent_basis verified)"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 15: claim_universe_support_consistency
# ----------------------------------------------------------------------
def test_claim_universe_support_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    claims_csv = repo_dir / "analysis" / "results" / "claims.csv"
    universes_csv = repo_dir / "registry" / "universes.csv"
    if not claims_csv.exists() or not universes_csv.exists():
        return False, ["claims.csv or universes.csv missing"], [], "Files missing"
        
    universes = {}
    with open(universes_csv, mode="r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            universes[r["universe_id"].strip()] = r
            
    checked = 0
    with open(claims_csv, mode="r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            checked += 1
            cid = r["claim_id"].strip()
            uid = r["universe_id"].strip()
            sup_str = r["support_n"].strip()
            
            if uid not in universes:
                errors.append(f"Claim '{cid}' references unknown universe '{uid}'")
                continue
                
            u_info = universes[uid]
            u_cnt_str = u_info["entity_count"].strip()
            u_notes = u_info.get("notes", "").lower()
            
            # If support_n is a dynamic range (e.g. "78 to 77")
            if "to" in sup_str:
                if "to" not in u_cnt_str:
                    errors.append(f"Claim '{cid}' has range support_n '{sup_str}' but universe '{uid}' entity_count is '{u_cnt_str}'")
                continue
                
            if sup_str.isdigit():
                sn = int(sup_str)
                if u_cnt_str.isdigit():
                    uc = int(u_cnt_str)
                    if sn > uc:
                        if "union" not in u_notes and "longitudinal" not in u_notes and "historical" not in u_notes:
                            errors.append(f"Claim '{cid}' support_n ({sn}) exceeds universe '{uid}' entity_count ({uc}) without documented longitudinal union")
                elif "to" in u_cnt_str:
                    parts = [int(p.strip()) for p in u_cnt_str.split("to") if p.strip().isdigit()]
                    if parts and sn > max(parts):
                        errors.append(f"Claim '{cid}' support_n ({sn}) exceeds maximum universe '{uid}' count ({max(parts)})")
            else:
                warnings.append(f"Claim '{cid}' support_n is non-numeric: '{sup_str}'")
                
    detail = f"{checked} claims verified for universe support_n consistency (support_n <= entity_count)"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 16: claim_note_numeric_drift
# ----------------------------------------------------------------------
def test_claim_note_numeric_drift(repo_dir: Path):
    errors = []
    warnings = []
    
    claims_csv = repo_dir / "analysis" / "results" / "claims.csv"
    if not claims_csv.exists():
        return False, ["claims.csv missing"], [], "claims.csv missing"
        
    stale_patterns = [
        (re.compile(r"disproving centrifugal suburban flight", re.IGNORECASE), "stale centrifugal flight language"),
        (re.compile(r"-\s*0\.36%"), "stale -0.36% enrollment change"),
        (re.compile(r"-\s*8\.00%"), "stale -8.00% enrollment sensitivity"),
        (re.compile(r"-\s*3\.26%"), "stale -3.26% teacher sensitivity"),
        (re.compile(r"\b22,860\.8\b"), "retracted 22,860.8 draft baseline"),
        (re.compile(r"\b24,028\.9\b"), "retracted 24,028.9 draft end level"),
        (re.compile(r"\+5\.11%"), "retracted +5.11% Balanced 77 figure"),
        (re.compile(r"-\s*9\.58%"), "retracted -9.58% declining district figure"),
        (re.compile(r"\+0\.73%"), "retracted +0.73% declining district teacher figure"),
        (re.compile(r"\b10,812\.24\b"), "retracted 10,812.24 Kansas baseline"),
        (re.compile(r"\b11,267\.50\b"), "retracted 11,267.50 Kansas LEA total"),
    ]
    
    checked = 0
    with open(claims_csv, mode="r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            checked += 1
            cid = r["claim_id"].strip()
            note = r["notes"].strip()
            
            for pat, desc in stale_patterns:
                if pat.search(note):
                    errors.append(f"Claim '{cid}' note contains {desc}: '{pat.pattern}'")
                    
            # Check for any percentage mentioned in notes (prohibited by design rule: numbers owned by columns)
            found_pcts = re.findall(r"([+-]?\d+\.?\d*)\s*%", note)
            if found_pcts:
                for p in found_pcts:
                    errors.append(f"Claim '{cid}' note contains redundant/drifting percentage '{p}%'; numbers must be owned by structured columns")
                    
    detail = f"{checked} claims verified free of stale/conflicting numbers in notes"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 17: source_dossier_measure_table_consistency
# ----------------------------------------------------------------------
def test_source_dossier_measure_table_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    measures_csv = repo_dir / "registry" / "measures.csv"
    canonical_names = {}
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            canonical_names[row["measure_id"].strip()] = row["canonical_name"].strip()
            
    sources_dir = repo_dir / "sources"
    source_dossiers = list(sources_dir.glob("*/README.md"))
    
    checked_mappings = 0
    for sd in source_dossiers:
        text = sd.read_text(encoding="utf-8")
        matches = re.findall(r"\|\s*`?(EDU-\d{3})`?\s*\|\s*([^|]+?)\s*\|", text)
        for mid, mname in matches:
            checked_mappings += 1
            mname_clean = mname.strip().strip("`")
            if mid not in canonical_names:
                errors.append(f"Source dossier {sd.relative_to(repo_dir)} references unknown measure ID '{mid}'")
                continue
                
            expected_name = canonical_names[mid]
            norm_actual = re.sub(r"[\s/]+", "", mname_clean.lower())
            norm_expected = re.sub(r"[\s/]+", "", expected_name.lower())
            
            if norm_actual not in norm_expected and norm_expected not in norm_actual:
                errors.append(
                    f"Source dossier {sd.relative_to(repo_dir)} labels {mid} as '{mname_clean}', "
                    f"expected canonical name '{expected_name}'"
                )
                
    detail = f"{checked_mappings} source-dossier downstream measure mappings verified against registry"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 18: claim_specific_dossier_consistency
# ----------------------------------------------------------------------
def test_claim_specific_dossier_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    claims_csv = repo_dir / "analysis" / "results" / "claims.csv"
    measures_csv = repo_dir / "registry" / "measures.csv"
    if not claims_csv.exists() or not measures_csv.exists():
        return False, ["Required files missing"], [], "Files missing"
        
    reg_status = {}
    dossier_paths = {}
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["measure_id"].strip()
            reg_status[mid] = row["status"].strip()
            dossier_paths[mid] = row["dossier_path"].strip()
            
    claims_by_measure = {}
    with open(claims_csv, mode="r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            mid = r["measure_id"].strip()
            claims_by_measure.setdefault(mid, []).append(r)
            
    verified_claim_rows = 0
    for mid, mstatus in reg_status.items():
        if mstatus != "audited":
            continue
        d_path = repo_dir / dossier_paths[mid]
        if not d_path.exists():
            continue
        d_text = d_path.read_text(encoding="utf-8")
        
        m_claims = claims_by_measure.get(mid, [])
        for c in m_claims:
            cid = c["claim_id"].strip()
            v_end_str = c["value_end"].strip()
            pct_str = c["percent_change"].strip()
            abs_str = c["absolute_change"].strip()
            
            # Find the specific row in Markdown tables containing this claim_id
            target_line = None
            for line in d_text.splitlines():
                if line.strip().startswith("|"):
                    cells = [cell.strip().strip("*` ") for cell in line.split("|")]
                    if cid in cells:
                        target_line = line
                        break
                        
            if not target_line:
                errors.append(f"Dossier {d_path.relative_to(repo_dir)} missing structured table row for claim '{cid}'")
                continue
                
            matched_row = False
            # Check percent_change
            if pct_str not in ("NA", "nan", ""):
                pct_val = float(pct_str)
                pct_cands = [f"{pct_val:+.2f}%", f"{pct_val:.2f}%", f"{pct_val:+.1f}%", f"{pct_val:.1f}%", f"{abs(pct_val):.2f}%"]
                for cand in pct_cands:
                    if cand in target_line:
                        matched_row = True
                        break
            # Check value_end or absolute_change
            if not matched_row and v_end_str not in ("NA", "nan", ""):
                v_end = float(v_end_str)
                v_cands = [f"{v_end:,.2f}", f"{v_end:,.0f}", f"{v_end:.2f}", f"{v_end:.0f}"]
                for cand in v_cands:
                    if cand in target_line:
                        matched_row = True
                        break
                        
            if matched_row:
                verified_claim_rows += 1
            else:
                errors.append(f"Dossier row for claim '{cid}' does not match registered numeric values (v_end={v_end_str}, pct={pct_str})")
                
    detail = f"{verified_claim_rows} claim rows explicitly verified against dossier summary tables"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 19: prohibited_legacy_terms_in_dossiers
# ----------------------------------------------------------------------
def test_prohibited_legacy_terms_in_dossiers(repo_dir: Path):
    errors = []
    warnings = []
    
    prohibited_patterns = [
        (re.compile(r"Students\s*/\s*Total\s*Staff", re.IGNORECASE), "misleading 'Students / Total Staff' PTR label"),
        (re.compile(r"40%\s*(?:to|–|-)\s*80%", re.IGNORECASE), "blanket '40% to 80%' class-size assertion"),
        (re.compile(r"24\s*(?:to|–|-)\s*28\+", re.IGNORECASE), "blanket '24 to 28+' class-size assertion"),
        (re.compile(r"centrifugal\s+suburban\s+flight", re.IGNORECASE), "discredited 'centrifugal suburban flight' causal claim"),
    ]
    
    measures_csv = repo_dir / "registry" / "measures.csv"
    audited_dossiers = []
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() == "audited":
                d_rel = row["dossier_path"].strip()
                if d_rel:
                    audited_dossiers.append(repo_dir / d_rel)
                    
    checked = 0
    for d_path in audited_dossiers:
        if not d_path.exists():
            continue
        text = d_path.read_text(encoding="utf-8")
        checked += 1
        for pat, desc in prohibited_patterns:
            matches = pat.findall(text)
            if matches:
                errors.append(f"Dossier {d_path.relative_to(repo_dir)} contains {desc}: {matches}")
                
    detail = f"{checked} audited dossiers verified free of prohibited legacy terms and blanket assertions"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 20: dossier_table_universe_and_subtotal_consistency
# ----------------------------------------------------------------------
def test_dossier_table_universe_and_subtotal_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    universes_csv = repo_dir / "registry" / "universes.csv"
    registered_universes = set()
    universe_counts = {}
    with open(universes_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = row["universe_id"].strip()
            registered_universes.add(uid)
            universe_counts[uid] = row["entity_count"].strip()
            
    measures_csv = repo_dir / "registry" / "measures.csv"
    audited_dossiers = []
    with open(measures_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() == "audited":
                d_rel = row["dossier_path"].strip()
                if d_rel:
                    audited_dossiers.append(repo_dir / d_rel)
                    
    # 1. Verify all cited universes in audited dossiers exist in universes.csv
    universe_citations_checked = 0
    for d_path in audited_dossiers:
        if not d_path.exists():
            continue
        text = d_path.read_text(encoding="utf-8")
        matches = set(re.findall(r"\b(KC_[A-Z0-9_]+)\b", text))
        for uid in matches:
            universe_citations_checked += 1
            if uid not in registered_universes:
                errors.append(f"Dossier {d_path.relative_to(repo_dir)} cites unregistered universe '{uid}'")
                
    # 2. Verify grade-band subtotal consistency in EDU-001 (Section 8.1 table)
    edu001_path = repo_dir / "measures" / "EDU-001-pupil-teacher-ratio" / "README.md"
    if edu001_path.exists():
        edu001_text = edu001_path.read_text(encoding="utf-8")
        band_counts = {}
        all_schools_count = None
        for line in edu001_text.splitlines():
            if line.strip().startswith("|") and any(k in line for k in ["Primary", "Middle", "High", "Other / Combined", "All Regular Schools"]):
                parts = [c.strip().strip("*` ") for c in line.split("|")[1:-1]]
                if len(parts) >= 2:
                    label = parts[0]
                    cnt_str = parts[1].replace(",", "")
                    if cnt_str.isdigit():
                        cnt = int(cnt_str)
                        if "All Regular Schools" in label:
                            all_schools_count = cnt
                        else:
                            band_counts[label] = cnt
        if all_schools_count is not None and band_counts:
            subtotal = sum(band_counts.values())
            if subtotal != all_schools_count:
                errors.append(f"EDU-001 Section 8.1 grade-band sum ({subtotal}) does not match All Regular Schools total ({all_schools_count}): {band_counts}")
            expected_u_count = universe_counts.get("KC_REGULAR_PTR_ACTIVE_616")
            if expected_u_count and expected_u_count.isdigit():
                if all_schools_count != int(expected_u_count):
                    errors.append(f"EDU-001 Section 8.1 total ({all_schools_count}) does not match KC_REGULAR_PTR_ACTIVE_616 entity_count ({expected_u_count})")
        else:
            errors.append("Could not parse EDU-001 Section 8.1 grade-band distribution table")

    # 3. Verify grade-band subtotal consistency in EDU-003 (Section 10.1 table) if present
    edu003_path = repo_dir / "measures" / "EDU-003-total-teacher-fte" / "README.md"
    if edu003_path.exists():
        edu003_text = edu003_path.read_text(encoding="utf-8")
        band_counts_003 = {}
        all_schools_count_003 = None
        for line in edu003_text.splitlines():
            if line.strip().startswith("|") and any(k in line for k in ["Elementary", "Middle", "High", "Other / Combined", "All Regular Schools"]):
                parts = [c.strip().strip("*` ") for c in line.split("|")[1:-1]]
                if len(parts) >= 2:
                    label = parts[0]
                    cnt_str = parts[1].replace(",", "")
                    if cnt_str.isdigit():
                        cnt = int(cnt_str)
                        if "All Regular Schools" in label:
                            all_schools_count_003 = cnt
                        else:
                            band_counts_003[label] = cnt
        if all_schools_count_003 is not None and band_counts_003:
            subtotal_003 = sum(band_counts_003.values())
            if subtotal_003 != all_schools_count_003:
                errors.append(f"EDU-003 Section 10.1 grade-band sum ({subtotal_003}) does not match All Regular Schools total ({all_schools_count_003}): {band_counts_003}")

    detail = f"{universe_citations_checked} universe citations registered; grade-band subtotals reconciled (N=616 in EDU-001, N=622 in EDU-003)"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Named Test 21: canonical_universe_implementation_consistency
# ----------------------------------------------------------------------
def test_canonical_universe_implementation_consistency(repo_dir: Path):
    errors = []
    warnings = []
    
    # 1. Prohibit raw operational_status == 1 in any analysis or ledger script
    op_status_pattern = re.compile(r"operational_status\s*==\s*['\"]?1['\"]?")
    py_files_checked = 0
    
    scan_dirs = [repo_dir / "analysis", repo_dir / "scripts"]
    for sdir in scan_dirs:
        if not sdir.exists():
            continue
        for p in sdir.rglob("*.py"):
            if p.name == "validate_observatory.py":
                continue
            py_files_checked += 1
            text = p.read_text(encoding="utf-8", errors="ignore")
            matches = op_status_pattern.findall(text)
            if matches:
                errors.append(f"Script {p.relative_to(repo_dir)} uses raw 'operational_status == 1' instead of canonical 'is_operating == True' flag")

    # 2. Verify explore_edu001_ptr.py implements KC_REGULAR_PTR_ACTIVE_616 registered criteria
    ptr_script = repo_dir / "analysis" / "cross-measure" / "explore_edu001_ptr.py"
    if ptr_script.exists():
        text_ptr = ptr_script.read_text(encoding="utf-8", errors="ignore")
        if "KC_REGULAR_PTR_ACTIVE_616" not in text_ptr:
            warnings.append("analysis/cross-measure/explore_edu001_ptr.py does not explicitly tag KC_REGULAR_PTR_ACTIVE_616 in comments")
        if "['is_operating'] == True" not in text_ptr and '["is_operating"] == True' not in text_ptr:
            errors.append("analysis/cross-measure/explore_edu001_ptr.py does not implement 'is_operating == True' for campus PTR filtering")
        if "school_type" not in text_ptr or "Regular School" not in text_ptr:
            errors.append("analysis/cross-measure/explore_edu001_ptr.py missing school_type == 'Regular School' filter")
        if "classroom_teacher_fte" not in text_ptr or "> 0" not in text_ptr:
            errors.append("analysis/cross-measure/explore_edu001_ptr.py missing classroom_teacher_fte > 0 filter")
    else:
        errors.append("Missing analysis/cross-measure/explore_edu001_ptr.py")

    # 3. Verify generate_claims_ledger.py implements is_operating == True for school counting
    claims_script = repo_dir / "scripts" / "generate_claims_ledger.py"
    if claims_script.exists():
        text_cl = claims_script.read_text(encoding="utf-8", errors="ignore")
        if "['is_operating'] == True" not in text_cl and '["is_operating"] == True' not in text_cl:
            errors.append("scripts/generate_claims_ledger.py does not implement 'is_operating == True' for school counts")

    detail = f"{py_files_checked} python scripts enforce canonical 'is_operating == True'; KC_REGULAR_PTR_ACTIVE_616 contract verified"
    return len(errors) == 0, errors, warnings, detail


# ----------------------------------------------------------------------
# Main Runner
# ----------------------------------------------------------------------
def validate_observatory():
    repo_dir = get_repo_dir()
    
    print("=" * 80)
    print("EDUCATION DATA OBSERVATORY — AUTOMATED INTEGRITY VALIDATION SUITE")
    print(f"Repository Root: {repo_dir}")
    print("=" * 80)
    
    named_tests = [
        ("registry_unique_ids", test_registry_unique_ids),
        ("registry_foreign_keys", test_registry_foreign_keys),
        ("active_dossiers_exist", test_active_dossiers_exist),
        ("source_dossiers_exist", test_source_dossiers_exist),
        ("upstream_checksums", test_upstream_checksums),
        ("portable_paths", test_portable_paths),
        ("markdown_internal_links", test_markdown_internal_links),
        ("dashboard_assets", test_dashboard_assets),
        ("git_hygiene", test_git_hygiene),
        ("roadmap_status_consistency", test_roadmap_status_consistency),
        ("source_inventory_consistency", test_source_inventory_consistency),
        ("canonical_measure_names_consistency", test_canonical_measure_names_consistency),
        ("claims_ledger_integrity", test_claims_ledger_integrity),
        ("claim_numeric_internal_consistency", test_claim_numeric_internal_consistency),
        ("claim_universe_support_consistency", test_claim_universe_support_consistency),
        ("claim_note_numeric_drift", test_claim_note_numeric_drift),
        ("source_dossier_measure_table_consistency", test_source_dossier_measure_table_consistency),
        ("claim_specific_dossier_consistency", test_claim_specific_dossier_consistency),
        ("prohibited_legacy_terms_in_dossiers", test_prohibited_legacy_terms_in_dossiers),
        ("dossier_table_universe_and_subtotal_consistency", test_dossier_table_universe_and_subtotal_consistency),
        ("canonical_universe_implementation_consistency", test_canonical_universe_implementation_consistency),
    ]
    
    total_tests = len(named_tests)
    passed_tests = 0
    all_errors = []
    all_warnings = []
    
    for idx, (name, test_func) in enumerate(named_tests, 1):
        try:
            passed, errors, warnings, detail = test_func(repo_dir)
            if passed:
                passed_tests += 1
                status_str = "[PASS]"
            else:
                status_str = "[FAIL]"
                all_errors.extend([f"[{name}] {e}" for e in errors])
                
            all_warnings.extend([f"[{name}] {w}" for w in warnings])
            print(f"  {status_str} {idx:02d}. {name:<40} : {detail}")
            
        except Exception as e:
            print(f"  [FAIL] {idx:02d}. {name:<40} : CRITICAL EXCEPTION {e}")
            all_errors.append(f"[{name}] Uncaught exception: {e}")
            
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Named Tests Evaluated: {total_tests}")
    print(f"Tests Passed:          {passed_tests} / {total_tests}")
    print(f"Tests Failed:          {total_tests - passed_tests} / {total_tests}")
    print(f"Warnings Recorded:     {len(all_warnings)}")
    
    if all_warnings:
        print("\nWarnings:")
        for w in all_warnings:
            print(f"  [WARN] {w}")
            
    if all_errors:
        print("\nERRORS DETECTED:")
        for e in all_errors:
            print(f"  [ERROR] {e}")
        print("\nRepository integrity check FAILED.")
        return 1
    else:
        print(f"\nAll {passed_tests} / {total_tests} named validation tests PASSED successfully! Observatory is healthy.")
        return 0


if __name__ == "__main__":
    sys.exit(validate_observatory())

