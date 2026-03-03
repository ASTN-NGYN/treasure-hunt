GRID_SIZE = 15
CELL_SIZE = 40

COLORS = {
    'empty': '#eceff1',  # empty cell - gray
    'treasure': '#8dd7fc', # treasure  - pink
    'trap': '#f7b9fa',   # trap - blue
    'wall': '#fcba03',   # wall - orange
    'A': '#88e788',  # start - green
    'B': '#ff8a80'   # target - red
}

ACTIONS = [
    (-1, 0),  # up
    (1, 0),   # down
    (0, -1),  # left
    (0, 1)    # right
]