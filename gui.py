import tkinter as tk
import config
from config import CELL_SIZE, COLORS, SYMBOLS

class TreasureHuntGUI:
    def __init__(self, grid_array):
        self.grid_array = grid_array
        self.grid_size = len(grid_array)
        self.window = tk.Tk()
        self.window.title("Treasure Hunt")

        table_size = self.grid_size * CELL_SIZE
        self.canvas = tk.Canvas(self.window, width=table_size, height=table_size, bg='white')

        self.canvas.pack(padx=10, pady=10)

        self.draw_grid()
        
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

                symbol = SYMBOLS[cell_value]

                if symbol != '':
                    self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text=symbol, font=('Arial', 12, 'bold'), fill = 'black')
    
    def run(self):
        self.window.mainloop()
                
                
