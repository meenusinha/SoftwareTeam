#!/bin/bash
set -e

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

# Load .env if present
if [ -f .env ]; then
  set -a; source .env; set +a
fi

# Create and activate venv if missing
if [ ! -d ".venv" ]; then
  echo "Setting up Python virtual environment..."
  python3 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
  echo "Dependencies installed."
fi

if [ -z "$GITHUB_TOKEN" ]; then
  echo ""
  echo "NOTE: GITHUB_TOKEN not set — running in RAG-only mode (no LLM summary)."
  echo "The orchestrator and knowledge retrieval steps will still run fully."
  echo "For LLM synthesis: add GITHUB_TOKEN to .env (github.com/settings/tokens)"
  echo "For VS Code Copilot mode (full experience, zero tokens): open the .code-workspace files."
  echo ""
fi

echo "Starting Multi-Repo Agentic Orchestration Demo..."
echo ""
.venv/bin/python orchestrator/demo/run_demo.py
