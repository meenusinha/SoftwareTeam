# SoftwareTeam — Pixel Agent Animation Window

A small always-on-top floating window that shows **pixel-art animations** of
the active workflow agent (Developer, Architect, Tester, etc.) while you work
in your terminal or VS Code.

The window is **pure display** — it never interferes with the CLI workflow.

---

## What it looks like

```
┌─────────────────────┐
│ ● SoftwareTeam    ✕ │  ← draggable title bar
│                     │
│      [sprite]       │  ← pixel agent (14×16 cells, 9px/cell)
│       🔍            │  ← state icon overlay
│                     │
│    Architect        │  ← agent name (colored)
│ ┌─────────────────┐ │
│ │🔍 Reviewing…    │ │  ← speech bubble (state color)
│ └─────────────────┘ │
└─────────────────────┘
```

The border color changes with state:
- 🔵 Blue — reviewing
- 🟢 Green — typing / approved
- 🔴 Red — changes requested
- 🟡 Gold — celebrating / reworking
- ⚪ Gray — idle / waiting

---

## Quick start

### 1. Install (Python 3.10+ required, tkinter included)

```bash
# No extra packages needed — tkinter is part of the Python standard library
# On Ubuntu/Debian if tkinter is missing:
sudo apt-get install python3-tk

# On macOS with Homebrew Python:
brew install python-tk
```

### 2. Run the demo (cycles through all agents and states)

**Mac / Linux:**
```bash
bash scripts/start-animation.sh --demo
```

**Windows:**
```powershell
.\scripts\Start-Animation.ps1 -Demo
```

**Or directly:**
```bash
python -m agent_animation.agent_window --demo
```

### 3. Run alongside your workflow

**Step 1 — Start the window** (keep it running in background):
```bash
bash scripts/start-animation.sh &
```

**Step 2 — Update state from your workflow scripts:**
```bash
# Syntax: bash scripts/set-agent-state.sh <agent> <state> [message]
bash scripts/set-agent-state.sh developer typing "Writing sudoku solver…"
bash scripts/set-agent-state.sh architect reviewing "Checking design patterns"
bash scripts/set-agent-state.sh tester approved "All 42 tests pass ✅"
bash scripts/set-agent-state.sh developer celebrating "PR merged! 🎉"
```

**Or from Python:**
```python
from agent_animation import set_typing, set_approved, set_celebrating

set_typing('developer', 'Writing sudoku solver…')
# ... do work ...
set_approved('developer', 'Implementation complete ✅')
```

---

## Agent names

| Name | Display |
|------|---------|
| `developer` | Developer (green) |
| `architect` | Architect (orange) |
| `tester` | Tester (blue) |
| `product-owner` | Product Owner (navy) |
| `it` | IT Agent (purple) |
| `cost-analyst` | Cost Analyst (gold) |

## State names

| State | Border | Icon | Description |
|-------|--------|------|-------------|
| `idle` | gray | 💤 | Doing nothing |
| `thinking` | light gray | 🤔 | Pondering |
| `reviewing` | blue | 🔍 | Reading code/docs |
| `typing` | green | ⌨️ | Writing code/docs |
| `reworking` | orange | 🔧 | Addressing feedback |
| `approved` | green | ✅ | Approved! |
| `changes_requested` | red | 🔴 | Needs changes |
| `handingoff` | purple | 🤝 | Passing to next agent |
| `celebrating` | flicker | 🎉 | Workflow complete |
| `waiting` | gray | ⏳ | Waiting for user |

---

## State file

The window polls `/tmp/agent-state.json` every 800ms (configurable via
`AGENT_STATE_FILE` env var).

```json
{
  "agent":   "developer",
  "state":   "typing",
  "message": "Writing sudoku solver…",
  "ts":      1741440000.0
}
```

---

## Integration with BigProjPOC workflow

Add state updates to your agent scripts in `BigProjPOC`:

```bash
# In copilot-instructions / agent step scripts:
bash /path/to/SoftwareTeam/scripts/set-agent-state.sh developer typing "Implementing feature…"
# ... run agent ...
bash /path/to/SoftwareTeam/scripts/set-agent-state.sh developer handingoff "Tester"
```

---

## Controls

| Action | How |
|--------|-----|
| Move window | Click and drag anywhere |
| Close | Click ✕ or press Escape |
