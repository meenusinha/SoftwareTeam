#!/bin/bash
# Run the multi-repo agentic orchestration demo (v1.0.0)
set -e
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
exec bash "$ROOT_DIR/scripts/run.sh"
