#!/usr/bin/env python3
"""Plot the dimensionless weak-field lattice dispersion relation.

This script visualizes the currently derived gauge-sector relation

    omega(q) = 2 * sqrt(beta) * |sin(q/2)|

for the 36-state routing cycle. It does not convert the result into photon
time-of-flight delays or claim a quantum-gravity prediction.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.gauge_dispersion import weak_field_angular_frequency
from src.gauge_dynamics import ROUTING_PERIOD


def dispersion_curve(beta: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    modes = np.arange(ROUTING_PERIOD, dtype=int)
    q = 2.0 * np.pi * modes / ROUTING_PERIOD
    omega = np.array(
        [weak_field_angular_frequency(int(m), beta=beta) for m in modes],
        dtype=float,
    )
    return q, omega


def generate_publication_plot(
    output_path: str = "docs/gauge_dispersion_curve.png",
    beta: float = 1.0,
) -> None:
    q, omega = dispersion_curve(beta)

    figure, axis = plt.subplots(figsize=(9, 5), dpi=180)
    axis.plot(q, omega, marker="o", markersize=3, linewidth=1.5)
    axis.set_title("Universal Matrix experimental U(1) lattice dispersion")
    axis.set_xlabel("Dimensionless routing wave number q")
    axis.set_ylabel("Dimensionless angular frequency omega")
    axis.grid(True, alpha=0.3)
    axis.text(
        0.02,
        0.96,
        "No SI speed or photon-delay prediction is implied without an independent unit map.",
        transform=axis.transAxes,
        va="top",
        fontsize=8,
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument(
        "--output",
        default="docs/gauge_dispersion_curve.png",
    )
    args = parser.parse_args()
    generate_publication_plot(args.output, args.beta)
