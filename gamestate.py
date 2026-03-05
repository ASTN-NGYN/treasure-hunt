from copy import deepcopy
from typing import List, Tuple, Optional

Coord = Tuple[int, int]

class GameState:
    def __init__(
        self,
        grid,
        agent_a,
        agent_b,
        treasures,
        current_player="A",
        prev_agent_a: Optional[Coord] = None,
        prev_agent_b: Optional[Coord] = None,
        prev2_agent_a: Optional[Coord] = None,
        prev2_agent_b: Optional[Coord] = None,
    ):
        self.grid = grid
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.treasures = treasures
        self.current_player = current_player
        # Walls are impassable; traps are legal but undesirable.
        self.blocked = {3}
        self.prev_agent_a = prev_agent_a
        self.prev_agent_b = prev_agent_b
        self.prev2_agent_a = prev2_agent_a
        self.prev2_agent_b = prev2_agent_b

    def is_terminal(self):
        return len(self.treasures) == 0
    
    def get_legal_moves(self):
        moves = []
        row, col = self.agent_a if self.current_player == "A" else self.agent_b
        other = self.agent_b if self.current_player == "A" else self.agent_a

        for d_row, d_col in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nr, nc = row + d_row, col + d_col
            if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid):
                if self.grid[nr][nc] not in self.blocked and (nr, nc) != other:
                    moves.append((nr, nc))
        return moves

    def apply_move(self, move):
        new_state = deepcopy(self)

        if self.current_player == "A":
            new_state.prev2_agent_a = self.prev_agent_a
            new_state.prev_agent_a = self.agent_a
            new_state.agent_a = move
        else:
            new_state.prev2_agent_b = self.prev_agent_b
            new_state.prev_agent_b = self.agent_b
            new_state.agent_b = move

        if move in new_state.treasures:
            new_state.treasures.remove(move)

        new_state.current_player = "B" if self.current_player == "A" else "A"
        return new_state
    
