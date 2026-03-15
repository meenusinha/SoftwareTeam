#!/usr/bin/env bash
# Write agent state from a shell workflow step.
# Usage: bash scripts/set-agent-state.sh <agent> <state> [message]
#
# Examples:
#   bash scripts/set-agent-state.sh developer typing "Writing code for PR #42"
#   bash scripts/set-agent-state.sh architect reviewing "Checking design patterns"
#   bash scripts/set-agent-state.sh tester approved "All tests pass"

cd "$(dirname "$0")/.."

# Auto-start animation window if not already running (safe — duplicate guard is in start-animation.sh)
bash scripts/start-animation.sh

AGENT="${1:-developer}"
STATE="${2:-idle}"
MSG="${3:-}"
python -c "
from agent_animation.state import write
write('$AGENT', '$STATE', '$MSG')
print(f'State: $AGENT / $STATE')
"
