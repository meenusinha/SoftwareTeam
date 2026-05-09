#!/bin/bash

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "=========================================="
echo "Cleaning build artifacts..."
echo "=========================================="

rm -rf .venv
rm -rf .chroma_db
rm -rf __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f /tmp/test_illumination /tmp/test_scan_manager /tmp/test_expose_sequence
rm -rf /tmp/gen-cpp

echo "Clean complete."
