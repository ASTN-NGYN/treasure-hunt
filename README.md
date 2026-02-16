treasure-hunt

developers: Austin Nguyen, Duy Ly, Sungmin Cha

This project creates a treasure hunt game on a grid of size 20 x 20. The grid contains:
- 2–3 treasures (T)
- 2 traps (X)
- several static walls (#) that cover about 20% of the grid

The program displays the grid directly. Treasures, traps, and walls are visually distinct.

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

6. The program will:
   - generate a 20 x 20 grid with 2–3 treasures, 2 traps, and walls
   - open a window showing the 2d grid
   - provide Run BFS, DFS, UCS, Greedy, and A* buttons
   - provide a Reset button to regenerate a new grid configuration


Experimentation & Results:
   - The better searching algorithm depends on the placement of the target grid, wall and trap placements, as well as the starting point. We noticed that if the target was beneath the start (vertically further), then DFS would perform better in fewer steps. Whereas, if the target was place somewhere horizontal, then BFS and UCS would excel.
   - The reason being, the way we implemented DFS it would search down as far as possible and then backtrack.
   - For BFS, we visit neighboring/adjacent cells and then explore their neighboring cells. Essentially expanding in all directions from the start point.
   - For UCS, implementation wise it is very similar to BFS except we track cost. Inside of our heap, we track the cost of each cell. Whenever we pop from our heap, we are popping the least expensive grid position. As we are exploring our grid, we add the cost of new cells to our heap, and we pop from our heap the cheapest grid position to go to.
   - All in all, the position of the target relative to the position of the start point decided which search was better. DFS is good when the target is in the straight path of the start point. BFS and UCS is better if the target is closer in proximity.
   
   - For A*, we use Manhattan distance as an admissible heuristic. The heap stores (f, g, coord) where f(n) = g(n) + h(n). We always expand the node with the smallest f(n) value. This guarantees the shortest path when the heuristic is admissible.
   - For Greedy, the heap stores only (h, coord). We expand the node that appears closest to the goal (smallest h) without considering the cost so far g(n). It explores toward the goal greedily but does not guarantee the shortest path.
   - A* is better when the shortest path is important (it guarantees optimality). Greedy can be faster in terms of nodes expanded and runtime but may find a longer path.

Use of Generative AI Statement:

After generating our grid, we noticed there were cases where the start point was trapped by walls and/or traps which would make a solution for that grid impossible. We used AI to brainstorm solutions to this edge case. After looking at the ideas, we chose the solution of continuous regenerating grids until there was a valid grid. We decided upon this solution because this was a very rare edge case, so it would be highly unlikely of causing a runtime error.

Refactoring gui.py to call grid.py led to several attribute errors. Through AI debugging, we realized we were passing the data structure rather than an instance of the class, which fixed our inability to access specific methods and variables.

<img width="733" height="829" alt="image" src="https://github.com/user-attachments/assets/39c8f41c-e2be-42a8-9b50-ddcffab8e3c4" />

