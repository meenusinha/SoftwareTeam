"""
Agent Animation Window
======================
An always-on-top Tkinter window that shows a pixel-art sprite of the currently
active workflow agent.  The character stands in front of a pixel-art desk with
a keyboard; in typing states the hands animate pressing keys.

Layout (top → bottom in canvas):
  4px gap
  sprite (144px tall, 16 rows × 9px)   [full character visible]
  keyboard (16px tall, overlaps sprite feet — looks like desk in front)
  desk surface strip (5px)
  desk front panel (22px)
  4px margin

Usage:
    python -m agent_animation.agent_window          # reads /tmp/agent-state.json
    python -m agent_animation.agent_window --demo   # cycles through all agents/states

Native OS window decorations provide minimize / maximize / close.
Press Escape to close.
"""

import tkinter as tk
import math
import time
import random
import argparse
import glob
import os
import sys

from .sprites import PALETTE, CELL, get_agent, get_state_config, AGENTS, STATE_CONFIG
from .state import read as read_state

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
SPRITE_COLS = 14
SPRITE_ROWS = 16
SPRITE_W    = SPRITE_COLS * CELL    # 126 px
SPRITE_H    = SPRITE_ROWS * CELL    # 144 px

KBD_W       = 150
KBD_H       = 16                    # keyboard body height
DESK_SURF   = 5                     # desk surface strip height
DESK_PANEL  = 22                    # desk front panel height

WIN_W       = 290
# Canvas: sprite + keyboard (overlaps last 12px of sprite) + desk surf + desk panel + margin
CANVAS_H    = SPRITE_H + KBD_H + DESK_SURF + DESK_PANEL + 8  # ~211
LABEL_H     = 46                    # agent name row
BUBBLE_H    = 82                    # speech bubble
WIN_H       = CANVAS_H + LABEL_H + BUBBLE_H + 10

BG          = '#1E1E2E'
FONT_LABEL  = ('Courier', 18, 'bold')
FONT_STATUS = ('Courier', 13)
FONT_HEADER = ('Courier', 9)

POLL_MS     = 800
BOB_PERIOD  = 1.4

# How far the keyboard overlaps the sprite bottom (covers feet row)
KBD_OVERLAP = 12


class AgentWindow:
    def __init__(self, root: tk.Tk, demo: bool = False):
        self.root  = root
        self.demo  = demo

        self._agent_name        = 'developer'
        self._state_name        = 'idle'
        self._message           = ''
        self._frame_idx         = 0
        self._start_time        = time.time()
        self._state_change_time = time.time()
        self._state_file_ts     = time.time()   # timestamp from the state file itself

        self._demo_agents = list(AGENTS.keys())
        self._demo_states = list(STATE_CONFIG.keys())
        self._demo_ai = self._demo_si = 0
        self._demo_ts = time.time()

        self._build_window()
        self._schedule_poll()
        self._schedule_frame()

    # -----------------------------------------------------------------------
    # Window construction
    # -----------------------------------------------------------------------
    def _build_window(self):
        r = self.root
        r.title('⬡ SoftwareTeam Agents')
        r.geometry(f'{WIN_W}x{WIN_H}+80+80')
        r.resizable(True, True)
        r.configure(bg=BG)
        r.attributes('-topmost', True)

        try:
            r.attributes('-alpha', 0.97)
        except tk.TclError:
            pass

        # Coloured border frame (changes with agent state)
        self._border_frame = tk.Frame(r, bg='#888888', padx=2, pady=2)
        self._border_frame.pack(fill='both', expand=True)

        inner = tk.Frame(self._border_frame, bg=BG)
        inner.pack(fill='both', expand=True)

        # Small decorative header strip
        header = tk.Frame(inner, bg='#252540', height=18)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text='● active agent', bg='#252540', fg='#7777AA',
                 font=FONT_HEADER, anchor='w').pack(side='left', padx=8)

        # Canvas — sprite + keyboard + desk
        self._canvas = tk.Canvas(inner, width=WIN_W - 8, height=CANVAS_H,
                                 bg=BG, highlightthickness=0)
        self._canvas.pack(pady=(4, 0))

        # Agent name label
        self._name_lbl = tk.Label(inner, text='Developer',
                                  bg=BG, fg='#66EE88',
                                  font=FONT_LABEL, anchor='center')
        self._name_lbl.pack(fill='x', padx=4)

        # Speech bubble
        self._bubble_frame = tk.Frame(inner, bg='#EEEEFF', padx=6, pady=5)
        self._bubble_frame.pack(fill='x', padx=6, pady=(2, 6))

        self._bubble_icon = tk.Label(self._bubble_frame, text='💤',
                                     bg='#EEEEFF', font=('Courier', 16))
        self._bubble_icon.pack(side='left')

        self._bubble_lbl = tk.Label(self._bubble_frame, text='Idle',
                                    bg='#EEEEFF', fg='#111133',
                                    font=FONT_STATUS, anchor='w',
                                    wraplength=WIN_W - 76, justify='left')
        self._bubble_lbl.pack(side='left', fill='x', expand=True)

        r.bind('<Escape>', lambda e: r.destroy())

    # -----------------------------------------------------------------------
    # State polling
    # -----------------------------------------------------------------------
    def _schedule_poll(self):
        self._poll()
        self.root.after(POLL_MS, self._schedule_poll)

    def _poll(self):
        self.root.attributes('-topmost', True)
        self.root.lift()
        if self.demo:
            self._advance_demo()
            return
        s = read_state()
        if s['agent'] != self._agent_name or s['state'] != self._state_name:
            self._frame_idx         = 0
            self._state_change_time = time.time()
        self._agent_name    = s['agent']
        self._state_name    = s['state']
        self._message       = s['message']
        self._state_file_ts = s['ts'] if s['ts'] else self._state_file_ts

    def _advance_demo(self):
        now = time.time()
        if now - self._demo_ts < 2.5:
            return
        self._demo_ts = now
        self._demo_si += 1
        if self._demo_si >= len(self._demo_states):
            self._demo_si = 0
            self._demo_ai = (self._demo_ai + 1) % len(self._demo_agents)
        self._agent_name = self._demo_agents[self._demo_ai]
        self._state_name = self._demo_states[self._demo_si]
        self._message    = f'Demo: {self._agent_name} / {self._state_name}'
        self._frame_idx  = 0

    # -----------------------------------------------------------------------
    # Render loop
    # -----------------------------------------------------------------------
    def _schedule_frame(self):
        self._render_frame()
        sc       = get_state_config(self._state_name)
        interval = max(80, int(1000 / sc['fps']))
        self.root.after(interval, self._schedule_frame)

    # Seconds in 'handingoff' before auto-transitioning display to 'waiting'.
    # Reliable because 'handingoff' is only ever set when asking the handover
    # question — the agent then stops, so 4 s of silence means it is waiting.
    _HANDOFF_WAIT_SECS = 4.0

    def _render_frame(self):
        agent_cfg = get_agent(self._agent_name)

        display_state = self._state_name
        display_msg   = self._message

        # Only auto-transition handingoff → waiting (reliable signal).
        # A general quiet-timer is intentionally NOT used here because long
        # operations (npm install, code generation, running tests) also produce
        # silence and would cause false "waiting for user input" displays.
        # For other questions/clarifications, agents must call:
        #   set-agent-state.sh {agent} waiting "Your question here..."
        # Permission dialogs are handled immediately by the PreToolUse hook.
        if (display_state == 'handingoff' and
                time.time() - self._state_change_time > self._HANDOFF_WAIT_SECS):
            display_state = 'waiting'
            display_msg   = 'Waiting for user input, please respond...'

        state_cfg = get_state_config(display_state)

        frames = agent_cfg[state_cfg['frames_key']]
        frame  = frames[self._frame_idx % len(frames)]
        self._frame_idx += 1

        bob_y = 0
        if state_cfg['bob']:
            elapsed = time.time() - self._start_time
            bob_y   = int(math.sin(elapsed * 2 * math.pi / BOB_PERIOD) * 2)

        c        = self._canvas
        canvas_w = WIN_W - 8          # 282
        cx       = canvas_w // 2      # 141
        ox       = cx - SPRITE_W // 2 # 141 - 63 = 78
        oy       = 4 + bob_y

        c.delete('all')

        # ------ 1. Draw full sprite ------
        for row_i, row in enumerate(frame):
            for col_i, ch in enumerate(row):
                color = PALETTE.get(ch)
                if color is None:
                    continue
                x1 = ox + col_i * CELL
                y1 = oy + row_i * CELL
                c.create_rectangle(x1, y1, x1 + CELL - 1, y1 + CELL - 1,
                                   fill=color, outline='')

        # State icon (top-right corner)
        icon = state_cfg['icon']
        c.create_text(ox + SPRITE_W - 2, oy + 4, text=icon,
                      anchor='ne', font=('Courier', 14))

        # Bright outline around the shoulder/body area to make arms pop
        body_x1 = ox + 2 * CELL
        body_x2 = ox + 12 * CELL
        body_y1 = oy + 8 * CELL
        body_y2 = oy + 12 * CELL
        agent_color = agent_cfg['color']
        c.create_rectangle(body_x1, body_y1, body_x2, body_y2,
                           outline=agent_color, fill='', width=1)

        # ------ 2. Arm lines: drawn BEFORE keyboard so keyboard covers their ends ------
        sprite_bottom = oy + SPRITE_H          # ~152
        kbd_y         = sprite_bottom - KBD_OVERLAP   # ~140
        kx            = cx - KBD_W // 2       # 141 - 75 = 66

        is_typing = state_cfg['frames_key'] == 'typing'
        l_hx, r_hx = self._get_hand_x(kx, is_typing)

        self._draw_arm_connections(c, ox, oy, kx, kbd_y, agent_cfg, l_hx, r_hx)

        # ------ 3. Keyboard (painted over sprite feet — appears as foreground desk) ------
        self._draw_keyboard(c, kx, kbd_y, KBD_W, KBD_H)

        # ------ 4. Desk surface + panel (below keyboard) ------
        desk_top = kbd_y + KBD_H              # ~156
        desk_w   = KBD_W + 40                 # 190
        dkx      = cx - desk_w // 2           # 141 - 95 = 46

        # Desk surface (lighter strip visible above panel)
        c.create_rectangle(dkx, desk_top,
                           dkx + desk_w, desk_top + DESK_SURF,
                           fill='#3E3E70', outline='')
        c.create_line(dkx, desk_top, dkx + desk_w, desk_top,
                      fill='#8888CC', width=1)

        # Desk front panel drop-shadow
        c.create_rectangle(dkx + 3, desk_top + DESK_SURF + 3,
                           dkx + desk_w + 3, desk_top + DESK_SURF + DESK_PANEL + 3,
                           fill='#111122', outline='')
        # Desk front panel
        c.create_rectangle(dkx, desk_top + DESK_SURF,
                           dkx + desk_w, desk_top + DESK_SURF + DESK_PANEL,
                           fill='#2A2A50', outline='#5555AA', width=1)

        # ------ 5. Hands on keyboard ------
        self._draw_hands(c, kx, kbd_y, state_cfg, l_hx, r_hx)

        # ------ 6. Update UI labels ------
        border_color = state_cfg['border_color']
        if display_state == 'celebrating':
            border_color = random.choice(
                ['#FF5566', '#55FF88', '#5566FF', '#FFEE44', '#FF55FF'])
        self._border_frame.configure(bg=border_color)

        bubble_bg = state_cfg['bubble_color']
        message   = display_msg or _default_message(display_state)
        self._bubble_frame.configure(bg=bubble_bg)
        self._bubble_icon.configure(bg=bubble_bg, text=icon)
        self._bubble_lbl.configure(bg=bubble_bg, fg='#111133', text=message)

        self._name_lbl.configure(
            text=agent_cfg['label'], fg=agent_cfg['color'])

    # -----------------------------------------------------------------------
    # Arm connections (sleeve lines bridging sprite body → keyboard)
    # -----------------------------------------------------------------------
    def _draw_arm_connections(self, c, ox, oy, kx, kbd_y, agent_cfg, l_hx, r_hx):
        """
        Draw two sleeve-colored lines from the sprite shoulders down to the
        current hand positions so arms visually track wherever the hands have
        drifted on the keyboard.
        """
        color = agent_cfg['color']

        sh_y   = oy + 8 * CELL
        l_x_sh = ox + 2 * CELL + 2
        r_x_sh = ox + 12 * CELL - 2

        # Track to hand centres (hands are 22px wide)
        l_x_kd = l_hx + 11
        r_x_kd = r_hx + 11
        tgt_y  = kbd_y + KBD_H

        elbow_y   = sh_y + (tgt_y - sh_y) // 2
        l_elbow_x = l_x_sh - 18
        r_elbow_x = r_x_sh + 18

        w = CELL - 2
        c.create_line(l_x_sh, sh_y, l_elbow_x, elbow_y, l_x_kd, tgt_y,
                      fill=color, width=w, capstyle='round', smooth=True)
        c.create_line(r_x_sh, sh_y, r_elbow_x, elbow_y, r_x_kd, tgt_y,
                      fill=color, width=w, capstyle='round', smooth=True)

    # -----------------------------------------------------------------------
    # Keyboard
    # -----------------------------------------------------------------------
    def _draw_keyboard(self, c, kx, ky, kw, kh):
        # Drop shadow
        c.create_rectangle(kx + 3, ky + 3, kx + kw + 3, ky + kh + 3,
                           fill='#111122', outline='')
        # Body
        c.create_rectangle(kx, ky, kx + kw, ky + kh,
                           fill='#252545', outline='#5555AA', width=1)
        # Inner bevel
        c.create_line(kx + 1, ky + 1, kx + kw - 1, ky + 1, fill='#4444AA')
        c.create_line(kx + 1, ky + 1, kx + 1,      ky + kh - 1, fill='#4444AA')

        # Three rows of keys
        kh_key, gap = 4, 2
        row_y0 = ky + 2
        self._draw_key_row(c, kx + 4,  row_y0,                    kw - 8,  11, kh_key, gap)
        self._draw_key_row(c, kx + 7,  row_y0 + kh_key + gap,     kw - 12, 10, kh_key, gap)
        self._draw_key_row(c, kx + 10, row_y0 + 2*(kh_key + gap), kw - 16,  8, kh_key, gap)

    def _draw_key_row(self, c, rx, ry, row_w, n, kh, gap):
        kw = max(3, (row_w - gap * (n - 1)) // n)
        for i in range(n):
            x1 = rx + i * (kw + gap)
            c.create_rectangle(x1, ry, x1 + kw, ry + kh,
                               fill='#3A3A72', outline='#6666AA', width=1)
            c.create_line(x1 + 1, ry + 1, x1 + kw - 1, ry + 1, fill='#8888CC')

    # -----------------------------------------------------------------------
    # Hands
    # -----------------------------------------------------------------------

    # Typing finger patterns: 8-frame cycle — (left_offsets[4], right_offsets[4])
    # Fingers ordered left→right on the hand (fi=0 outermost, fi=3 innermost/index)
    # For left hand:  fi=0 pinky … fi=3 index
    # For right hand: fi=0 index … fi=3 pinky
    # Press depth 5px — visible against keyboard background
    _TYPING_PATTERNS = [
        ([0, 0, 0, 5], [0, 0, 0, 0]),   # left index presses
        ([0, 0, 0, 0], [5, 0, 0, 0]),   # right index presses
        ([0, 0, 5, 0], [0, 0, 0, 0]),   # left middle presses
        ([0, 0, 0, 0], [0, 5, 0, 0]),   # right middle presses
        ([0, 5, 0, 5], [0, 0, 0, 0]),   # left middle+ring
        ([0, 0, 0, 0], [0, 5, 0, 5]),   # right middle+ring
        ([0, 0, 5, 0], [5, 0, 0, 0]),   # left middle + right index (cross)
        ([0, 5, 0, 0], [0, 0, 5, 0]),   # left ring   + right middle (cross)
    ]

    def _get_hand_x(self, kx, is_typing):
        """Return (l_hx, r_hx) — hand left-edge x positions.
        In typing state the hands drift slowly across the keyboard and back,
        giving the impression of reaching for different key regions."""
        l_base = kx + 18
        r_base = kx + KBD_W - 40
        if not is_typing:
            return l_base, r_base

        t = time.time()
        # Left hand drifts rightward ±16px over ~3s; right hand independent phase
        l_drift = int(math.sin(t * math.pi / 1.5) * 16)
        r_drift = int(math.sin(t * math.pi / 1.5 + math.pi * 0.8) * 16)
        # Clamp so hands stay on their respective halves of the keyboard
        l_hx = max(kx + 5,            min(kx + KBD_W // 2 - 24, l_base + l_drift))
        r_hx = max(kx + KBD_W // 2,   min(kx + KBD_W - 25,      r_base - r_drift))
        return l_hx, r_hx

    def _draw_hands(self, c, kx, kbd_y, state_cfg, l_hx, r_hx):
        """
        Draw two symmetric hands resting on / pressing the keyboard.
        Left hand:  thumb on RIGHT/inner side (points toward centre).
        Right hand: thumb on LEFT/inner side  (points toward centre).
        """
        skin   = '#FFCC99'
        shadow = '#CC9966'
        base_y = kbd_y + 1

        is_typing = state_cfg['frames_key'] == 'typing'
        if is_typing:
            pattern = self._TYPING_PATTERNS[self._frame_idx % len(self._TYPING_PATTERNS)]
            l_offsets, r_offsets = pattern
        else:
            l_offsets = r_offsets = [0, 0, 0, 0]

        # Left hand:  thumb_right=True  → thumb on right/inner side
        # Right hand: thumb_right=False → thumb on left/inner side
        self._draw_hand(c, l_hx, base_y, skin, shadow,
                        thumb_right=True,  finger_offsets=l_offsets)
        self._draw_hand(c, r_hx, base_y, skin, shadow,
                        thumb_right=False, finger_offsets=r_offsets)

    def _draw_hand(self, c, hx, hy, skin, shadow, thumb_right=False, finger_offsets=None):
        """
        Draw a top-down hand: palm + 4 finger stubs + thumb.
        thumb_right=True  → thumb on right side of palm (left hand viewed from above).
        thumb_right=False → thumb on left side of palm  (right hand viewed from above).
        finger_offsets: 4 ints, positive = finger pressed downward.
        """
        if finger_offsets is None:
            finger_offsets = [0, 0, 0, 0]

        # Palm
        c.create_oval(hx, hy, hx + 22, hy + 10,
                      fill=skin, outline=shadow, width=1)

        # Four finger stubs above palm (fi=0 leftmost, fi=3 rightmost)
        for fi in range(4):
            fx  = hx + 2 + fi * 5
            fh  = 7 if fi in (1, 2) else 5
            fdy = finger_offsets[fi]
            c.create_rectangle(fx, hy - fh + fdy, fx + 4, hy + 2 + fdy,
                               fill=skin, outline=shadow, width=1)

        # Thumb — inner side (both thumbs point toward each other, naturally)
        if thumb_right:
            # Left hand: thumb on right inner side
            c.create_oval(hx + 17, hy + 2, hx + 26, hy + 9,
                          fill=skin, outline=shadow, width=1)
        else:
            # Right hand: thumb on left inner side
            c.create_oval(hx - 4, hy + 2, hx + 5, hy + 9,
                          fill=skin, outline=shadow, width=1)


def _default_message(state: str) -> str:
    return {
        'idle':              'Idle…',
        'thinking':          'Thinking…',
        'reviewing':         'Reviewing code…',
        'typing':            'Writing…',
        'reworking':         'Addressing feedback…',
        'approved':          'All good! ✅',
        'changes_requested': 'Changes needed 🔴',
        'handingoff':        'Handing off…',
        'celebrating':       'Merged! 🎉',
        'waiting':           'Waiting for user input, please respond...',
    }.get(state, '')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def _ensure_display():
    """
    On Wayland sessions (Fedora, Ubuntu with Wayland, etc.) DISPLAY is not set
    but XWayland is usually running and exposes an X11 socket.  Try to find it
    so Tkinter can connect.
    """
    if os.environ.get('DISPLAY'):
        return  # already set, nothing to do

    # Look for any live X11 socket under /tmp/.X11-unix/
    sockets = sorted(glob.glob('/tmp/.X11-unix/X*'))
    for sock in sockets:
        if os.path.exists(sock):
            display_num = sock.replace('/tmp/.X11-unix/X', '')
            os.environ['DISPLAY'] = f':{display_num}'
            return

    # Fallback: :0 is the conventional XWayland display
    os.environ['DISPLAY'] = ':0'


def main():
    parser = argparse.ArgumentParser(description='Agent animation floating window')
    parser.add_argument('--demo', action='store_true',
                        help='Cycle through all agents and states automatically')
    args = parser.parse_args()

    # Ensure DISPLAY is set before Tkinter tries to open it (needed on Wayland)
    _ensure_display()

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        # Provide an actionable error instead of a silent crash into the log
        print(f'[agent_animation] Cannot open display: {exc}', file=sys.stderr)
        print('[agent_animation] Suggestions:', file=sys.stderr)
        print('  - Run: export DISPLAY=:0  (XWayland must be running)', file=sys.stderr)
        print('  - Or install XWayland:    sudo dnf install xorg-x11-server-Xwayland',
              file=sys.stderr)
        sys.exit(1)

    AgentWindow(root, demo=args.demo)
    root.mainloop()


if __name__ == '__main__':
    main()
