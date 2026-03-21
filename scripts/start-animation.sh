#!/usr/bin/env bash
# Start the agent animation window (skips launch if already running).
# Usage: bash scripts/start-animation.sh [--demo]
cd "$(dirname "$0")/.."

# Only one instance at a time
if pgrep -f "agent_animation.agent_window" > /dev/null 2>&1; then
  exit 0
fi

# On Wayland sessions (e.g. Fedora default), DISPLAY is not set but XWayland
# is usually running.  Find the first X11 socket and export DISPLAY so Tkinter
# can connect to it.
if [ -z "$DISPLAY" ]; then
  if [ -n "$WAYLAND_DISPLAY" ] || [ -n "$XDG_SESSION_TYPE" ]; then
    for _x in /tmp/.X11-unix/X*; do
      [ -S "$_x" ] && export DISPLAY=":${_x##*X}" && break
    done
  fi
  # If still unset, fall back to :0 which is the conventional XWayland display
  if [ -z "$DISPLAY" ] && [ -e /tmp/.X11-unix/X0 ]; then
    export DISPLAY=:0
  fi
fi

# Reset to initial IT agent state so stale state from a previous session is cleared
python -c "from agent_animation.state import write; write('it', 'idle', 'Ready...')" 2>/dev/null || true

# nohup + redirect so the window process survives the calling shell exiting.
# Errors are logged to /tmp/agent-animation.log for debugging.
nohup python -m agent_animation.agent_window "$@" \
  </dev/null >>/tmp/agent-animation.log 2>&1 &
