GRID_SIZE = 15       # default grid size for adversarial search
MIN_GRID_SIZE = 15
CELL_SIZE = 35

COLORS = {
    'empty': '#eceff1',  # empty cell - gray
    'treasure': '#8dd7fc', # treasure  - pink
    'trap': '#f7b9fa',   # trap - blue
    'wall': '#fcba03',   # wall - orange
    'start': '#88e788',  # start - green
    'agent_a': '#4a6cff',  # agent_a - green
    'agent_b': '#ff4a4a',  # agent_b - green
}

SYMBOLS = {
    0: '',      # empty cell
    1: 'T',     # treasure
    2: 'X',     # trap
    3: '#',     # wall
    4: 'A',     # agent A
    5: 'B',     # agent B
}