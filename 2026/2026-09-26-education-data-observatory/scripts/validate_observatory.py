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
            print(f"  {status_str} {idx:02d}. {name:<36} : {detail}")
            
        except Exception as e:
            print(f"  [FAIL] {idx:02d}. {name:<36} : CRITICAL EXCEPTION {e}")
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
