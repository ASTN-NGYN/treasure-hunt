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
        self.num_traps = self.calculate_num_traps()
        self.generate_grid()
        
    def calculate_num_walls(self):
        return int(np.random.randint(5, 10))

    def calculate_num_traps(self):
        return int(2)
    
    def generate_grid(self):
        for _ in range(100):
            self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

            startx, starty = 19, 0
            self.grid[startx, starty] = 4

            self.num_treasures = np.random.randint(2, 4)
            self.treasure_positions = []
            for _ in range(self.num_treasures):
                tx, ty = self.get_random_empty_cell()
                self.grid[tx, ty] = 1
                self.treasure_positions.append((tx, ty))

            for _ in range(self.num_traps):
                trap_x, trap_y = self.get_random_empty_cell()
                self.grid[trap_x, trap_y] = 2

            for _ in range(self.num_walls):
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
    
    # def _find_start(self):
    #     for row in range(self.grid_size):
    #         for col in range(self.grid_size):
    #             if self.grid[row, col] == 4:
    #                 return row, col
    #     return (10, 0)

    def _solution_exists(self, start):
        for goal in self.treasure_positions:
            result = dfs(self.grid, start, goal)
            if len(result.path) > 0:
                return True
        return False
