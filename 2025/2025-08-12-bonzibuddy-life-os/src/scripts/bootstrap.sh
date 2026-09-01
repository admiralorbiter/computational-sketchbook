#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p var backups
python scripts/db_apply.py
echo "Bootstrap complete. Run: make dev"
