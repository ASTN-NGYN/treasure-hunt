import tkinter as tk
from tkinter import ttk
from config import GRID_SIZE, CELL_SIZE, COLORS
from grid import Grid
from search import minimax, alphabeta, random_move, apply_move, get_valid_moves

ALGO_OPTIONS = ["Minimax", "Alpha-Beta", "Random"]
AUTO_PLAY_DELAY_MS = 400   # milliseconds between auto-play steps


class TreasureHuntApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Treasure Hunt - Adversarial AI")
        self.root.resizable(False, False)

        self.grid = Grid()
        self._auto_playing = False
        self._after_id = None

        self._build_ui()
        self._bind_keys()
        self.draw()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=GRID_SIZE * CELL_SIZE,
            height=GRID_SIZE * CELL_SIZE,
            bg=COLORS["empty"]
        )
        self.canvas.pack()

        # ── Controls row 1: depth + algorithm selectors ──
        row1 = tk.Frame(self.root, pady=4)
        row1.pack()

        tk.Label(row1, text="Depth:").pack(side="left", padx=(0, 4))
        self.depth_var = tk.IntVar(value=2)
        depth_btn_frame = tk.Frame(row1, relief="sunken", bd=1)
        depth_btn_frame.pack(side="left", padx=(0, 12))
        self._depth_buttons = {}
        for d in (2, 4, 6):
            btn = tk.Button(
                depth_btn_frame, text=str(d), width=3,
                relief="flat", bd=0, padx=6, pady=2,
                command=lambda v=d: self._select_depth(v)
            )
            btn.pack(side="left")
            self._depth_buttons[d] = btn
        self._select_depth(2)

        tk.Label(row1, text="Agent A:").pack(side="left")
        self.algo_a_var = tk.StringVar(value="Alpha-Beta")
        ttk.Combobox(
            row1, textvariable=self.algo_a_var,
            values=ALGO_OPTIONS, width=10, state="readonly"
        ).pack(side="left", padx=(0, 12))

        tk.Label(row1, text="Agent B:").pack(side="left")
        self.algo_b_var = tk.StringVar(value="Alpha-Beta")
        ttk.Combobox(
            row1, textvariable=self.algo_b_var,
            values=ALGO_OPTIONS, width=10, state="readonly"
        ).pack(side="left")

        # ── Controls row 2: action buttons ──
        row2 = tk.Frame(self.root, pady=2)
        row2.pack()

        tk.Button(row2, text="Step (1 move)",
                  command=self.step_once, width=13).pack(side="left", padx=4)
        self.autoplay_btn = tk.Button(
            row2, text="▶ Auto Play",
            command=self.toggle_autoplay, width=13
        )
        self.autoplay_btn.pack(side="left", padx=4)
        tk.Button(row2, text="Reset",
                  command=self.reset, width=10).pack(side="left", padx=4)

        # ── Human mode hint ──
        tk.Label(
            self.root,
            text="Human turn (Agent A): Arrow keys or WASD",
            font=("Arial", 8), fg="gray"
        ).pack()

        # ── Metrics label ──
        self.metrics_label = tk.Label(
            self.root, text="", font=("Courier", 9), justify="left"
        )
        self.metrics_label.pack(pady=4)

        # ── Log box ──
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill="both", padx=6, pady=(0, 6))
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        self.log_box = tk.Text(
            log_frame, height=8, width=72,
            font=("Courier", 8), state="disabled",
            yscrollcommand=scrollbar.set
        )
        self.log_box.pack(side="left", fill="both")
        scrollbar.config(command=self.log_box.yview)

    def _bind_keys(self):
        """Arrow / WASD keys move Agent A when it's A's turn (human mode)."""
        key_map = {
            "Up": (-1, 0), "w": (-1, 0),
            "Down": (1, 0), "s": (1, 0),
            "Left": (0, -1), "a": (0, -1),
            "Right": (0, 1), "d": (0, 1),
        }
        def on_key(event):
            if self._auto_playing:
                return
            state = self.grid.get_state()
            if state["turn"] != "A" or not state["treasures"]:
                return
            move = key_map.get(event.keysym)
            if move and move in get_valid_moves(state, "A"):
                new_state = apply_move(state, move)
                self.grid.update_state(new_state)
                self._log(f"Human A → {move}")
                self._refresh_metrics(new_state, algo="Human", nodes=0,
                                      pruned=None, runtime=0.0)
                self.draw()
                self._check_game_over(new_state)

        self.root.bind("<Key>", on_key)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self):
        self.canvas.delete("all")
        state = self.grid.get_state()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                pos = (r, c)

                if pos in state["walls"]:
                    color = COLORS["wall"]
                elif pos in state["traps"]:
                    color = COLORS["trap"]
                elif pos in state["treasures"]:
                    color = COLORS["treasure"]
                else:
                    color = COLORS["empty"]

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#cfd8dc"
                )

                # Labels inside cells
                if pos in state["traps"]:
                    self.canvas.create_text(
                        x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2,
                        text="✕", font=("Arial", 10, "bold"), fill="#7b1fa2"
                    )
                elif pos in state["treasures"]:
                    self.canvas.create_text(
                        x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2,
                        text="★", font=("Arial", 10, "bold"), fill="#1565c0"
                    )

        # Agent A
        ar, ac = state["a_pos"]
        self.canvas.create_oval(
            ac * CELL_SIZE + 4, ar * CELL_SIZE + 4,
            ac * CELL_SIZE + CELL_SIZE - 4, ar * CELL_SIZE + CELL_SIZE - 4,
            fill=COLORS["A"], outline="#2e7d32", width=2
        )
        self.canvas.create_text(
            ac * CELL_SIZE + CELL_SIZE // 2,
            ar * CELL_SIZE + CELL_SIZE // 2,
            text="A", font=("Arial", 9, "bold"), fill="#1b5e20"
        )

        # Agent B
        br, bc = state["b_pos"]
        self.canvas.create_oval(
            bc * CELL_SIZE + 4, br * CELL_SIZE + 4,
            bc * CELL_SIZE + CELL_SIZE - 4, br * CELL_SIZE + CELL_SIZE - 4,
            fill=COLORS["B"], outline="#b71c1c", width=2
        )
        self.canvas.create_text(
            bc * CELL_SIZE + CELL_SIZE // 2,
            br * CELL_SIZE + CELL_SIZE // 2,
            text="B", font=("Arial", 9, "bold"), fill="#b71c1c"
        )

        # Score header
        self.canvas.create_rectangle(0, 0, GRID_SIZE * CELL_SIZE, 18,
                                     fill="#37474f", outline="")
        self.canvas.create_text(
            GRID_SIZE * CELL_SIZE // 2, 9,
            text=(f"A score: {state['a_score']}   "
                  f"B score: {state['b_score']}   "
                  f"Turn: {state['turn']}   "
                  f"Treasures left: {len(state['treasures'])}"),
            fill="white", font=("Arial", 9, "bold")
        )

    # ── Game logic ────────────────────────────────────────────────────────────

    def _run_agent(self, state):
        """Run the appropriate algorithm for the current player. Returns new_state."""
        turn = state["turn"]
        algo = self.algo_a_var.get() if turn == "A" else self.algo_b_var.get()
        depth = self.depth_var.get()

        if algo == "Minimax":
            move, nodes, runtime = minimax(state, depth)
            pruned = None
        elif algo == "Alpha-Beta":
            move, nodes, pruned, runtime = alphabeta(state, depth)
        else:  # Random
            move = random_move(state)
            nodes, pruned, runtime = 0, None, 0.0

        if move is None:
            return state, algo, 0, None, 0.0   # no valid move

        new_state = apply_move(state, move)
        self._log(
            f"Agent {turn} [{algo}] depth={depth} "
            f"move={move}  nodes={nodes}"
            + (f"  pruned={pruned}" if pruned is not None else "")
            + f"  {runtime*1000:.1f}ms"
        )
        self._refresh_metrics(new_state, algo, nodes, pruned, runtime)
        return new_state, algo, nodes, pruned, runtime

    def step_once(self):
        """Advance the game by exactly one move."""
        state = self.grid.get_state()
        if not state["treasures"]:
            self._log("Game already over. Press Reset.")
            return

        new_state, *_ = self._run_agent(state)
        self.grid.update_state(new_state)
        self.draw()
        self._check_game_over(new_state)

    def toggle_autoplay(self):
        if self._auto_playing:
            self._stop_autoplay()
        else:
            self._start_autoplay()

    def _start_autoplay(self):
        self._auto_playing = True
        self.autoplay_btn.config(text="■ Stop")
        self._autoplay_tick()

    def _stop_autoplay(self):
        self._auto_playing = False
        self.autoplay_btn.config(text="▶ Auto Play")
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _autoplay_tick(self):
        if not self._auto_playing:
            return
        state = self.grid.get_state()
        if not state["treasures"]:
            self._stop_autoplay()
            self._check_game_over(state)
            return

        new_state, *_ = self._run_agent(state)
        self.grid.update_state(new_state)
        self.draw()

        if not new_state["treasures"]:
            self._stop_autoplay()
            self._check_game_over(new_state)
            return

        self._after_id = self.root.after(AUTO_PLAY_DELAY_MS, self._autoplay_tick)

    def _check_game_over(self, state):
        if not state["treasures"]:
            a, b = state.get("a_score", 0), state.get("b_score", 0)
            if a > b:
                result = f"Agent A wins! ({a} vs {b})"
            elif b > a:
                result = f"Agent B wins! ({b} vs {a})"
            else:
                result = f"Draw! ({a} vs {b})"
            self._log(f"=== GAME OVER: {result} ===")
            self.metrics_label.config(text=f"GAME OVER — {result}")

    def reset(self):
        self._stop_autoplay()
        self.grid.reset()
        self.metrics_label.config(text="")
        self.draw()
        self._log("─── New game ───")

    # ── Depth selector ────────────────────────────────────────────────────────

    def _select_depth(self, value):
        self.depth_var.set(value)
        for d, btn in self._depth_buttons.items():
            if d == value:
                btn.config(bg="#1565c0", fg="white", relief="flat")
            else:
                btn.config(bg="#e0e0e0", fg="black", relief="flat")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refresh_metrics(self, state, algo, nodes, pruned, runtime):
        turn_display = "B" if state["turn"] == "A" else "A"   # just moved
        parts = [
            f"Agent {turn_display} [{algo}]",
            f"Depth {self.depth_var.get()}",
            f"Nodes {nodes}",
            f"Time {runtime*1000:.2f} ms",
        ]
        if pruned is not None:
            ratio = pruned / nodes if nodes else 0
            parts.append(f"Pruned {pruned} ({ratio:.0%})")
        self.metrics_label.config(text="   ".join(parts))

    def _log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
