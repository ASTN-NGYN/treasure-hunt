from __future__ import annotations

import csv
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


def plot_entropy_curve(entropy_history: list[float]):
    """Plot entropy across scan steps."""
    fig, ax = plt.subplots()
    ax.plot(range(len(entropy_history)), entropy_history, marker="o", linewidth=1.5)
    ax.set_xlabel("Scan Step")
    ax.set_ylabel("Entropy")
    ax.set_title("Entropy Over Scan Steps")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    plt.show()
    return ax


def plot_belief_heatmap(belief_grid: np.ndarray):
    """Plot a heatmap of the belief distribution."""
    fig, ax = plt.subplots()
    image = ax.imshow(belief_grid, cmap="viridis", interpolation="nearest")
    ax.set_title("Belief Distribution")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    plt.show()
    return ax


def plot_noise_results(csv_file: str):
    """Read experiment CSV, aggregate success by noise level, and plot success rate."""
    grouped_success: dict[str, list[float]] = defaultdict(list)

    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            noise_level = row.get("noise_level", "")
            if not noise_level:
                continue

            value = str(row.get("success", "")).strip().lower()
            success = 1.0 if value in {"1", "true", "yes"} else 0.0
            grouped_success[noise_level].append(success)

    noise_levels = list(grouped_success.keys())
    success_rates = [sum(values) / len(values) if values else 0.0 for values in grouped_success.values()]

    fig, ax = plt.subplots()
    ax.bar(noise_levels, success_rates, color="#4C72B0")
    ax.set_xlabel("Noise Level")
    ax.set_ylabel("Success Rate")
    ax.set_title("Success Rate by Noise Level")
    ax.set_ylim(0.0, 1.0)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    plt.show()
    return ax