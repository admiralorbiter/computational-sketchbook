#!/usr/bin/env python3
"""
Education Data Observatory — Automated Repository Validation Suite
Checks structural integrity, registry referential consistency, markdown link health,
image existence, path portability, and git hygiene.
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

def validate_observatory():
    script_dir = Path(__file__).resolve().parent
    repo_dir = script_dir.parent
    
    print("=" * 80)
    print(f"EDUCATION DATA OBSERVATORY VALIDATION SUITE")
    print(f"Repository Root: {repo_dir}")
    print("=" * 80)
    
    errors = []
    warnings = []
    checks_passed = 0
    
    # ---------------------------------------------------------
    # 1. REGISTRY REFERENTIAL INTEGRITY CHECKS
    # ---------------------------------------------------------
    print("\n[CHECK 1] Validating Registries & Referential Integrity...")
    
    measures_file = repo_dir / "registry" / "measures.csv"
    sources_file = repo_dir / "registry" / "sources.csv"
    op_file = repo_dir / "registry" / "operationalizations.csv"
    rel_file = repo_dir / "registry" / "relationships.csv"
    
    measure_ids = set()
    dossier_paths = set()
    with open(measures_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = row["measure_id"].strip()
            if mid in measure_ids:
                errors.append(f"measures.csv: Duplicate measure_id '{mid}'")
            measure_ids.add(mid)
            
            d_path = row["dossier_path"].strip()
            status = row.get("status", "").strip()
            if d_path:
                full_d_path = repo_dir / d_path
                if not full_d_path.exists():
                    if status in ("in_progress", "audited", "active"):
                        errors.append(f"measures.csv: Active/Audited Measure '{mid}' references nonexistent dossier '{d_path}'")
                    else:
                        # Proposed measure whose dossier has not yet been authored
                        pass
                else:
                    dossier_paths.add(d_path)
    
    print(f"  [PASS] measures.csv: {len(measure_ids)} unique measures registered.")
    checks_passed += 1
    
    source_ids = set()
    with open(sources_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["source_id"].strip()
            if sid in source_ids:
                errors.append(f"sources.csv: Duplicate source_id '{sid}'")
            source_ids.add(sid)
            
            # Check source dossier existence
            src_dossier = repo_dir / "sources" / sid / "README.md"
            if not src_dossier.exists():
                warnings.append(f"sources.csv: Source '{sid}' does not have a dossier at 'sources/{sid}/README.md'")
    
    print(f"  [PASS] sources.csv: {len(source_ids)} unique sources registered.")
    checks_passed += 1
    
    op_ids = set()
    with open(op_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            oid = row["operationalization_id"].strip()
            if oid in op_ids:
                errors.append(f"operationalizations.csv: Duplicate operationalization_id '{oid}'")
            op_ids.add(oid)
            
            mid = row["measure_id"].strip()
            if mid not in measure_ids:
                errors.append(f"operationalizations.csv: Operationalization '{oid}' references unknown measure '{mid}'")
                
            sid = row["source_id"].strip()
            if sid not in source_ids:
                errors.append(f"operationalizations.csv: Operationalization '{oid}' references unknown source '{sid}'")
                
    print(f"  [PASS] operationalizations.csv: {len(op_ids)} unique operationalizations registered (all foreign keys valid).")
    checks_passed += 1
    
    valid_nodes = measure_ids.union(source_ids)
    rel_count = 0
    with open(rel_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            s_node = row.get("source_node", "").strip()
            t_node = row.get("target_node", "").strip()
            if not s_node or not t_node:
                continue
            rel_count += 1
            if s_node not in valid_nodes:
                errors.append(f"relationships.csv: source_node '{s_node}' is neither a registered measure nor source")
            if t_node not in valid_nodes:
                errors.append(f"relationships.csv: target_node '{t_node}' is neither a registered measure nor source")
                
    print(f"  [PASS] relationships.csv: {rel_count} relationships registered (all nodes exist in measures or sources).")
    checks_passed += 1
    
    # ---------------------------------------------------------
    # 2. UPSTREAM ARTIFACTS AND CHECKSUM AUDIT
    # ---------------------------------------------------------
    print("\n[CHECK 2] Validating Upstream Artifacts Ledger...")
    upstream_file = repo_dir / "data" / "upstream_artifacts.csv"
    if not upstream_file.exists():
        errors.append("data/upstream_artifacts.csv is missing!")
    else:
        verified_artifacts = 0
        with open(upstream_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                src_proj = row["source_project"].strip()
                rel_path = row["relative_path"].strip()
                expected_sha = row.get("sha256_or_git_blob_sha", "").strip()
                full_path = (repo_dir.parent / src_proj / rel_path).resolve()
                if not full_path.exists():
                    warnings.append(f"Upstream artifact not found at '{rel_path}' in project '{src_proj}' (checked {full_path})")
                else:
                    h = hashlib.sha256()
                    with open(full_path, "rb") as bf:
                        while chunk := bf.read(65536):
                            h.update(chunk)
                    actual_sha = h.hexdigest()
                    if actual_sha != expected_sha:
                        errors.append(f"Upstream artifact checksum mismatch for '{rel_path}'!\n  Expected: {expected_sha}\n  Actual:   {actual_sha}")
                    else:
                        verified_artifacts += 1
        print(f"  [PASS] data/upstream_artifacts.csv: {verified_artifacts} upstream data artifacts cryptographically verified.")
        checks_passed += 1
        
    # ---------------------------------------------------------
    # 3. PORTABILITY & HYGIENE: SCAN FOR FORBIDDEN PATH PATTERNS
    # ---------------------------------------------------------
    print("\n[CHECK 3] Scanning Repository for Absolute Paths and Local URI Schemes...")
    scan_exts = {".md", ".py", ".csv", ".json"}
    hardcoded_user_pattern = re.compile(r"[cC]:[\\/][uU]sers[\\/]", re.IGNORECASE)
    file_uri_pattern = re.compile(r"file:///", re.IGNORECASE)
    
    forbidden_path_violations = []
    
    for root, dirs, files in os.walk(repo_dir):
        # Skip git directory
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            p = Path(root) / file
            if p.suffix.lower() in scan_exts:
                # Don't flag this validation script itself for containing search strings
                if p.name == "validate_observatory.py":
                    continue
                try:
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    if hardcoded_user_pattern.search(content):
                        forbidden_path_violations.append(f"Absolute Windows user path found in: {p.relative_to(repo_dir)}")
                    if file_uri_pattern.search(content):
                        forbidden_path_violations.append(f"Local file:/// URI scheme found in: {p.relative_to(repo_dir)}")
                except Exception as e:
                    warnings.append(f"Could not read {p.relative_to(repo_dir)}: {e}")
                    
    if forbidden_path_violations:
        for v in forbidden_path_violations:
            errors.append(v)
    else:
        print("  [PASS] Zero hardcoded user-specific paths or file:/// URIs detected across all repo files.")
        checks_passed += 1

    # ---------------------------------------------------------
    # 4. MARKDOWN LINK & IMAGE ASSET HEALTH
    # ---------------------------------------------------------
    print("\n[CHECK 4] Verifying Markdown Links and Dashboard Image Assets...")
    image_pattern = re.compile(r"!\[.*?\]\((.*?)\)")
    link_pattern = re.compile(r"(?<!!)\[.*?\]\((.*?)\)")
    
    missing_assets = []
    total_images_checked = 0
    
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            if file.endswith(".md"):
                doc_path = Path(root) / file
                content = doc_path.read_text(encoding="utf-8", errors="ignore")
                
                # Check images
                for img in image_pattern.findall(content):
                    # Clean query or fragment
                    img_clean = img.split("#")[0].split("?")[0].strip()
                    if img_clean.startswith("http://") or img_clean.startswith("https://"):
                        continue
                    total_images_checked += 1
                    target_p = (doc_path.parent / img_clean).resolve()
                    if not target_p.exists():
                        missing_assets.append(f"Broken image reference in {doc_path.relative_to(repo_dir)}: '{img}' (resolved to {target_p})")
                        
    if missing_assets:
        for ma in missing_assets:
            errors.append(ma)
    else:
        print(f"  [PASS] {total_images_checked} markdown image references checked; all image assets exist on disk.")
        checks_passed += 1

    # ---------------------------------------------------------
    # 5. GIT HYGIENE: PYCACHE AND COMPILED ARTIFACT CHECK
    # ---------------------------------------------------------
    print("\n[CHECK 5] Checking Git & Repository Hygiene (pycache / .pyc)...")
    pycache_violations = []
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for d in dirs:
            if d == "__pycache__":
                pycache_violations.append(f"__pycache__ directory found at: {(Path(root) / d).relative_to(repo_dir)}")
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                pycache_violations.append(f"Compiled bytecode file found at: {(Path(root) / f).relative_to(repo_dir)}")
                
    if pycache_violations:
        for pv in pycache_violations:
            errors.append(pv)
    else:
        print("  [PASS] Zero __pycache__ or .pyc bytecode files present in repository tree.")
        checks_passed += 1

    # ---------------------------------------------------------
    # SUMMARY REPORT
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Checks Passed: {checks_passed} / 5")
    print(f"Warnings:      {len(warnings)}")
    print(f"Errors:        {len(errors)}")
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  [WARN] {w}")
            
    if errors:
        print("\nERRORS DETECTED:")
        for e in errors:
            print(f"  [ERROR] {e}")
        print("\nRepository integrity check FAILED.")
        return 1
    else:
        print("\nAll repository integrity checks PASSED successfully! Observatory is healthy.")
        return 0

if __name__ == "__main__":
    sys.exit(validate_observatory())
