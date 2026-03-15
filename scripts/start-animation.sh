#!/usr/bin/env bash
# Start the agent animation window (skips launch if already running).
# Usage: bash scripts/start-animation.sh [--demo]
cd "$(dirname "$0")/.."

# Only one instance at a time
if pgrep -f "agent_animation.agent_window" > /dev/null 2>&1; then
  exit 0
fi

# nohup + redirect so the window process survives the calling shell exiting.
# Errors are logged to /tmp/agent-animation.log for debugging.
nohup python -m agent_animation.agent_window "$@" \
  </dev/null >>/tmp/agent-animation.log 2>&1 &
