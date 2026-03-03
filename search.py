from __future__ import annotations
import heapq
from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
import time, math

Coord = Tuple[int, int]

@dataclass
class SearchResult:
    path: List[Coord]
    nodes_expanded: int
    runtime: float


def get_successor_functions(pos: Coord, grid_size: int) -> Iterable[Coord]:
    row, col = pos
    for d_row, d_col in [(-1, 0), (0, 1), (1, 0), (0, -1)]:  # up, right, down, left
        next_row, next_col = row + d_row, col + d_col
        if 0 <= next_row < grid_size and 0 <= next_col < grid_size:
            yield next_row, next_col


def build_path(parent: Dict[Coord, Coord], start: Coord, goal: Coord) -> List[Coord]:
    if goal not in parent and goal != start:
        return []

    path = [goal]
    current = goal
    while current != start:
        current = parent[current]
        path.append(current)
    path.reverse()
    return path

def bfs(grid, start: Coord, goal: Coord) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    explored = []

    t0 = time.perf_counter()

    q = deque([start])
    visited = {start}
    parent = {}
    nodes_expanded = 0

    while q:
        current = q.popleft()
        nodes_expanded += 1
        explored.append(current)
        
        if current == goal:
            break

        for nb in get_successor_functions(current, size):
            row, col = nb
            if grid[row][col] in blocked:
                continue
            if nb in visited:
                continue
            visited.add(nb)
            parent[nb] = current
            q.append(nb)

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    print(f"BFS Explored: {explored}")

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def dfs(grid, start: Coord, goal: Coord) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    explored = []

    t0 = time.perf_counter()

    stack = [start]
    visited = {start}
    parent = {}
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1
        explored.append(current)

        if current == goal:
            break

        for nb in reversed(list(get_successor_functions(current, size))):
            row, col = nb
            if grid[row][col] in blocked:
                continue
            if nb in visited:
                continue
            visited.add(nb)
            parent[nb] = current
            stack.append(nb)

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    print(f"DFS Explored: {explored}")

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def ucs(grid, start: Coord, goal: Coord) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    explored = []

    t0 = time.perf_counter()

    # Min-heap: (cost, row, col)
    start_row, start_col = start
    heap = [(0, start_row, start_col)]
    visited = set()
    parent = {}
    nodes_expanded = 0

    while heap:
        cost, row, col = heapq.heappop(heap)
        current = (row, col)

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1
        explored.append(current)

        if current == goal:
            break

        for nb in get_successor_functions(current, size):
            nrow, ncol = nb
            if grid[nrow][ncol] in blocked:
                continue
            if nb in visited:
                continue
            new_cost = cost + 1
            heapq.heappush(heap, (new_cost, nrow, ncol))
            parent[nb] = current

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    print(f"UCS Explored: {explored}")

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def a_star(grid, start: Coord, goal: Coord) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    explored = []

    t0 = time.perf_counter()

    heap = [(_manhattan_distance(start, goal), 0, start)]
    visited = set()
    parent = {}
    nodes_expanded = 0

    while heap:
        f, g, current_coord = heapq.heappop(heap)
        current = current_coord

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1
        explored.append((current, f))

        if current == goal:
            break

        for nb in get_successor_functions(current, size):
            nrow, ncol = nb
            if grid[nrow][ncol] in blocked:
                continue
            if nb in visited:
                continue
            new_g = g + 1
            new_h = _manhattan_distance(nb, goal)
            new_f = new_g + new_h
            heapq.heappush(heap, (new_f, new_g, (nrow, ncol)))
            parent[nb] = current

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    print(f"A* Explored: {explored}")

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def greedy(grid, start: Coord, goal: Coord) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    explored = []

    t0 = time.perf_counter()

    heap = [(0, start)] # (heuristic value, (row, col))
    visited = {start}
    parent = {}
    nodes_expanded = 0

    while heap:
        h_cost, current = heapq.heappop(heap)
        nodes_expanded += 1
        explored.append((current, h_cost))

        if current == goal:
            break

        for nb in get_successor_functions(current, size):
            nrow, ncol = nb
            if grid[nrow][ncol] in blocked:
                continue
            if nb in visited:
                continue
            
            visited.add(nb)
            heuristic_cost = _manhattan_distance(nb, goal)
            heapq.heappush(heap, (heuristic_cost, nb))
            parent[nb] = current

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    print(f"Greedy Explored: {explored}")

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def _manhattan_distance(current: Coord, goal: Coord) -> int:
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

def evaluate_state(grid_array, agent_pos, opponent_pos, treasures, history_a=None, history_b=None):
    if not treasures:
        return 0

    # Distance for A
    dist_a = min(_manhattan_distance(agent_a_pos, t) for t in treasures)
    # Distance for B
    dist_b = min(_manhattan_distance(agent_b_pos, t) for t in treasures)

    # Score = (Proximity Advantage) + (Treasure Count Advantage)
    # If A is closer, score is positive. If B is closer, score is negative.
    score = (dist_b - dist_a) 
    
    # Add penalties for history to stop circling
    if history_a and agent_a_pos in history_a: score -= 50
    if history_b and agent_b_pos in history_b: score += 50 # Help B avoid circles too

    return score

def alpha_beta(grid, depth, alpha, beta, is_maximizing, agent_pos, opp_pos, treasures, history=None):
    # Terminal state or depth limit
    if depth == 0 or not treasures:
        return evaluate_state(grid, agent_pos, opp_pos, treasures) + depth, None

    nodes_expanded = 1
    best_move = None
    
    # Get possible moves (Up, Right, Down, Left)
    possible_moves = []
    current_p = agent_pos if is_maximizing else opp_pos
    for next_p in get_successor_functions(current_p, len(grid)):
        if grid[next_p[0]][next_p[1]] != 3: # Not a wall
            possible_moves.append(next_p)

    if is_maximizing:
        max_eval = -math.inf
        for move in possible_moves:
            # Simulate move
            eval, _ = alpha_beta(grid, depth - 1, alpha, beta, False, move, opp_pos, treasures)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break # Pruning
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in possible_moves:
            eval, _ = alpha_beta(grid, depth - 1, alpha, beta, True, agent_pos, move, treasures)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break # Pruning
        return min_eval, best_move