#!/bin/bash
# Run the Distributed Independent Repo Agents demo
set -e
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT_DIR"
if [ -f .env ]; then set -a; source .env; set +a; fi
if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then source "$ROOT_DIR/.venv/bin/activate"; fi
export PYTHONPATH="$ROOT_DIR"
python orchestrator/demo/run_demo.py
