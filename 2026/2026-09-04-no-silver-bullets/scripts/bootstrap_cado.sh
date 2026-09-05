#!/usr/bin/env bash
# bootstrap_cado.sh: Automates CADO-NFS checkout, dependency check, and compilation.
# Pinned to development commit 73ca6b6847118b05b15eeec27c86f45cef82a19e

set -euo pipefail

PINNED_COMMIT="73ca6b6847118b05b15eeec27c86f45cef82a19e"
CADO_DIR="${1:-${CADO_NFS_ROOT:-./cado-nfs}}"
REPO_URL="https://gitlab.inria.fr/cado-nfs/cado-nfs.git"
FALLBACK_URL="https://github.com/cado-nfs/cado-nfs.git"

echo "=== CADO-NFS Bootstrap ==="
echo "Target directory: ${CADO_DIR}"
echo "Pinned commit:    ${PINNED_COMMIT}"

# Check for apt-get on Debian/Ubuntu
if command -v apt-get >/dev/null 2>&1; then
    echo "Checking / installing required system packages..."
    sudo apt-get update -qq || true
    sudo apt-get install -y -qq build-essential cmake libgmp-dev libhwloc-dev python3 git || true
fi

# Clone or fetch
if [ ! -d "${CADO_DIR}/.git" ]; then
    echo "Cloning CADO-NFS repository..."
    git clone "${REPO_URL}" "${CADO_DIR}" || git clone "${FALLBACK_URL}" "${CADO_DIR}"
fi

cd "${CADO_DIR}"

echo "Checking out pinned commit: ${PINNED_COMMIT}..."
git fetch --all --tags -q || true
git checkout -q "${PINNED_COMMIT}"

ACTUAL_COMMIT=$(git rev-parse HEAD)
if [ "${ACTUAL_COMMIT}" != "${PINNED_COMMIT}" ]; then
    echo "ERROR: Checkout failed. Expected ${PINNED_COMMIT}, got ${ACTUAL_COMMIT}" >&2
    exit 1
fi
echo "Verified commit: ${ACTUAL_COMMIT}"

echo "Compiling CADO-NFS into deterministic build/nsb-r3 (this may take several minutes)..."
NPROCS=$(nproc 2>/dev/null || echo 4)
# Enforce fresh empty build directory for canonical certification
if [ -d "build/nsb-r3" ]; then
    echo "Cleaning existing build/nsb-r3 to enforce fresh empty build directory for certification..."
    rm -rf build/nsb-r3
fi
cmake -B build/nsb-r3 -DCMAKE_BUILD_TYPE=Release .
cmake --build build/nsb-r3 -j"${NPROCS}"

echo "Compilation finished successfully."
echo "Running environment check..."
cd - >/dev/null
python3 scripts/verify_cado_environment.py --cado-root "${CADO_DIR}"
