#!/bin/bash
set -e

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
  source "$ROOT_DIR/.venv/bin/activate"
fi

echo "=========================================="
echo "Installing dependencies..."
echo "=========================================="

pip install -r requirements.txt

echo "=========================================="
echo "Build complete."
echo "=========================================="
