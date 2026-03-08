"""
Agent Animation Window
======================
An always-on-top floating Tkinter window that shows a pixel-art sprite of
the currently active workflow agent, with idle bob animation, state-based
border color and speech bubble.

Usage:
    python -m agent_animation.agent_window          # reads /tmp/agent-state.json
    python -m agent_animation.agent_window --demo   # cycles through all agents/states

Drag the window by clicking and dragging anywhere on it.
Close with the × button or press Escape.
"""

import tkinter as tk
import math
import time
import sys
import argparse
from typing import Optional

from .sprites import PALETTE, CELL, get_agent, get_state_config, AGENTS, STATE_CONFIG
from .state import read as read_state

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
SPRITE_COLS  = 14          # sprite grid width  (chars per row in sprite data)
SPRITE_ROWS  = 16          # sprite grid height (rows per sprite)
SPRITE_W     = SPRITE_COLS * CELL
SPRITE_H     = SPRITE_ROWS * CELL

WIN_W        = SPRITE_W + 24          # window width
BUBBLE_H     = 56                     # speech bubble height
LABEL_H      = 22                     # agent name label height
CLOSE_BTN_S  = 18                     # close button size
WIN_H        = SPRITE_H + BUBBLE_H + LABEL_H + 20

BG           = '#1E1E2E'              # dark background
FG           = '#CDD6F4'              # foreground text
FONT_LABEL   = ('Courier', 10, 'bold')
FONT_BUBBLE  = ('Courier', 9)
FONT_CLOSE   = ('Courier', 10, 'bold')

POLL_MS      = 800    # how often to poll state file (ms)
FRAME_MS     = 160    # base animation frame interval (ms)
BOB_PERIOD   = 1.4    # seconds for one full bob cycle


class AgentWindow:
    def __init__(self, root: tk.Tk, demo: bool = False):
        self.root = root
        self.demo = demo

        # --- current display state ---
        self._agent_name  = 'developer'
        self._state_name  = 'idle'
        self._message     = ''
        self._frame_idx   = 0
        self._start_time  = time.time()
        self._drag_x      = 0
        self._drag_y      = 0

        # --- demo cycling ---
        self._demo_agents = list(AGENTS.keys())
        self._demo_states = list(STATE_CONFIG.keys())
        self._demo_ai     = 0
        self._demo_si     = 0
        self._demo_ts     = time.time()

        self._build_window()
        self._schedule_poll()
        self._schedule_frame()

    # -----------------------------------------------------------------------
    # Window construction
    # -----------------------------------------------------------------------
    def _build_window(self):
        r = self.root
        r.title('SoftwareTeam')
        r.geometry(f'{WIN_W}x{WIN_H}+80+80')
        r.resizable(False, False)
        r.configure(bg=BG)
        r.attributes('-topmost', True)
        r.overrideredirect(True)   # borderless

        # Semi-transparent on supported platforms
        try:
            r.attributes('-alpha', 0.93)
        except tk.TclError:
            pass

        # Outer frame with colored border (state indicator)
        self._border_frame = tk.Frame(r, bg='#888888', padx=2, pady=2)
        self._border_frame.pack(fill='both', expand=True)

        inner = tk.Frame(self._border_frame, bg=BG)
        inner.pack(fill='both', expand=True)

        # Title bar (drag handle + close button)
        title_bar = tk.Frame(inner, bg='#2A2A3E', height=22)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)

        self._title_lbl = tk.Label(title_bar, text='● SoftwareTeam',
                                   bg='#2A2A3E', fg='#888888',
                                   font=('Courier', 8), anchor='w')
        self._title_lbl.pack(side='left', padx=6)

        close_btn = tk.Label(title_bar, text='✕', bg='#2A2A3E', fg='#FF6666',
                              font=FONT_CLOSE, cursor='hand2', padx=4)
        close_btn.pack(side='right', padx=2)
        close_btn.bind('<Button-1>', lambda e: self.root.destroy())

        # Drag bindings on title bar and sprite area
        for widget in (title_bar, self._title_lbl):
            widget.bind('<ButtonPress-1>',   self._on_drag_start)
            widget.bind('<B1-Motion>',        self._on_drag_motion)

        # Sprite canvas
        self._canvas = tk.Canvas(inner, width=WIN_W - 8, height=SPRITE_H + 8,
                                  bg=BG, highlightthickness=0)
        self._canvas.pack(pady=(4, 0))
        self._canvas.bind('<ButtonPress-1>',  self._on_drag_start)
        self._canvas.bind('<B1-Motion>',       self._on_drag_motion)

        # Agent name label
        self._name_lbl = tk.Label(inner, text='Developer',
                                   bg=BG, fg='#44AA44',
                                   font=FONT_LABEL, anchor='center')
        self._name_lbl.pack(fill='x', padx=4)

        # Speech bubble
        self._bubble_frame = tk.Frame(inner, bg='#FFFFFF', padx=4, pady=3)
        self._bubble_frame.pack(fill='x', padx=6, pady=(2, 6))

        self._bubble_icon = tk.Label(self._bubble_frame, text='💤',
                                      bg='#FFFFFF', font=('Courier', 13))
        self._bubble_icon.pack(side='left')

        self._bubble_lbl  = tk.Label(self._bubble_frame,
                                      text='Idle',
                                      bg='#FFFFFF', fg='#333333',
                                      font=FONT_BUBBLE, anchor='w',
                                      wraplength=WIN_W - 60,
                                      justify='left')
        self._bubble_lbl.pack(side='left', fill='x', expand=True)

        # Keyboard shortcut
        r.bind('<Escape>', lambda e: r.destroy())

    # -----------------------------------------------------------------------
    # Drag support
    # -----------------------------------------------------------------------
    def _on_drag_start(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _on_drag_motion(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f'+{x}+{y}')

    # -----------------------------------------------------------------------
    # State polling
    # -----------------------------------------------------------------------
    def _schedule_poll(self):
        self._poll()
        self.root.after(POLL_MS, self._schedule_poll)

    def _poll(self):
        if self.demo:
            self._advance_demo()
            return

        s = read_state()
        if s['agent'] != self._agent_name or s['state'] != self._state_name:
            self._frame_idx = 0  # reset animation on change
        self._agent_name = s['agent']
        self._state_name = s['state']
        self._message    = s['message']

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
    # Animation render loop
    # -----------------------------------------------------------------------
    def _schedule_frame(self):
        self._render_frame()
        sc = get_state_config(self._state_name)
        interval = max(80, int(1000 / sc['fps']))
        self.root.after(interval, self._schedule_frame)

    def _render_frame(self):
        agent_cfg  = get_agent(self._agent_name)
        state_cfg  = get_state_config(self._state_name)

        frames_key = state_cfg['frames_key']
        frames     = agent_cfg[frames_key]
        frame      = frames[self._frame_idx % len(frames)]
        self._frame_idx += 1

        # Bob offset (sinusoidal y shift)
        bob_y = 0
        if state_cfg['bob']:
            elapsed = time.time() - self._start_time
            bob_y   = int(math.sin(elapsed * 2 * math.pi / BOB_PERIOD) * 2)

        # Draw sprite
        c = self._canvas
        c.delete('all')

        ox = (WIN_W - 8 - SPRITE_W) // 2  # center horizontally
        oy = 4 + bob_y

        for row_i, row in enumerate(frame):
            for col_i, ch in enumerate(row):
                color = PALETTE.get(ch)
                if color is None:
                    continue
                x1 = ox + col_i * CELL
                y1 = oy + row_i * CELL
                x2 = x1 + CELL - 1
                y2 = y1 + CELL - 1
                c.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

        # State icon overlay (top-right of sprite)
        icon = state_cfg['icon']
        c.create_text(ox + SPRITE_W - 4, oy + 4, text=icon,
                      anchor='ne', font=('Courier', 14))

        # Update border color
        border_color = state_cfg['border_color']
        self._border_frame.configure(bg=border_color)

        # Update speech bubble
        bubble_bg  = state_cfg['bubble_color']
        message    = self._message or _default_message(self._state_name)
        self._bubble_frame.configure(bg=bubble_bg)
        self._bubble_icon.configure(bg=bubble_bg, text=icon)
        self._bubble_lbl.configure(bg=bubble_bg, text=message)

        # Update name label
        label = agent_cfg['label']
        color = agent_cfg['color']
        self._name_lbl.configure(text=label, fg=color)

        # Flicker effect for celebrating state
        if self._state_name == 'celebrating':
            import random
            colors = ['#FF6666', '#66FF66', '#6666FF', '#FFFF66', '#FF66FF']
            self._border_frame.configure(bg=random.choice(colors))


def _default_message(state: str) -> str:
    defaults = {
        'idle':              'Idle…',
        'thinking':          'Thinking…',
        'reviewing':         'Reviewing code…',
        'typing':            'Writing…',
        'reworking':         'Addressing feedback…',
        'approved':          'All good! ✅',
        'changes_requested': 'Changes needed 🔴',
        'handingoff':        'Handing off…',
        'celebrating':       'Merged! 🎉',
        'waiting':           'Waiting for you…',
    }
    return defaults.get(state, '')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Agent animation floating window')
    parser.add_argument('--demo', action='store_true',
                        help='Cycle through all agents and states automatically')
    args = parser.parse_args()

    root = tk.Tk()
    AgentWindow(root, demo=args.demo)
    root.mainloop()


if __name__ == '__main__':
    main()
