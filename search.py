from __future__ import annotations
import heapq
from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
import time

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

def a_star(grid, start: Coord, goal: Coord, heuristic) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    explored = []

    t0 = time.perf_counter()

    start_row, start_col = start
    heap = [(heuristic, 0, start_row, start_col)]
    visited = set()
    parent = {}
    nodes_expanded = 0

    while heap:
        f, g, row, col = heapq.heappop(heap)
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
            new_g = g + 1
            new_f = new_g + heuristic
            heapq.heappush(heap, (new_f, new_g, nrow, ncol))
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
        cost, current = heapq.heappop(heap)
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
            
            visited.add(nb)
            heuristic_cost = _manhattan_distance(nb, goal)
            heapq.heappush(heap, (heuristic_cost, nb))
            parent[nb] = current

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    print(f"Greedy Explored: {explored}")

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def _manhattan_distance(current: Coord, nb: Coord) -> int:
    return abs(current[0] - nb[0]) + abs(current[1] - nb[1])