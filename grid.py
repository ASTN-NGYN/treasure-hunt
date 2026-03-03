import random
from config import GRID_SIZE


class Grid:
    def __init__(self):
        self.size = GRID_SIZE
        self.reset()

    def random_cell(self):
        return (
            random.randint(0, self.size - 1),
            random.randint(0, self.size - 1)
        )

    def reset(self):
        self.a_pos = (0, 0)
        self.b_pos = (self.size - 1, self.size - 1)
        self.a_score = 0
        self.b_score = 0
        self.turn = "A"

        reserved = {self.a_pos, self.b_pos}

        # Walls (avoid agent start positions)
        self.walls = set()
        attempts = 0
        while len(self.walls) < 10 and attempts < 1000:
            pos = self.random_cell()
            if pos not in reserved:
                self.walls.add(pos)
            attempts += 1
        reserved.update(self.walls)

        # Traps (2–3, avoid reserved)
        self.traps = set()
        count = random.randint(2, 3)
        attempts = 0
        while len(self.traps) < count and attempts < 1000:
            pos = self.random_cell()
            if pos not in reserved:
                self.traps.add(pos)
            attempts += 1
        reserved.update(self.traps)

        # Treasures (3–5, avoid reserved)
        self.treasures = set()
        count = random.randint(3, 5)
        attempts = 0
        while len(self.treasures) < count and attempts < 1000:
            pos = self.random_cell()
            if pos not in reserved:
                self.treasures.add(pos)
            attempts += 1

    def get_state(self):
        return {
            "a_pos":     self.a_pos,
            "b_pos":     self.b_pos,
            "treasures": set(self.treasures),
            "traps":     set(self.traps),
            "walls":     set(self.walls),
            "turn":      self.turn,
            "a_score":   self.a_score,
            "b_score":   self.b_score,
        }

    def update_state(self, state):
        self.a_pos     = state["a_pos"]
        self.b_pos     = state["b_pos"]
        self.treasures = state["treasures"]
        self.turn      = state["turn"]
        self.a_score   = state.get("a_score", self.a_score)
        self.b_score   = state.get("b_score", self.b_score)
