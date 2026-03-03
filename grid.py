import numpy as np
from config import MIN_GRID_SIZE
import config
from search import dfs
from typing import Tuple

Coord = Tuple[int, int]

class Grid:
    def __init__(self, grid_size=15):
        self.grid_size = grid_size
        self.agent_a_pos = (0, 0)
        self.agent_b_pos = (14, 14)
        self.treasures = [] 
        self.traps = []
        self.walls = []
        self.generate_random_setup()

    def generate_random_setup(self):
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        # 1. Place 3-5 Treasures (Value 1)
        for _ in range(np.random.randint(3, 6)):
            pos = self.get_random_empty_cell()
            self.treasures.append(pos)
            self.grid[pos] = 1
            
        # 2. Place 2-3 Traps (Value 2)
        for _ in range(np.random.randint(2, 4)):
            pos = self.get_random_empty_cell()
            self.grid[pos] = 2

        # 3. Place Walls (Value 3)
        for _ in range(20):
            pos = self.get_random_empty_cell()
            self.grid[pos] = 3
            
        # 4. Set Agents (Value 4 for A, 5 for B)
        self.grid[self.agent_a_pos] = 4
        self.grid[self.agent_b_pos] = 5
        
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

            startx, starty = self.agent_coords
            self.grid[startx, starty] = 4

            for _ in range(2):
                treasure_x, treasure_y = self.get_random_empty_cell()
                self.grid[treasure_x, treasure_y] = 1

            for _ in range(self.random_traps):
                trap_x, trap_y = self.get_random_empty_cell()
                self.grid[trap_x, trap_y] = 2

            for _ in range(self.random_walls):
                wall_x, wall_y = self.get_random_empty_cell()
                self.grid[wall_x, wall_y] = 3
            
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
