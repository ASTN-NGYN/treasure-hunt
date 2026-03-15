from __future__ import annotations

from typing import Dict, List, Tuple

from bayes import BayesianBelief, SensorModel
from search import a_star

Coord = Tuple[int, int]


class BayesianAgent:
    """Agent that combines Bayesian belief updates with A* movement."""

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

    def scan(self) -> bool:
        """Perform a scan at the agent position and update belief."""
        position = self.grid.agent_coords
        observation = self.belief.simulate_observation(position)
        self.belief.update(position, observation)
        self.entropy_history.append(self.belief.compute_entropy())
        self.scans += 1
        return observation

    def choose_target(self) -> Coord:
        """Select the next exploration target from maximum belief."""
        return self.belief.argmax_cell()

    def move_to_target(self, target: Coord) -> bool:
        """Move the agent one step toward target using existing A*."""
        start = self.grid.agent_coords

        for _ in range(len(self.grid.valid_cells())):
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

            # Suppress unreachable/current target and try the next best belief cell.
            self.belief.belief[target[0], target[1]] = 0.0
            self.belief.normalize()
            target = self.choose_target()

        return False

    def step(self) -> Dict[str, object]:
        """Run one Bayesian scan-and-move iteration and collect treasure if reached."""
        observation = self.scan()
        target = self.choose_target()
        moved = self.move_to_target(target)

        found_treasure = False
        agent_pos = self.grid.agent_coords

        if self.grid.is_treasure(agent_pos):
            self.grid.remove_treasure(agent_pos)
            self.treasures_found += 1
            self.belief.initialize_uniform_prior()
            found_treasure = True

        return {
            "observation": observation,
            "target": target,
            "moved": moved,
            "found_treasure": found_treasure,
            "position": self.grid.agent_coords,
        }

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
