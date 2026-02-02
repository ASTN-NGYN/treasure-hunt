import numpy as np
from config import MIN_GRID_SIZE
import config
from search import dfs

class Grid:
    def __init__(self, grid_size):
        self.grid_size = grid_size

        if self.grid_size < MIN_GRID_SIZE:
            raise ValueError(f"Grid size must be at least {MIN_GRID_SIZE}")

        config.GRID_SIZE = self.grid_size
        
        self.num_walls = self.calculate_num_walls()
        self.generate_grid()
        
    def calculate_num_walls(self):
        return int(self.grid_size**2 * 0.10)
    
    def generate_grid(self):
        for _ in range(100):
            self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

            treasure_x, treasure_y = self.get_random_empty_cell()
            self.grid[treasure_x, treasure_y] = 1

            trap_x, trap_y = self.get_random_empty_cell()
            self.grid[trap_x, trap_y] = 2

            for _ in range(self.num_walls):
                wall_x, wall_y = self.get_random_empty_cell()
                self.grid[wall_x, wall_y] = 3

            start = self._find_start()
            goal = (treasure_x, treasure_y)

            if self._solution_exists(start, goal):
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
    
    def _find_start(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row, col] == 0:
                    return row, col
        return (0, 0)

    def _solution_exists(self, start, goal):
        result = dfs(self.grid, start, goal)
        return len(result.path) > 0
