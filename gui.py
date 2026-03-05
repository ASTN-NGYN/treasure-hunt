import tkinter as tk
import random
import time

from config import CELL_SIZE, COLORS, SYMBOLS, GRID_SIZE
from grid import Grid
from gamestate import GameState
from adversarial import minimax, alphabeta, Metrics


class TreasureHuntMap:
    def __init__(self, grid: Grid, *, root: tk.Tk | None = None, on_reset=None):
        self.grid = grid
        self.grid_array = grid.get_grid()
        self.grid_size = len(self.grid_array)

        self.window = root or tk.Tk()
        self.window.title("Treasure Hunt - Adversarial AI")
        self.window.maxsize(1500, 800)

        self._on_reset = on_reset

        # UI Layout
        self.frame = tk.Frame(self.window)
        self.frame.pack(fill="both", expand=True)

        table_size = self.grid_size * CELL_SIZE
        self.canvas = tk.Canvas(
            self.frame,
            width=table_size,
            height=table_size,
            bg="white"
        )
        self.canvas.pack(padx=10, pady=(10, 6))

        self.a_score = 0
        self.b_score = 0

        self.draw_grid()

        controls = tk.Frame(self.frame)
        controls.pack(pady=(6, 4))

        # MINIMAX
        tk.Button(
            controls,
            text="Minimax Step",
            command=lambda: self.run_minimax(6)
        ).pack(side="left", padx=4)

        # ALPHA-BETA
        tk.Button(
            controls,
            text="AlphaBeta Step",
            command=lambda: self.run_alphabeta(6)
        ).pack(side="left", padx=4)

        # RESET
        if self._on_reset:
            tk.Button(
                controls,
                text="Reset",
                command=self._on_reset
            ).pack(side="left", padx=4)
        else:
            tk.Button(
                controls,
                text="Reset",
                command=self.window.destroy
            ).pack(side="left", padx=4)

        self._metrics_var = tk.StringVar(value="")
        self._metrics_label = tk.Label(
            self.frame,
            textvariable=self._metrics_var,
            anchor="w",
            justify="left"
        )
        self._metrics_label.pack(fill="x", padx=10, pady=(2, 10))

        # Track A's recent positions to reduce oscillation in depth-limited search
        self._prev_agent_a = None
        self._prev2_agent_a = None
        # Auto-play state.
        self._auto_playing = False
        self._auto_algo = None
        self._auto_depth = None

        tk.Button(controls, text="Auto Play Minimax", command=lambda: self._start_auto_play("minimax", 6)).pack(side="left", padx=4)
        tk.Button(controls, text="Auto Play AlphaBeta", command=lambda: self._start_auto_play("alphabeta", 6)).pack(side="left", padx=4)
        tk.Button(controls, text="Stop", command=self._stop_auto_play).pack(side="left", padx=4)

    def draw_grid(self):
        self.canvas.delete("all")

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell_value = self.grid_array[row][col]

                match cell_value:
                    case 0:
                        color = COLORS['empty']
                    case 1:
                        color = COLORS['treasure']
                    case 2:
                        color = COLORS['trap']
                    case 3:
                        color = COLORS['wall']
                    case 4:
                        color = COLORS['agent_a']      # Agent A
                    case 5:
                        color = COLORS['agent_b']      # Agent B
                    case _:
                        color = COLORS['empty']

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="#a6a6a6",
                    width=1
                )

                symbol = SYMBOLS.get(cell_value, '')
                if symbol:
                    self.canvas.create_text(
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=symbol,
                        font=('Arial', 12, 'bold'),
                        fill='black'
                    )

    def run_minimax(self, depth):
        metrics = Metrics()
        state = GameState(
            self.grid_array,
            self.grid.agent_a_coords,
            self.grid.agent_b_coords,
            self.grid.treasure_coords.copy(),
            current_player="A",
            prev_agent_a=getattr(self, "_prev_agent_a", None),
            prev2_agent_a=getattr(self, "_prev2_agent_a", None),
        )
        start_time = time.perf_counter()
        score, move = minimax(state, depth, metrics, True)
        end_time = time.perf_counter()

        if move:
            old_a = self.grid.agent_a_coords
            self._apply_agent_a_move(move)
            self._prev2_agent_a = self._prev_agent_a
            self._prev_agent_a = old_a
            self._random_opponent_move()
        else:
            self._prev_agent_a = self.grid.agent_a_coords

        self._metrics_var.set(
            f"Minimax (Depth {depth}) — "
            f"Nodes: {metrics.nodes_expanded}, "
            f"Time: {(end_time - start_time) * 1000:.2f} ms"
        )
        t1 = time.perf_counter()

    def run_alphabeta(self, depth):
        metrics = Metrics()
        state = GameState(
            self.grid_array,
            self.grid.agent_a_coords,
            self.grid.agent_b_coords,
            self.grid.treasure_coords.copy(),
            current_player="A",
            prev_agent_a=getattr(self, "_prev_agent_a", None),
            prev2_agent_a=getattr(self, "_prev2_agent_a", None),
        )
        start_time = time.perf_counter()
        score, move = alphabeta(
            state,
            depth,
            float("-inf"),
            float("inf"),
            metrics,
            True,
        )
        end_time = time.perf_counter()

        if move:
            old_a = self.grid.agent_a_coords
            self._apply_agent_a_move(move)
            self._prev2_agent_a = self._prev_agent_a
            self._prev_agent_a = old_a
            self._random_opponent_move()
        else:
            self._prev2_agent_a = self._prev_agent_a
            self._prev_agent_a = self.grid.agent_a_coords

        prune_ratio = (
            metrics.pruned / metrics.nodes_expanded
            if metrics.nodes_expanded else 0
        )
        self._metrics_var.set(
            f"AlphaBeta (Depth {depth}) — "
            f"Nodes: {metrics.nodes_expanded}, "
            f"Pruned: {metrics.pruned}, "
            f"Ratio: {prune_ratio:.2f}, "
            f"Time: {(end_time - start_time) * 1000:.2f} ms"
        )

    def _start_auto_play(self, algo: str, depth: int):
        self._auto_playing = True
        self._auto_algo = algo
        self._auto_depth = depth
        self._auto_play_next()

    def _stop_auto_play(self):
        self._auto_playing = False

    def _auto_play_next(self):
        if not self._auto_playing:
            return
        if not self.grid.treasure_coords:
            self._auto_playing = False
            self._announce_winner()
            return
        state = GameState(
            self.grid_array,
            self.grid.agent_a_coords,
            self.grid.agent_b_coords,
            self.grid.treasure_coords.copy(),
            current_player="A",
            prev_agent_a=getattr(self, "_prev_agent_a", None),
            prev2_agent_a=getattr(self, "_prev2_agent_a", None),
        )
        if not state.get_legal_moves():
            self._auto_playing = False
            self._announce_winner()
            return
        metrics = Metrics()
        start_time = time.perf_counter()
        if self._auto_algo == "minimax":
            score, move = minimax(state, self._auto_depth, metrics, True)
        else:
            score, move = alphabeta(state, self._auto_depth, float("-inf"), float("inf"), metrics, True)
        end_time = time.perf_counter()
        if move:
            old_a = self.grid.agent_a_coords
            self._apply_agent_a_move(move)
            self._prev2_agent_a = self._prev_agent_a
            self._prev_agent_a = old_a
            self._random_opponent_move()
        else:
            self._auto_playing = False
            return
        if not self.grid.treasure_coords:
            self._auto_playing = False
            self._announce_winner()
            return 
            
        prune_ratio = (metrics.pruned / metrics.nodes_expanded) if metrics.nodes_expanded else 0
        algo_name = (self._auto_algo or "minimax").capitalize()
        label = (
            f"{algo_name} D{self._auto_depth} — "
            f"Nodes: {metrics.nodes_expanded}, "
            f"Time: {(end_time - start_time) * 1000:.2f} ms"
        )
        if self._auto_algo == "alphabeta":
            label += f", Pruned: {metrics.pruned}, Ratio: {prune_ratio:.2f}"
        self._metrics_var.set(label)
        if self._auto_playing:
            self.window.after(400, self._auto_play_next)

    def _apply_agent_a_move(self, move):
        old_row, old_col = self.grid.agent_a_coords
        new_row, new_col = move

        self.grid_array[old_row][old_col] = 0

        if (new_row, new_col) in self.grid.treasure_coords:
            self.grid.treasure_coords.remove((new_row, new_col))
            self.a_score += 1

        self.grid.agent_a_coords = (new_row, new_col)
        self.grid_array[new_row][new_col] = 4

        self.draw_grid()

    def _random_opponent_move(self):
        """Greedy opponent for Agent B that moves toward the nearest treasure."""
        row, col = self.grid.agent_b_coords
        moves = []

        for d_row, d_col in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nr, nc = row + d_row, col + d_col
            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                if self.grid_array[nr][nc] != 3 and self.grid_array[nr][nc] != 4:
                    moves.append((nr, nc))

        if not moves:
            return

        # If there are treasures, choose the move that minimizes distance to the closest treasure.
        if self.grid.treasure_coords:
            def dist_to_nearest_treasure(pos):
                r, c = pos
                return min(abs(r - tr) + abs(c - tc) for tr, tc in self.grid.treasure_coords)

            best_dist = None
            best_moves = []
            for m in moves:
                d = dist_to_nearest_treasure(m)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best_moves = [m]
                elif d == best_dist:
                    best_moves.append(m)
            move = random.choice(best_moves)
        else:
            move = random.choice(moves)

        old_row, old_col = self.grid.agent_b_coords
        self.grid_array[old_row][old_col] = 0

        if move in self.grid.treasure_coords:
            self.grid.treasure_coords.remove(move)
            self.b_score += 1

        self.grid.agent_b_coords = move
        self.grid_array[move[0]][move[1]] = 5

        self.draw_grid()

    def destroy(self):
        self.is_running = False
        self.frame.destroy()

    def _announce_winner(self):
        if self.a_score > self.b_score:
            result = f"Game over. Winner: A (A={self.a_score}, B={self.b_score})"
        elif self.b_score > self.a_score:
            result = f"Game over. Winner: B (A={self.a_score}, B={self.b_score})"
        else:
            result = f"Game over. Tie (A={self.a_score}, B={self.b_score})"

        # Show in the metrics label:
        self._metrics_var.set((self._metrics_var.get() or "") + " — " + result)

        # And optionally print to the console:
        print(result)

class TreasureHuntApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Treasure Hunt - Adversarial AI")
        self._map_view: TreasureHuntMap | None = None
        self._create_new_map()

    def _create_new_map(self):
        grid = Grid(GRID_SIZE)
        self._map_view = TreasureHuntMap(
            grid,
            root=self.root,
            on_reset=self.reset
        )

    def reset(self):
        if self._map_view is not None:
            self._map_view.destroy()
            self._map_view = None
        self._create_new_map()

    def run(self):
        self.root.mainloop()