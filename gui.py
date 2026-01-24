import tkinter as tk
from config import CELL_SIZE, COLORS, MIN_GRID_SIZE, SYMBOLS
from grid import Grid

# Treasure Map
class TreasureHuntMap:
    def __init__(self, grid_array, *, root: tk.Tk | None = None, on_reset=None):
        self.grid_array = grid_array
        self.grid_size = len(grid_array)
        self.window = root or tk.Tk()
        self.window.title("Treasure Hunt")

        self._on_reset = on_reset

        self.frame = tk.Frame(self.window)
        self.frame.pack(fill="both", expand=True)

        table_size = self.grid_size * CELL_SIZE
        self.canvas = tk.Canvas(self.frame, width=table_size, height=table_size, bg='white')

        self.canvas.pack(padx=10, pady=(10, 6))

        self.draw_grid()

        self.reset_button = tk.Button(self.frame, text="Reset", command=on_reset)
        self.reset_button.pack(pady=(6, 10))
        
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
                    case _:
                        color = COLORS['empty']

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#a6a6a6', width=1)

                symbol = SYMBOLS.get(cell_value, '')

                if symbol != '':
                    self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text=symbol, font=('Arial', 12, 'bold'), fill = 'black')

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

        self._prompt_frame: tk.Frame | None = None
        self._map_view: TreasureHuntMap | None = None
        self._error_var = tk.StringVar(value="")
        self._size_var = tk.StringVar()

        self._show_size_prompt()

    def _show_size_prompt(self):
        frame = tk.Frame(self.root, padx=16, pady=16)
        frame.pack(fill="both", expand=True)
        self._prompt_frame = frame

        title = tk.Label(frame, text="Treasure Hunt", font=("Arial", 16, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        label = tk.Label(frame, text=f"Enter grid size (min {MIN_GRID_SIZE}):")
        label.pack(anchor="w")

        entry = tk.Entry(frame, textvariable=self._size_var, width=12)
        entry.pack(anchor="w", pady=(6, 10))
        entry.focus_set()
        entry.bind("<Return>", lambda _event: self._submit_size())

        submit = tk.Button(frame, text="Submit", command=self._submit_size)
        submit.pack(anchor="w")

        error = tk.Label(frame, textvariable=self._error_var, fg="red")
        error.pack(anchor="w", pady=(10, 0))

    def _submit_size(self):
        raw = self._size_var.get().strip()

        # Check for if input is valid and in range
        try:
            size = int(raw)
        except ValueError:
            self._error_var.set("Please enter a valid integer.")
            return

        if size < MIN_GRID_SIZE:
            self._error_var.set(f"Grid size must be at least {MIN_GRID_SIZE}.")
            return

        # Destroy the prompt frame
        if self._prompt_frame is not None:
            self._prompt_frame.destroy()
            self._prompt_frame = None

        # Generates and displays the map
        grid = Grid(size)
        self._map_view = TreasureHuntMap(grid.get_grid(), root=self.root, on_reset=self.reset)

    def reset(self):
        # Destroy map (if any)
        if self._map_view is not None:
            self._map_view.destroy()
            self._map_view = None

        # Reset prompt state
        self._error_var.set("")
        self._size_var.set("")
        self._show_size_prompt()

    def run(self):
        self.root.mainloop()
