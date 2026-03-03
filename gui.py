import tkinter as tk
from config import CELL_SIZE, COLORS, SYMBOLS
from grid import Grid
from search import SearchResult, bfs, dfs, ucs, greedy, a_star, alpha_beta
import time

# Treasure Map
class TreasureHuntMap:
    def __init__(self, grid: Grid, *, root: tk.Tk | None = None, on_reset=None):
        self.grid = grid
        self.grid_array = grid.get_grid()
        self.grid_size = len(self.grid_array)
        self.window = root or tk.Tk()
        self.window.title("Adversarial Treasure Hunt")
        
        self._on_reset = on_reset
        self.turn = "A"  # Starts with Agent A
        self.scores = {"A": 0, "B": 0}
        self.is_running = False

        # UI Layout
        self.frame = tk.Frame(self.window)
        self.frame.pack(fill="both", expand=True)

        table_size = self.grid_size * CELL_SIZE
        self.canvas = tk.Canvas(self.frame, width=table_size, height=table_size, bg="white")
        self.canvas.pack(padx=10, pady=10)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(pady=5)

        self.btn_ab = tk.Button(controls, text="Start Alpha-Beta (Depth 4)", command=lambda: self.start_game("AB"))
        self.btn_ab.pack(side="left", padx=4)
        
        if self._on_reset:
            tk.Button(controls, text="Reset Grid", command=self._on_reset).pack(side="left", padx=4)

        # Metrics & Scoreboard
        self._stats_var = tk.StringVar(value="Scores -> A: 0 | B: 0")
        tk.Label(self.frame, textvariable=self._stats_var, font=('Arial', 12, 'bold')).pack()
        
        self._metrics_var = tk.StringVar(value="Ready to begin...")
        tk.Label(self.frame, textvariable=self._metrics_var, fg="blue").pack()

        self.move_history_a = [] # Store last 4 positions for Agent A
        self.move_history_b = []
        self.max_history = 4

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1, y1 = col * CELL_SIZE, row * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                val = self.grid_array[row][col]
                color = COLORS.get('empty', 'white')
                if val == 1: color = COLORS['treasure']
                elif val == 2: color = COLORS['trap']
                elif val == 3: color = COLORS['wall']
                elif val == 4: color = "blue"  # Agent A
                elif val == 5: color = "red"   # Agent B

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#a6a6a6')
                
                # Draw Symbols
                symbol = SYMBOLS.get(val, '')
                if val == 4: symbol = "A"
                if val == 5: symbol = "B"
                if symbol:
                    self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text=symbol, font=('Arial', 10, 'bold'))

    def start_game(self, algo):
        if self.is_running: return
        self.is_running = True
        self.game_loop()

    def game_loop(self):
        if not self.grid.treasures or not self.is_running:
            self.end_game()
            return

        if self.turn == "A":
            self.move_agent_a()
            self.turn = "B"
        else:
            self.move_agent_b()
            self.turn = "A"

        self.draw_grid()
        self._stats_var.set(f"Scores -> A: {self.scores['A']} | B: {self.scores['B']}")
        
        # Delay for visualization
        self.window.after(500, self.game_loop)

    def move_agent_a(self):
        t0 = time.perf_counter()
        
        # Pass the history to the alpha_beta function
        _, next_move = alpha_beta(
            self.grid_array, 
            4, 
            float('-inf'), 
            float('inf'), 
            True, 
            self.grid.agent_a_pos, 
            self.grid.agent_b_pos, 
            self.grid.treasures,
            history=self.move_history_a  # Pass history here
        )
        t1 = time.perf_counter()

        if next_move:
            # Update history buffer
            self.move_history_a.append(self.grid.agent_a_pos)
            if len(self.move_history_a) > self.max_history:
                self.move_history_a.pop(0)
                
            self.update_position("A", next_move)
            self._metrics_var.set(f"AI (A) thought for {(t1-t0)*1000:.2f}ms")

    def move_agent_b(self):
        """
        Agent B uses Alpha-Beta as the MINIMIZING player.
        It tries to reach treasures to 'steal' them from Agent A or 
        move to states that are bad for Agent A.
        """
        t0 = time.perf_counter()
        
        # We call alpha_beta with is_maximizing=False 
        # because the evaluation function is written from Agent A's perspective.
        _, next_move = alpha_beta(
            self.grid_array, 
            4, # Depth
            float('-inf'), 
            float('inf'), 
            False, # is_maximizing = False for Agent B
            self.grid.agent_a_pos, 
            self.grid.agent_b_pos, 
            self.grid.treasures,
            history=self.move_history_b # Ensure history is tracked for B too
        )
        t1 = time.perf_counter()

        if next_move:
            # Update history for B to prevent circling
            self.move_history_b.append(self.grid.agent_b_pos)
            if len(self.move_history_b) > self.max_history:
                self.move_history_b.pop(0)
                
            self.update_position("B", next_move)
            # Optional: Log performance for your report
            print(f"Agent B moved to {next_move} (Time: {(t1-t0)*1000:.2f}ms)")
        else:
            # Fallback: if no move found (trapped), stay put or try random
            print("Agent B is trapped!")

    def update_position(self, agent_id, new_move):
        # 1. Validation: Don't move into walls
        if self.grid_array[new_move] == 3:
            print(f"Warning: Agent {agent_id} attempted to move into a wall at {new_move}")
            return

        old_pos = self.grid.agent_a_pos if agent_id == "A" else self.grid.agent_b_pos
        
        # 2. Update Grid Array (Clear old spot)
        self.grid_array[old_pos] = 0 
        
        # 3. Handle Items
        cell_type = self.grid_array[new_move]
        if cell_type == 1: # Treasure collected
            self.scores[agent_id] += 1
            if new_move in self.grid.treasures:
                self.grid.treasures.remove(new_move)
        elif cell_type == 2: # Trap hit
            self.scores[agent_id] -= 1

        # 4. Update internal state
        if agent_id == "A":
            self.grid.agent_a_pos = new_move
            self.grid_array[new_move] = 4
        else:
            self.grid.agent_b_pos = new_move
            self.grid_array[new_move] = 5

    def end_game(self):
        self.is_running = False
        winner = "Agent A" if self.scores["A"] > self.scores["B"] else "Agent B"
        if self.scores["A"] == self.scores["B"]: winner = "It's a Tie!"
        messagebox.showinfo("Game Over", f"Winner: {winner}\nFinal Score - A: {self.scores['A']} B: {self.scores['B']}")

    def destroy(self):
        self.is_running = False
        self.frame.destroy()

'''
Main app of the program
    1) Prompts user for grid size (checks for validity as well)
    2) Generates the grid and displays the map
'''
class TreasureHuntApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Treasure Hunt")
        
        self._map_view: TreasureHuntMap | None = None
        self._create_new_map()

    def _create_new_map(self):
        grid = Grid(20)
        self._map_view = TreasureHuntMap(grid, root=self.root, on_reset=self.reset)

    def reset(self):
        # Destroy map (if any)
        if self._map_view is not None:
            self._map_view.destroy()
            self._map_view = None

        self._create_new_map()

    def run(self):
        self.root.mainloop()
