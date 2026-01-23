treasure-hunt

developers: Austin Nguyen, Duy Ly, Sungmin Cha

This project creates a treasure hunt game on a grid of size N x N. The grid contains:
- exactly one treasure
- exactly one trap
- walls that cover about 20% of the grid

The user chooses the grid size (minimum 8). The program opens a tkinter window displaying the 2d grid.

Requirements:
- Python 3.12 (or Python version with tkinter available)
- NumPy

How to set up and run:

1. Open a terminal and go to the project directory:  
   cd path/to/treasure-hunt

3. Create a python 3.12 virtual environment:  
   python3.12 -m venv venv

4. Activate the virtual environment:  
   On macOS:
   source venv/bin/activate

5. Install dependencies:  
   pip install -r requirements.txt

6. Run the program:  
   python main.py

7. When prompted, enter a grid size (an integer 8 or larger). The program will:
   - generate an N x N grid
   - place one treasure, one trap, and walls
   - open a window showing the 2d grid
