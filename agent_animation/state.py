"""
State file interface for the agent animation window.

The CLI workflow writes agent state to STATE_FILE.
The animation window reads it to know what to display.

State file format (JSON):
{
    "agent":   "developer",          # one of: developer, architect, tester, product-owner, it, cost-analyst
    "state":   "typing",             # see sprites.STATE_CONFIG for valid states
    "message": "Reviewing PR #42…"   # short text shown in speech bubble (optional)
}
"""

import json
import os
import time
from pathlib import Path

STATE_FILE = Path(os.environ.get('AGENT_STATE_FILE', '/tmp/agent-state.json'))

_DEFAULT_STATE = {
    'agent':   'developer',
    'state':   'idle',
    'message': '',
}


def write(agent: str, state: str, message: str = '') -> None:
    """Write current agent state. Call this from CLI workflow steps."""
    data = {'agent': agent, 'state': state, 'message': message, 'ts': time.time()}
    STATE_FILE.write_text(json.dumps(data, indent=2))


def read() -> dict:
    """Read current agent state. Returns default if file missing or invalid."""
    try:
        data = json.loads(STATE_FILE.read_text())
        return {
            'agent':   data.get('agent', 'developer'),
            'state':   data.get('state', 'idle'),
            'message': data.get('message', ''),
            'ts':      data.get('ts', 0.0),
        }
    except Exception:
        return dict(_DEFAULT_STATE)


def clear() -> None:
    """Remove the state file (e.g., on workflow end)."""
    STATE_FILE.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Convenience helpers — call these directly from bash via:
#   python -c "from agent_animation.state import *; write('developer','typing','Writing code…')"
# ---------------------------------------------------------------------------

def set_thinking(agent: str, message: str = 'Thinking…') -> None:
    write(agent, 'thinking', message)

def set_typing(agent: str, message: str = 'Writing…') -> None:
    write(agent, 'typing', message)

def set_reviewing(agent: str, message: str = 'Reviewing…') -> None:
    write(agent, 'reviewing', message)

def set_reworking(agent: str, message: str = 'Addressing feedback…') -> None:
    write(agent, 'reworking', message)

def set_approved(agent: str, message: str = 'Approved! ✅') -> None:
    write(agent, 'approved', message)

def set_changes_requested(agent: str, message: str = 'Changes needed 🔴') -> None:
    write(agent, 'changes_requested', message)

def set_handingoff(agent: str, next_agent: str = '') -> None:
    msg = f'Handing off to {next_agent}…' if next_agent else 'Handing off…'
    write(agent, 'handingoff', msg)

def set_celebrating(agent: str, message: str = 'Merged! 🎉') -> None:
    write(agent, 'celebrating', message)

def set_waiting(agent: str, message: str = 'Waiting for user…') -> None:
    write(agent, 'waiting', message)

def set_idle(agent: str, message: str = '') -> None:
    write(agent, 'idle', message)
