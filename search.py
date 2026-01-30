from __future__ import annotations
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
    for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
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

    t0 = time.perf_counter()

    frontier = deque([start])
    visited = {start}
    parent: Dict[Coord, Coord] = {}
    nodes_expanded = 0

    while frontier:
        current = frontier.popleft()
        nodes_expanded += 1

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
            frontier.append(nb)

    path = build_path(parent, start, goal)
    t1 = time.perf_counter()

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def dfs(grid, start: Coord, goal: Coord) -> SearchResult:
    size = len(grid)
    blocked = {2, 3}

    t0 = time.perf_counter()

    stack = [start]
    visited = {start}
    parent: Dict[Coord, Coord] = {}
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1

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

    return SearchResult(path=path, nodes_expanded=nodes_expanded, runtime=t1 - t0)

def ucs(grid, start: Coord, goal: Coord) -> SearchResult:
    # start here!