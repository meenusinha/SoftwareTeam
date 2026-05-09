#!/bin/bash
set -e

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

# Load .env if present
if [ -f .env ]; then
  set -a; source .env; set +a
fi

# Check GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
  echo "ERROR: GITHUB_TOKEN is not set."
  echo "Create a .env file with: GITHUB_TOKEN=your-github-token"
  echo "Generate a token (models:read scope) at: https://github.com/settings/tokens"
  exit 1
fi

# Create and activate venv if missing
if [ ! -d ".venv" ]; then
  echo "Setting up Python virtual environment..."
  python3 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
  echo "Dependencies installed."
fi

echo ""
echo "Starting Multi-Repo Agentic Orchestration Demo..."
echo ""
.venv/bin/python orchestrator/demo/run_demo.py
