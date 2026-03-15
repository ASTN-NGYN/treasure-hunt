from __future__ import annotations

from typing import Tuple

import numpy as np

from config import ENTROPY_EPS

Coord = Tuple[int, int]


class SensorModel:
    """Binary sensor model with false positive and false negative rates."""

    def __init__(self, false_positive: float, false_negative: float):
        self.false_positive = false_positive
        self.false_negative = false_negative

    def prob_observation(self, observed_present: bool, actual_present: bool) -> float:
        """Return P(observation | actual presence)."""
        if actual_present:
            return 1 - self.false_negative if observed_present else self.false_negative
        return self.false_positive if observed_present else 1 - self.false_positive


class BayesianBelief:
    """Belief grid over possible treasure locations."""

    def __init__(self, grid, scan_radius: int, sensor_model: SensorModel):
        self.grid = grid
        self.scan_radius = scan_radius
        self.sensor_model = sensor_model
        self.belief = np.zeros((self.grid.grid_size, self.grid.grid_size), dtype=float)
        self.initialize_uniform_prior()

    def initialize_uniform_prior(self) -> None:
        """Initialize a uniform prior over all valid treasure cells."""
        self.belief.fill(0.0)
        valid_cells = self.grid.valid_cells()

        if not valid_cells:
            return

        prior = 1.0 / len(valid_cells)
        for row, col in valid_cells:
            self.belief[row, col] = prior

    def simulate_observation(self, scan_center: Coord) -> bool:
        """Simulate a noisy sensor reading for a scan centered at the given cell."""
        actual_present = any(
            self.grid.is_treasure(cell)
            for cell in self.grid.get_cells_in_radius(scan_center, self.scan_radius)
        )
        present_probability = self.sensor_model.prob_observation(True, actual_present)
        return bool(np.random.random() < present_probability)

    def update(self, scan_center: Coord, observation: bool) -> None:
        """Apply a Bayesian update for the given observation at the scan center."""
        scan_cells = set(self.grid.get_cells_in_radius(scan_center, self.scan_radius))
        posterior = np.zeros_like(self.belief)

        for row, col in self.grid.valid_cells():
            actual_present = (row, col) in scan_cells
            likelihood = self.sensor_model.prob_observation(observation, actual_present)
            posterior[row, col] = likelihood * self.belief[row, col]

        self.belief = posterior
        self.normalize()

    def normalize(self) -> None:
        """Normalize the belief grid so its total probability mass is one."""
        total = float(self.belief.sum())
        if total <= 0.0:
            self.initialize_uniform_prior()
            return

        self.belief /= total

    def compute_entropy(self) -> float:
        """Compute Shannon entropy of the current belief distribution."""
        probabilities = self.belief[self.belief > 0.0]
        if probabilities.size == 0:
            return 0.0

        return float(-np.sum(probabilities * np.log(probabilities + ENTROPY_EPS)))

    def argmax_cell(self) -> Coord:
        """Return the cell with the highest belief value."""
        row, col = np.unravel_index(np.argmax(self.belief), self.belief.shape)
        return int(row), int(col)

    def get_belief(self) -> np.ndarray:
        """Return the current belief grid."""
        return self.belief