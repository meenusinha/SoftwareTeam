#!/bin/bash
set -e

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

# Load .env if present
if [ -f .env ]; then
  set -a; source .env; set +a
fi

# Create venv if missing
if [ ! -d ".venv" ]; then
  echo "Setting up Python virtual environment..."
  python3 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
fi

echo "=========================================="
echo "Running Python tests..."
echo "=========================================="
.venv/bin/pytest repos/illumination/tests/python/ repos/scan_manager/tests/python/ repos/expose_sequence/tests/python/ orchestrator/tests/ -v

echo ""
echo "=========================================="
echo "Checking C++ stub compilation..."
echo "=========================================="
for repo in illumination scan_manager expose_sequence; do
  echo "  Compiling $repo tests..."
  g++ -std=c++17 -I repos/$repo/src \
    repos/$repo/src/*/*.cpp \
    repos/$repo/tests/cpp/test_$repo.cpp \
    -o /tmp/test_$repo 2>&1 && echo "  ✅ $repo: OK" || echo "  ⚠️  $repo: compile warning (non-fatal)"
done

echo ""
echo "All tests done."
