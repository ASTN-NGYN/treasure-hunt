from __future__ import annotations

import csv
from typing import Dict, Iterable, List

import numpy as np

from bayesian_agent import BayesianAgent
from config import NOISE_PRESETS
from grid import Grid

ResultValue = float | int | bool | str


class ExperimentRunner:
    """Run repeated Bayesian treasure-hunt episodes and aggregate metrics."""

    def __init__(
        self,
        grid_size: int,
        scan_radius: int,
        false_positive: float,
        false_negative: float,
        seeds: Iterable[int],
    ):
        self.grid_size = grid_size
        self.scan_radius = scan_radius
        self.false_positive = false_positive
        self.false_negative = false_negative
        self.seeds = list(seeds)
        self.step_limit = self.grid_size * self.grid_size * 10
        self.episode_results: List[Dict[str, ResultValue]] = []
        self.noise_results: Dict[str, Dict[str, float]] = {}
        self.noise_episode_results: List[Dict[str, ResultValue]] = []

    def run_episode(self, seed: int) -> Dict[str, ResultValue]:
        """Run one episode and return collected metrics."""
        grid = Grid(self.grid_size)
        grid.reset_random(seed)

        agent = BayesianAgent(
            grid=grid,
            scan_radius=self.scan_radius,
            false_positive=self.false_positive,
            false_negative=self.false_negative,
        )

        total_treasures = len(grid.remaining_treasures())
        steps = 0

        while len(grid.remaining_treasures()) > 0 and steps < self.step_limit:
            agent.step()
            steps += 1

        final_entropy = agent.belief.compute_entropy()
        success = agent.treasures_found == total_treasures

        return {
            "seed": seed,
            "moves": agent.moves,
            "scans": agent.scans,
            "treasures_found": agent.treasures_found,
            "final_entropy": final_entropy,
            "success": success,
            "steps": steps,
        }

    def run_experiments(self) -> Dict[str, float]:
        """Run all configured episodes and return aggregated statistics."""
        self.episode_results = [self.run_episode(seed) for seed in self.seeds]

        if not self.episode_results:
            return {
                "avg_moves": 0.0,
                "avg_scans": 0.0,
                "avg_entropy": 0.0,
                "success_rate": 0.0,
            }

        moves = np.array([float(item["moves"]) for item in self.episode_results], dtype=float)
        scans = np.array([float(item["scans"]) for item in self.episode_results], dtype=float)
        entropy = np.array([float(item["final_entropy"]) for item in self.episode_results], dtype=float)
        success = np.array([1.0 if bool(item["success"]) else 0.0 for item in self.episode_results], dtype=float)

        return {
            "avg_moves": float(moves.mean()),
            "avg_scans": float(scans.mean()),
            "avg_entropy": float(entropy.mean()),
            "success_rate": float(success.mean()),
        }

    def print_results(self) -> None:
        """Print per-episode and aggregated experiment metrics as a table."""
        aggregated = self.run_experiments()

        headers = ["Seed", "Moves", "Scans", "Treasures", "Final Entropy", "Success"]
        row_format = "{:<8}{:<10}{:<10}{:<12}{:<16}{:<10}"

        print(row_format.format(*headers))
        print("-" * 66)

        for item in self.episode_results:
            print(
                row_format.format(
                    str(item["seed"]),
                    str(item["moves"]),
                    str(item["scans"]),
                    str(item["treasures_found"]),
                    f"{float(item['final_entropy']):.6f}",
                    "yes" if bool(item["success"]) else "no",
                )
            )

        print("\nAggregated")
        print(f"avg_moves: {aggregated['avg_moves']:.3f}")
        print(f"avg_scans: {aggregated['avg_scans']:.3f}")
        print(f"avg_entropy: {aggregated['avg_entropy']:.6f}")
        print(f"success_rate: {aggregated['success_rate']:.3f}")

    def run_noise_experiments(self) -> Dict[str, Dict[str, float]]:
        """Run experiments for each configured noise preset and aggregate metrics."""
        self.noise_results = {}
        self.noise_episode_results = []

        for noise_level, (false_positive, false_negative) in NOISE_PRESETS.items():
            runner = ExperimentRunner(
                grid_size=self.grid_size,
                scan_radius=self.scan_radius,
                false_positive=false_positive,
                false_negative=false_negative,
                seeds=self.seeds,
            )
            aggregated = runner.run_experiments()
            self.noise_results[noise_level] = aggregated

            for item in runner.episode_results:
                row = dict(item)
                row["noise_level"] = noise_level
                self.noise_episode_results.append(row)

        return self.noise_results

    def save_results_csv(self, filename: str) -> None:
        """Save per-episode results to CSV."""
        rows = self.noise_episode_results
        if not rows:
            if not self.episode_results:
                self.run_experiments()

            rows = []
            for item in self.episode_results:
                row = dict(item)
                row["noise_level"] = "custom"
                rows.append(row)

        fieldnames = [
            "noise_level",
            "seed",
            "moves",
            "scans",
            "treasures_found",
            "final_entropy",
            "success",
        ]

        with open(filename, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key) for key in fieldnames})

    def print_noise_summary(self) -> None:
        """Print aggregated metrics for each noise level as a summary table."""
        if not self.noise_results:
            self.run_noise_experiments()

        headers = ["Noise Level", "Avg Moves", "Avg Scans", "Avg Entropy", "Success Rate"]
        row_format = "{:<14}{:<12}{:<12}{:<14}{:<14}"

        print(row_format.format(*headers))
        print("-" * 66)

        for noise_level, stats in self.noise_results.items():
            print(
                row_format.format(
                    noise_level,
                    f"{stats['avg_moves']:.3f}",
                    f"{stats['avg_scans']:.3f}",
                    f"{stats['avg_entropy']:.6f}",
                    f"{stats['success_rate']:.3f}",
                )
            )
