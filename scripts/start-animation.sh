#!/usr/bin/env bash
# Start the agent animation window (skips launch if already running).
# Usage: bash scripts/start-animation.sh [--demo]
cd "$(dirname "$0")/.."

# Only one instance at a time
if pgrep -f "agent_animation.agent_window" > /dev/null 2>&1; then
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. Ensure DISPLAY is set (Wayland / XWayland)
# ---------------------------------------------------------------------------
if [ -z "$DISPLAY" ]; then
  for _x in /tmp/.X11-unix/X*; do
    [ -S "$_x" ] && export DISPLAY=":${_x##*X}" && break
  done
  [ -z "$DISPLAY" ] && export DISPLAY=:0
fi

# ---------------------------------------------------------------------------
# 2. Ensure tkinter is installed
#    On Fedora/RHEL it ships as a separate package (python3-tkinter).
#    Strategy:
#      a) Try passwordless sudo first (works if recent sudo session is active).
#      b) Fall back to opening a visible terminal so the user can type the
#         password — then wait (up to 90 s) for the install to finish.
# ---------------------------------------------------------------------------
if ! python -c "import tkinter" 2>/dev/null; then
  echo "[agent_animation] tkinter not found — attempting install" >>/tmp/agent-animation.log

  # Detect the right package + manager
  _TKPKG=""
  if   command -v dnf     >/dev/null 2>&1; then _TKPKG="dnf install -y python3-tkinter"
  elif command -v apt-get >/dev/null 2>&1; then _TKPKG="apt-get install -y python3-tk"
  elif command -v pacman  >/dev/null 2>&1; then _TKPKG="pacman -S --noconfirm tk"
  elif command -v zypper  >/dev/null 2>&1; then _TKPKG="zypper install -y python3-tk"
  fi

  if [ -n "$_TKPKG" ]; then
    # (a) Try non-interactive sudo (works if NOPASSWD or recent auth)
    if ! sudo -n $_TKPKG >>/tmp/agent-animation.log 2>&1; then
      # (b) Open a terminal so the user can authorise
      _FLAG="/tmp/agent-tkinter-done.$$"
      _CMD="sudo $_TKPKG && touch $_FLAG; echo '--- tkinter installed, closing in 3 s ---'; sleep 3"
      if   command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal -- bash -c "$_CMD" 2>/dev/null &
      elif command -v konsole >/dev/null 2>&1; then
        konsole -e bash -c "$_CMD" 2>/dev/null &
      elif command -v xterm >/dev/null 2>&1; then
        xterm -e "$_CMD" 2>/dev/null &
      fi
      # Wait up to 90 s for the flag file the install command creates
      _waited=0
      while [ $_waited -lt 90 ] && ! python -c "import tkinter" 2>/dev/null; do
        sleep 3; _waited=$((_waited + 3))
      done
      rm -f "$_FLAG"
    fi
  fi
fi

# ---------------------------------------------------------------------------
# 3. Reset to initial IT agent state
# ---------------------------------------------------------------------------
python -c "from agent_animation.state import write; write('it', 'idle', 'Ready...')" 2>/dev/null || true

# ---------------------------------------------------------------------------
# 4. Launch animation window (detached so it survives the calling shell)
# ---------------------------------------------------------------------------
nohup python -m agent_animation.agent_window "$@" \
  </dev/null >>/tmp/agent-animation.log 2>&1 &
