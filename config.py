GRID_SIZE = 15       # default grid size for adversarial search
MIN_GRID_SIZE = 15
CELL_SIZE = 35

# Optional manual layout configuration.
# Coordinates are (row, col) with 0-based indexing.
# Set these to None / [] to use random generation instead.
AGENT_A_COORD = (2,12)
AGENT_B_COORD = (12,2)

TREASURE_COORDS = [(6,5), (7,10), (10,8)]
TRAP_COORDS = [(5,5), (6,4), (7,5), (7,9), (6,10), (8,10), (9,8), (10,7), (11,8)] 
WALL_COORDS = [(4,7), (4,8), (4,9), (8,4), (9,4), (10,4), (12,10), (12,11), (3,11)] 

COLORS = {
    'empty': '#eceff1',    # empty cell - gray
    'treasure': '#8dd7fc', # treasure  - pink
    'trap': '#f7b9fa',     # trap - blue
    'wall': '#fcba03',     # wall - orange
    'start': '#88e788',    # start - green
    'agent_a': '#4a6cff',  # agent_a - green
    'agent_b': '#ff4a4a',  # agent_b - green
}

SYMBOLS = {
    0: '',   # empty cell
    1: 'T',  # treasure
    2: 'X',  # trap
    3: '#',  # wall
    4: 'A',  # agent A
    5: 'B',  # agent B
}