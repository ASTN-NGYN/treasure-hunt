import numpy as np
import random
from typing import Tuple, List

Coord = Tuple[int, int]


class Grid:
    """
    Grid class used ONLY for Minimax / Alpha-Beta adversarial search.
    
    Tile Encoding:
    0 = Empty
    1 = Treasure
    2 = Trap
    3 = Wall
    4 = Agent A
    5 = Agent B
    """

    def __init__(self, grid_size: int):
        self.grid_size = grid_size

        # Layout (agents, treasures, traps, walls) is generated randomly
        self.agent_a_coords: Coord
        self.agent_b_coords: Coord
        self.treasure_coords: List[Coord]
        self.traps_coords: List[Coord]
        self.walls_coords: List[Coord]

        self._generate_random_layout()
        self._create_grid()

    # -------------------------------------------------
    # Grid Creation
    # -------------------------------------------------

    def _random_empty_cell(self, occupied):
        """Return a random coordinate not already in occupied."""
        while True:
            r = random.randrange(self.grid_size)
            c = random.randrange(self.grid_size)
            if (r, c) not in occupied:
                return (r, c)

    def _generate_random_layout(self):
        """
        Randomly generate positions for agents, treasures, traps, and walls.
        Follows the assignment spec of:
        - 3–5 treasures
        - 2–3 traps
        - Several walls
        """
        occupied = set()

        # Agents
        self.agent_a_coords = self._random_empty_cell(occupied)
        occupied.add(self.agent_a_coords)

        self.agent_b_coords = self._random_empty_cell(occupied)
        occupied.add(self.agent_b_coords)

        # Treasures: 3–5
        num_treasures = random.randint(3, 5)
        self.treasure_coords = []
        for _ in range(num_treasures):
            cell = self._random_empty_cell(occupied)
            occupied.add(cell)
            self.treasure_coords.append(cell)

        # Traps: 2–3
        num_traps = random.randint(2, 3)
        self.traps_coords = []
        for _ in range(num_traps):
            cell = self._random_empty_cell(occupied)
            occupied.add(cell)
            self.traps_coords.append(cell)

        # Walls: "several" – choose 10–20
        num_walls = random.randint(5, 10)
        self.walls_coords = []
        for _ in range(num_walls):
            cell = self._random_empty_cell(occupied)
            occupied.add(cell)
            self.walls_coords.append(cell)

    def _create_grid(self):
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

        # Place treasures
        for r, c in self.treasure_coords:
            self.grid[r, c] = 1

        # Place traps
        for r, c in self.traps_coords:
            self.grid[r, c] = 2

        # Place walls
        for r, c in self.walls_coords:
            self.grid[r, c] = 3

        # Place agents
        ar, ac = self.agent_a_coords
        br, bc = self.agent_b_coords

        self.grid[ar, ac] = 4
        self.grid[br, bc] = 5

    # -------------------------------------------------
    # Public API for GUI / GameState
    # -------------------------------------------------

    def get_grid(self):
        return self.grid

    def update_agent_position(self, agent: str, new_pos: Coord):
        """
        Updates agent position on board.
        agent = "A" or "B"
        """

        if agent == "A":
            old_r, old_c = self.agent_a_coords
            self.grid[old_r, old_c] = 0

            self.agent_a_coords = new_pos
            self.grid[new_pos[0], new_pos[1]] = 4

        elif agent == "B":
            old_r, old_c = self.agent_b_coords
            self.grid[old_r, old_c] = 0

            self.agent_b_coords = new_pos
            self.grid[new_pos[0], new_pos[1]] = 5

    def remove_treasure(self, coord: Coord):
        if coord in self.treasure_coords:
            self.treasure_coords.remove(coord)
            self.grid[coord[0], coord[1]] = 0

    # -------------------------------------------------
    # Utility
    # -------------------------------------------------

    def is_valid_cell(self, row: int, col: int) -> bool:
        if row < 0 or row >= self.grid_size:
            return False
        if col < 0 or col >= self.grid_size:
            return False
        if self.grid[row, col] == 3:  # wall
            return False
        return True