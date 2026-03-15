from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np

from bayes import BayesianBelief, SensorModel
from search import a_star

Coord = Tuple[int, int]


class BayesianAgent:
    """Optimized Bayesian treasure hunting agent."""

    def __init__(
        self,
        grid,
        scan_radius: int,
        false_positive: float,
        false_negative: float,
    ):
        self.grid = grid
        self.sensor_model = SensorModel(false_positive, false_negative)
        self.belief = BayesianBelief(grid, scan_radius, self.sensor_model)
        self.belief.initialize_uniform_prior()

        self.moves = 0
        self.scans = 0
        self.treasures_found = 0
        self.entropy_history: List[float] = []

        self.unreachable = set()

    # SCAN
    def scan(self) -> bool:
        """Perform a sensor scan and update belief."""
        position = self.grid.agent_coords
        observation = self.belief.simulate_observation(position)
        self.belief.update(position, observation)
        entropy = self.belief.compute_entropy()
        self.entropy_history.append(entropy)
        self.scans += 1
        return observation

    # TARGET SELECTION
    def choose_targets(self, k: int = 10) -> List[Coord]:
        """
        Return top-k highest probability cells.
        Avoid unreachable cells.
        """

        belief = self.belief.belief

        flat = belief.flatten()
        indices = flat.argsort()[::-1]

        targets = []
        size = self.grid.grid_size

        for idx in indices:
            r = idx // size
            c = idx % size
            cell = (r, c)

            if cell in self.unreachable:
                continue

            if self.grid.is_blocked(cell):
                continue

            targets.append(cell)
            if len(targets) >= k:
                break

        return targets

    # MOVE
    def move_to_target(self) -> bool:
        """Move toward best reachable belief target."""
        targets = self.choose_targets()
        start = self.grid.agent_coords

        for target in targets:
            result = a_star(self.grid.get_grid(), start, target)

            if len(result.path) >= 2:
                next_cell = result.path[1]
                old_row, old_col = start
                new_row, new_col = next_cell

                if self.grid.get_grid()[old_row, old_col] == 4:
                    self.grid.get_grid()[old_row, old_col] = 0

                self.grid.agent_coords = next_cell
                if not self.grid.is_treasure(next_cell):
                    self.grid.get_grid()[new_row, new_col] = 4

                self.moves += 1
                return True

            # mark unreachable
            self.unreachable.add(target)

        return False

    # STEP
    def step(self) -> Dict[str, object]:
        observation = self.scan()
        moved = self.move_to_target()

        found_treasure = False
        agent_pos = self.grid.agent_coords

        if self.grid.is_treasure(agent_pos):
            self.grid.remove_treasure(agent_pos)
            self.treasures_found += 1
            # reset belief after collecting treasure
            self.belief.initialize_uniform_prior()
            self.unreachable.clear()
            found_treasure = True

        return {
            "observation": observation,
            "moved": moved,
            "found_treasure": found_treasure,
            "position": self.grid.agent_coords,
        }

    # RUN LOOP
    def run_until_treasure(self, max_steps: int | None = None) -> int:
        """Repeat step() until one treasure is collected."""
        start_found = self.treasures_found
        steps = 0

        while self.treasures_found == start_found:
            if max_steps is not None and steps >= max_steps:
                break
            self.step()
            steps += 1

        return steps