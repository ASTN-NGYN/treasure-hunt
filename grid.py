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

        self.agent_coords = (10,10)
        self.treasure_coords = [(3, 17), (17, 3)]
        self.traps_coords = [(3, 16),(4, 17), (16, 3), (17, 4)]
        self.walls_coords = [(1,8), (2,8), (3,9), (4,9), (5,15), 
                            (6,12), (7,7), (8,13), (10,6), (11,10), 
                            (13,3), (14,14), (15,6), (17,18), 
                            (18,9), (5,4), (9,4), (12,16)]
        
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
