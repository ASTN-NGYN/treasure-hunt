import numpy as np
from config import MIN_GRID_SIZE
import config

class Grid:
    def __init__(self, grid_size):
        self.grid_size = grid_size

        if self.grid_size < MIN_GRID_SIZE:
            raise ValueError(f"Grid size must be at least {MIN_GRID_SIZE}")

        config.GRID_SIZE = self.grid_size
        
        self.num_walls = self.calculate_num_walls()
        self.generate_grid()
        
    def calculate_num_walls(self):
        return int(self.grid_size**2 * 0.2)
    
    def generate_grid(self):
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

        treasure_x, treasure_y = self.get_random_empty_cell()
        self.grid[treasure_x, treasure_y] = 1

        trap_x, trap_y = self.get_random_empty_cell()
        self.grid[trap_x, trap_y] = 2

        for _ in range(self.num_walls):
            wall_x, wall_y = self.get_random_empty_cell()
            self.grid[wall_x, wall_y] = 3
    
    def get_random_empty_cell(self):
        row = np.random.randint(0, self.grid_size)
        col = np.random.randint(0, self.grid_size)

        if self.grid[row, col] != 0:
            return self.get_random_empty_cell()
        
        return row, col
    
    def get_grid(self):
        return self.grid
