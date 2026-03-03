from __future__ import annotations
import heapq
from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
import time

Coord = Tuple[int, int]

GoalArray = List[Coord]

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

def greedy(grid, start: Coord, goal_array: GoalArray) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}
    t0 = time.perf_counter()
    full_path = []
    current_start = start
    total_nodes_expanded = 0

    for goal in goal_array:
        heap = [(0, current_start)]
        visited = {current_start}
        parent = {}
        nodes_expanded = 0
        path_to_goal = []

        while heap:
            _, current = heapq.heappop(heap)
            nodes_expanded += 1

            if current == goal:
                path_to_goal = build_path(parent, current_start, goal)
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

        if not path_to_goal:
            break

        if not full_path:
            full_path = path_to_goal
        else:
            full_path = full_path + path_to_goal[1:]
        total_nodes_expanded += nodes_expanded
        current_start = goal

    t1 = time.perf_counter()
    return SearchResult(path=full_path, nodes_expanded=total_nodes_expanded, runtime=t1 - t0)

def _manhattan_distance(current: Coord, goal: Coord) -> int:
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])