treasure-hunt

developers: Austin Nguyen, Duy Ly, Sungmin Cha

This project creates a treasure hunt game on a grid of size N x N. The grid contains:
- exactly one treasure
- exactly one trap
- walls that cover about 20% of the grid

The user chooses the grid size (minimum 8) in a small  prompt window. After submitting, the program displays the 2d grid.

Requirements:
- Python 3.12 (or Python version with tkinter available)
- NumPy

How to set up and run:

1. Open a terminal and go to the project directory:  
   cd path/to/treasure-hunt

2. Create a python 3.12 virtual environment:  
   python3.12 -m venv venv

3. Activate the virtual environment:  
   On macOS:
   source venv/bin/activate

4. Install dependencies:  
   pip install -r requirements.txt

5. Run the program:  
   python main.py

6. In the GUI, enter a grid size and click Submit. The program will:
   - generate an N x N grid
   - place one treasure, one trap, and walls
   - open a window showing the 2d grid


Experimentation & Results:
   - The better searching algorithm depends on the placement of the target grid, wall and trap placements, as well as the starting point. We noticed that if the target was beneath the start (vertically further), then DFS would perform better in fewer steps. Whereas, if the target was place somewhere horizontal, then BFS and UCS would excel.
   - The reason being, the way we implemented DFS it would search down as far as possible and then backtrack.
   - For BFS, we visit neighboring/adjacent cells and then explore their neighboring cells. Essentially expanding in all directions from the start point.
   - For UCS, implementation wise it is very similar to BFS except we track cost. Inside of our heap, we track the cost of each cell. Whenever we pop from our heap, we are popping the least expensive grid position. As we are exploring our grid, we add the cost of new cells to our heap, and we pop from our heap the cheapest grid position to go to.
   - All in all, the position of the target relative to the position of the start point decided which search was better. DFS is good when the target is in the straight path of the start point. BFS and UCS is better if the target is closer in proximity.

Use of Generative AI Statement:

After generating our grid, we noticed there were cases where the start point was trapped by walls and/or traps which would make a solution for that grid impossible. We used AI to brainstorm solutions to this edge case. After looking at the ideas, we chose the solution of continuous regenerating grids until there was a valid grid. We decided upon this solution because this was a very rare edge case, so it would be highly unlikely of causing a runtime error.

<img width="1070" height="1256" alt="image" src="https://github.com/user-attachments/assets/20e0659a-e9bd-4190-91e3-de935f5e061f" />
