GRID_SIZE = 8       # default grid size
DEFAULT_GRID_SIZE = 20
MIN_GRID_SIZE = 8
CELL_SIZE = 35
ENTROPY_EPS = 1e-12
DEFAULT_SCAN_RADIUS = 2
DEFAULT_FALSE_POSITIVE = 0.1
DEFAULT_FALSE_NEGATIVE = 0.2

NOISE_PRESETS = {
    "low": (0.05, 0.05),
    "medium": (0.1, 0.2),
    "high": (0.2, 0.3),
}

COLORS = {
    'empty': '#eceff1',  # empty cell - gray
    'treasure': '#8dd7fc', # treasure  - pink
    'trap': '#f7b9fa',   # trap - blue
    'wall': '#fcba03',   # wall - orange
    'start': '#88e788',  # start - green
}

SYMBOLS = {
    0: '',      # empty cell
    1: 'T',     # treasure
    2: 'X',     # trap
    3: '#',     # wall
    4: 'S',     # start
}