import tkinter as tk
from config import CELL_SIZE, COLORS, SYMBOLS
from grid import Grid
from search import SearchResult, bfs, dfs, ucs, greedy

# Treasure Map
class TreasureHuntMap:
    def __init__(self, grid_array, *, root: tk.Tk | None = None, on_reset=None):
        self.grid_array = grid_array
        self.grid_size = len(grid_array)
        self.window = root or tk.Tk()
        self.window.title("Treasure Hunt")

        self._on_reset = on_reset
        self._path_items: list[int] = []

        self.frame = tk.Frame(self.window)
        self.frame.pack(fill="both", expand=True)

        table_size = self.grid_size * CELL_SIZE
        self.canvas = tk.Canvas(self.frame, width=table_size, height=table_size, bg="white")

        self.canvas.pack(padx=10, pady=(10, 6))

        self.draw_grid()

        controls = tk.Frame(self.frame)
        controls.pack(pady=(6, 4))

        tk.Button(controls, text="Run BFS", command=self.run_bfs).pack(side="left", padx=4)
        tk.Button(controls, text="Run DFS", command=self.run_dfs).pack(side="left", padx=4)
        tk.Button(controls, text="Run UCS", command=self.run_ucs).pack(side="left", padx=4)
        tk.Button(controls, text="Run Greedy", command=self.run_greedy).pack(side="left", padx=4)
        if self._on_reset:
            tk.Button(controls, text="Reset", command=self._on_reset).pack(side="left", padx=4)
        else:
            tk.Button(controls, text="Reset", command=self.window.destroy).pack(side="left", padx=4)
        self._metrics_var = tk.StringVar(value="")
        self._metrics_label = tk.Label(self.frame, textvariable=self._metrics_var, anchor="w", justify="left")
        self._metrics_label.pack(fill="x", padx=10, pady=(2, 10))
        
    def draw_grid(self):
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
                        color = COLORS['start']
                    case _:
                        color = COLORS['empty']

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#a6a6a6', width=1)

                symbol = SYMBOLS.get(cell_value, '')

                if symbol != '':
                    self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text=symbol, font=('Arial', 12, 'bold'), fill = 'black')

    def _find_start_and_goal(self):
        start = None
        goal = None

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = self.grid_array[row][col]
                if value == 1:
                    goal = (row, col)
                if start is None and value == 4:
                    start = (row, col)

        if start is None:
            start = (0, 0)
        if goal is None:
            goal = (self.grid_size - 1, self.grid_size - 1)

        return start, goal

    def _show_result(self, algo_name: str, result: SearchResult):
        for item_id in self._path_items:
            self.canvas.delete(item_id)
        self._path_items.clear()

        path = result.path
        if path:
            for (row, col) in path:
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                pad = 4
                item_id = self.canvas.create_rectangle(
                    x1 + pad,
                    y1 + pad,
                    x2 - pad,
                    y2 - pad,
                    outline="green",
                    width=2,
                )
                self._path_items.append(item_id)

        path_len = max(len(path) - 1, 0)
        self._metrics_var.set(
            f"{algo_name} — Path length: {path_len}, "
            f"Nodes expanded: {result.nodes_expanded}, "
            f"Time: {result.runtime * 1000:.2f} ms"
        )

    def _run_search(self, algo_name: str, func):
        start, goal = self._find_start_and_goal()
        result = func(self.grid_array, start, goal)
        self._show_result(algo_name, result)

    def run_bfs(self):
        self._run_search("BFS", bfs)

    def run_dfs(self):
        self._run_search("DFS", dfs)

    def run_ucs(self):
        self._run_search("UCS", ucs)

    def run_greedy(self):
        self._run_search("Greedy", greedy)

    def destroy(self):
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
        self._map_view = TreasureHuntMap(grid.get_grid(), root=self.root, on_reset=self.reset)

    def reset(self):
        # Destroy map (if any)
        if self._map_view is not None:
            self._map_view.destroy()
            self._map_view = None

        self._create_new_map()

    def run(self):
        self.root.mainloop()
