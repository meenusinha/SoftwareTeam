#!/usr/bin/env bash
# Start the agent animation window.
# Usage: bash scripts/start-animation.sh [--demo]
set -e
cd "$(dirname "$0")/.."
python -m agent_animation.agent_window "$@"
