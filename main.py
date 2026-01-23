from gui import TreasureHuntGUI
from config import MIN_GRID_SIZE
from grid import Grid

def main():

    while True:
        try:
            grid_size = int(input("Enter the size of the grid (min 8): "))
            if grid_size >= MIN_GRID_SIZE:
                break
            else:
                print(f"Grid size must be at least {MIN_GRID_SIZE}")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
        
    grid = Grid(grid_size)
    grid_array = grid.get_grid()
    gui = TreasureHuntGUI(grid_array)
    
    gui.run()



if __name__ == "__main__":
    main()