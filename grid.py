import numpy as np
from config import MIN_GRID_SIZE
import config
from search import dfs
from typing import Tuple

Coord = Tuple[int, int]

class Grid:
    def __init__(self, grid_size):
        self.grid_size = grid_size

        if self.grid_size < MIN_GRID_SIZE:
            raise ValueError(f"Grid size must be at least {MIN_GRID_SIZE}")

        config.GRID_SIZE = self.grid_size

        # self.agent_coords = (10,10)
        # self.treasure_coords = [(3, 17), (17, 3)]
        # self.traps_coords = [(3, 16),(4, 17), (16, 3), (17, 4)]
        # self.walls_coords = [(1,8), (2,8), (3,9), (4,9), (5,15), 
        #                     (6,12), (7,7), (8,13), (10,6), (11,10), 
        #                     (13,3), (14,14), (15,6), (17,18), 
        #                     (18,9), (5,4), (9,4), (12,16)]


        # ======================================================
        # PROMPT 1: Medium Noise Treasure Hunt
        # ======================================================
        # self.agent_coords = (2, 2)

        # self.treasure_coords = [
        #     (6, 8)
        # ]

        # self.traps_coords = [
        #     (5, 7),
        #     (14, 13)
        # ]

        # self.walls_coords = [
        #     (4,5),(4,6),(4,7),
        #     (9,10),(10,10),(11,10),
        #     (12,4),(13,4),(14,4),
        #     (16,11)
        # ]


        # ======================================================
        # PROMPT 2: High Noise Treasure Hunt
        # ======================================================

        self.agent_coords = (18, 3)
        
        self.treasure_coords = [
            (5,16),
            (11,11),
            (17,14)
        ]
        
        self.traps_coords = [
            (6,15),
            (10,12),
            (16,13)
        ]
        
        self.walls_coords = [
            (3,8),(4,8),(5,8),
            (8,4),(8,5),(8,6),
            (10,15),(11,15),(12,15),
            (13,9),(14,9),(15,9)
        ]
        
        self.random_walls = self.calculate_num_walls()   # for when you want to generate the walls randomly
        self.random_traps = self.calculate_num_traps()   # for when you want to generate the traps randomly
        
        self.generate_grid()
        
    def calculate_num_walls(self):
        return int(np.random.randint(5, 10))

    def calculate_num_traps(self):
        return int(2)
    
    def generate_grid(self):
        for _ in range(100):
            self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

            startx, starty = self.agent_coords
            self.grid[startx, starty] = 4

            for tx, ty in self.treasure_coords:
                self.grid[tx, ty] = 1

            for trap_x, trap_y in self.traps_coords:
                self.grid[trap_x, trap_y] = 2

            for wall_x, wall_y in self.walls_coords:
                self.grid[wall_x, wall_y] = 3

            start = (startx, starty)

            if self._solution_exists(start):
                return

        raise RuntimeError("Failed to generate a valid grid after 100 attempts")

    # Generate a random grid with random walls, traps, and treasures
    def generate_random_grid(self):
        for _ in range(100):
            self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
            treasure_coords = []
            traps_coords = []
            walls_coords = []

            startx, starty = self.agent_coords
            self.grid[startx, starty] = 4

            for _ in range(2):
                treasure_x, treasure_y = self.get_random_empty_cell()
                self.grid[treasure_x, treasure_y] = 1
                treasure_coords.append((treasure_x, treasure_y))

            for _ in range(self.random_traps):
                trap_x, trap_y = self.get_random_empty_cell()
                self.grid[trap_x, trap_y] = 2
                traps_coords.append((trap_x, trap_y))

            for _ in range(self.random_walls):
                wall_x, wall_y = self.get_random_empty_cell()
                self.grid[wall_x, wall_y] = 3
                walls_coords.append((wall_x, wall_y))

            self.treasure_coords = treasure_coords
            self.traps_coords = traps_coords
            self.walls_coords = walls_coords
            
            start = (startx, starty)

            if self._solution_exists(start):
                return

        raise RuntimeError("Failed to generate a valid grid after 100 attempts")

    
    def get_random_empty_cell(self):
        row = np.random.randint(0, self.grid_size)
        col = np.random.randint(0, self.grid_size)

        if self.grid[row, col] != 0:
            return self.get_random_empty_cell()
        
        return row, col
    
    def get_grid(self):
        return self.grid

    def is_wall(self, cell: Coord) -> bool:
        """Return True when the given cell contains a wall."""
        return cell in self.walls_coords

    def is_trap(self, cell: Coord) -> bool:
        """Return True when the given cell contains a trap."""
        return cell in self.traps_coords

    def is_treasure(self, cell: Coord) -> bool:
        """Return True when the given cell contains a treasure."""
        return cell in self.treasure_coords

    def is_blocked(self, cell: Coord) -> bool:
        """Return True when the given cell cannot contain treasure."""
        return self.is_wall(cell) or self.is_trap(cell)

    def valid_cells(self) -> list[Coord]:
        """Return all cells where treasure could exist."""
        return [
            (row, col)
            for row in range(self.grid_size)
            for col in range(self.grid_size)
            if not self.is_blocked((row, col))
        ]

    def remaining_treasures(self) -> list[Coord]:
        """Return the list of treasure coordinates that still exist."""
        return list(self.treasure_coords)

    def remove_treasure(self, cell: Coord) -> None:
        """Remove a collected treasure from both the coordinate list and grid."""
        if cell not in self.treasure_coords:
            return

        self.treasure_coords.remove(cell)
        self.grid[cell[0], cell[1]] = 4 if cell == self.agent_coords else 0

    def get_cells_in_radius(self, center: Coord, radius: int) -> list[Coord]:
        """Return in-bounds cells within the given Manhattan radius."""
        cells = []
        row_center, col_center = center

        for row in range(max(0, row_center - radius), min(self.grid_size, row_center + radius + 1)):
            for col in range(max(0, col_center - radius), min(self.grid_size, col_center + radius + 1)):
                if self._manhattan_distance(center, (row, col)) <= radius:
                    cells.append((row, col))

        return cells

    def reset_random(self, seed: int | None = None) -> None:
        """Clear and regenerate a random grid, optionally using a seed."""
        if seed is not None:
            np.random.seed(seed)

        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.random_walls = self.calculate_num_walls()
        self.random_traps = self.calculate_num_traps()
        self.treasure_coords = []
        self.traps_coords = []
        self.walls_coords = []
        self.generate_random_grid()

    def get_shortest_treasure(self, start: Coord) -> Coord | None:
        min_distance = float('inf')
        closest_treasure = None
        for treasure_coord in self.treasure_coords:
            distance = self._manhattan_distance(start, treasure_coord)
            if distance < min_distance:
                min_distance = distance
                closest_treasure = treasure_coord
        return closest_treasure
    
    def _manhattan_distance(self, current: Coord, goal: Coord) -> int:
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

    def _solution_exists(self, start):
        for goal in self.treasure_coords:
            result = dfs(self.grid, start, goal)
            if len(result.path) > 0:
                return True
        return False
