"""
Pixel sprite definitions for each agent role.

Each sprite is a list of strings (rows, top to bottom).
Each character maps to a color via PALETTE.
Grid: 12 cols × 18 rows. Each cell is rendered at CELL px × CELL px.
"""

CELL = 9  # screen pixels per sprite cell

PALETTE = {
    ' ': None,        # transparent
    'S': '#FFCC99',   # skin
    'E': '#1A1A1A',   # dark (eyes)
    'W': '#FFFFFF',   # white
    'K': '#444444',   # dark gray
    'N': '#FFAA77',   # neck shadow
    'L': '#222255',   # dark legs
    'b': '#111111',   # black feet
    'r': '#CC5544',   # mouth
    'H': '#553311',   # dark brown hair
    'D': '#AA7733',   # light brown hair
    'h': '#221100',   # very dark hair
    'G': '#3A9944',   # green    (Developer)
    'g': '#5DBB6A',   # green light
    'O': '#CC7700',   # orange   (Architect)
    'o': '#EE9922',   # orange light
    'T': '#5588CC',   # blue     (Tester)
    't': '#88AADD',   # blue light
    'B': '#224499',   # navy     (Product Owner)
    'c': '#4466BB',   # navy light
    'P': '#772299',   # purple   (IT Agent)
    'p': '#9944BB',   # purple light
    'Y': '#AA8800',   # gold     (Cost Analyst)
    'y': '#CCAA22',   # gold light
}

# ---------------------------------------------------------------------------
# Base sprite template: 12 wide × 18 tall
# X = body color placeholder (replaced per agent)
# x = body color light placeholder
# ---------------------------------------------------------------------------
_BASE = [
    "    HHHHHH    ",  # 0  hair top
    "   HhHHHHhH   ",  # 1  hair
    "   HSSSSSSSH  ",  # 2  face top
    "   HSEESEESH  ",  # 3  eyes
    "   HSSSSSSSH  ",  # 4  nose
    "   HSSSrSSSH  ",  # 5  mouth
    "    SSSSSS    ",  # 6  chin
    "     NNNN     ",  # 7  neck
    "   xxxxxxxx   ",  # 8  shoulders
    "  xxxxxxxxxx  ",  # 9  chest
    "  xxxxxxxxxx  ",  # 10 body
    "  xxxxxxxxxx  ",  # 11 lower body
    "   XXXXXX     ",  # 12 hips
    "   LL  LL     ",  # 13 legs
    "   LL  LL     ",  # 14 legs
    "   bb  bb     ",  # 15 feet
]

# Typing frame 2: hands raised slightly (rows 9-10 shift arm chars)
_BASE_TYPING = [
    "    HHHHHH    ",
    "   HhHHHHhH   ",
    "   HSSSSSSSH  ",
    "   HSEESEESH  ",
    "   HSSSSSSSH  ",
    "   HSSSrSSSH  ",
    "    SSSSSS    ",
    "     NNNN     ",
    "  xxxxxxxxxxxx",  # arms out
    "  xxxxxxxxxx  ",
    " xxxxxxxxxxxx ",  # hands up
    "  xxxxxxxxxx  ",
    "   XXXXXX     ",
    "   LL  LL     ",
    "   LL  LL     ",
    "   bb  bb     ",
]

def _make(body: str, body_light: str, hair: str = 'H') -> list[list[str]]:
    """Substitute body+hair color characters into base sprite, return 2D char list."""
    result = []
    for row in _BASE:
        new_row = []
        for ch in row:
            if ch == 'X':
                new_row.append(body)
            elif ch == 'x':
                new_row.append(body_light)
            elif ch == 'H' and hair != 'H':
                new_row.append(hair)
            else:
                new_row.append(ch)
        result.append(new_row)
    return result

def _make_typing(body: str, body_light: str, hair: str = 'H') -> list[list[str]]:
    result = []
    for row in _BASE_TYPING:
        new_row = []
        for ch in row:
            if ch == 'X':
                new_row.append(body)
            elif ch == 'x':
                new_row.append(body_light)
            elif ch == 'H' and hair != 'H':
                new_row.append(hair)
            else:
                new_row.append(ch)
        result.append(new_row)
    return result

# ---------------------------------------------------------------------------
# Agent sprite sets: each agent has frames for idle / typing
# ---------------------------------------------------------------------------

AGENTS = {
    'developer': {
        'color':  '#3A9944',
        'label':  'Developer',
        'idle':   [_make('G', 'g', 'h'), _make('G', 'g', 'h')],  # 2 identical; bob handled by y-offset
        'typing': [_make('G', 'g', 'h'), _make_typing('G', 'g', 'h')],
    },
    'architect': {
        'color':  '#CC7700',
        'label':  'Architect',
        'idle':   [_make('O', 'o', 'D'), _make('O', 'o', 'D')],
        'typing': [_make('O', 'o', 'D'), _make_typing('O', 'o', 'D')],
    },
    'tester': {
        'color':  '#5588CC',
        'label':  'Tester',
        'idle':   [_make('T', 't', 'H'), _make('T', 't', 'H')],
        'typing': [_make('T', 't', 'H'), _make_typing('T', 't', 'H')],
    },
    'product-owner': {
        'color':  '#224499',
        'label':  'Product Owner',
        'idle':   [_make('B', 'c', 'h'), _make('B', 'c', 'h')],
        'typing': [_make('B', 'c', 'h'), _make_typing('B', 'c', 'h')],
    },
    'it': {
        'color':  '#772299',
        'label':  'IT Agent',
        'idle':   [_make('P', 'p', 'E'), _make('P', 'p', 'E')],
        'typing': [_make('P', 'p', 'E'), _make_typing('P', 'p', 'E')],
    },
    'cost-analyst': {
        'color':  '#AA8800',
        'label':  'Cost Analyst',
        'idle':   [_make('Y', 'y', 'D'), _make('Y', 'y', 'D')],
        'typing': [_make('Y', 'y', 'D'), _make_typing('Y', 'y', 'D')],
    },
}

# ---------------------------------------------------------------------------
# State → animation config
# ---------------------------------------------------------------------------
STATE_CONFIG = {
    'idle': {
        'frames_key': 'idle',
        'fps': 2,
        'bob': True,
        'bubble_color': '#FFFFFF',
        'border_color': '#888888',
        'icon': '💤',
    },
    'thinking': {
        'frames_key': 'idle',
        'fps': 2,
        'bob': True,
        'bubble_color': '#FFFFCC',
        'border_color': '#AAAAAA',
        'icon': '🤔',
    },
    'reviewing': {
        'frames_key': 'idle',
        'fps': 3,
        'bob': True,
        'bubble_color': '#DDEEFF',
        'border_color': '#4488CC',
        'icon': '🔍',
    },
    'typing': {
        'frames_key': 'typing',
        'fps': 4,
        'bob': False,
        'bubble_color': '#EEFFEE',
        'border_color': '#44AA44',
        'icon': '⌨️',
    },
    'reworking': {
        'frames_key': 'typing',
        'fps': 6,
        'bob': False,
        'bubble_color': '#FFF0CC',
        'border_color': '#EE9922',
        'icon': '🔧',
    },
    'approved': {
        'frames_key': 'idle',
        'fps': 2,
        'bob': True,
        'bubble_color': '#CCFFCC',
        'border_color': '#33AA33',
        'icon': '✅',
    },
    'changes_requested': {
        'frames_key': 'idle',
        'fps': 2,
        'bob': True,
        'bubble_color': '#FFDDDD',
        'border_color': '#CC3333',
        'icon': '🔴',
    },
    'handingoff': {
        'frames_key': 'typing',
        'fps': 4,
        'bob': False,
        'bubble_color': '#EEE0FF',
        'border_color': '#8833CC',
        'icon': '🤝',
    },
    'celebrating': {
        'frames_key': 'idle',
        'fps': 3,
        'bob': True,
        'bubble_color': '#FFFACC',
        'border_color': '#FFCC00',
        'icon': '🎉',
    },
    'waiting': {
        'frames_key': 'idle',
        'fps': 1,
        'bob': True,
        'bubble_color': '#F5F5F5',
        'border_color': '#AAAAAA',
        'icon': '⏳',
    },
}

def get_agent(name: str) -> dict:
    """Return agent config, defaulting to developer if unknown."""
    return AGENTS.get(name, AGENTS['developer'])

def get_state_config(state: str) -> dict:
    """Return state animation config, defaulting to idle."""
    return STATE_CONFIG.get(state, STATE_CONFIG['idle'])
