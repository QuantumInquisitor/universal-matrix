#!/usr/bin/env python3
r"""
scripts/plot_dispersion.py
==========================
Publication-Grade Plot Generator for Quantum Gravity Phase Dispersion Curves.

Plots photon arrival time delay (\Delta \tau) as a function of energy (GeV)
and cosmological distance (light-years) comparing the 114-node SO(13) model
against standard General Relativity (\Delta \tau = 0.0 s).
"""

import os
import sys
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Physical Constants
E_PLANCK = 1.9561e9         # Planck Energy (Joules)
LIGHT_SPEED = 299792458.0   # Speed of light (m/s)
LY_TO_METERS = 9.46073e15   # 1 Light-year in meters
GEV_TO_JOULES = 1.60218e-10 # 1 GeV in Joules
ALPHA_GEOMETRIC = 1.0 / (54.0 * (math.pi ** 2))
B_BOUNDARY = 6
N_CORE = 108


def calculate_delay_us(energy_gev: np.ndarray, distance_ly: float) -> np.ndarray:
    """Calculates theoretical phase dispersion delay in microseconds."""
    distance_meters = distance_ly * LY_TO_METERS
    energy_joules = energy_gev * GEV_TO_JOULES
    energy_ratio = energy_joules / E_PLANCK
    boundary_ratio = (B_BOUNDARY / N_CORE) ** 2
    time_of_flight = distance_meters / LIGHT_SPEED

    delay_seconds = energy_ratio * boundary_ratio * ALPHA_GEOMETRIC * time_of_flight * 10.0
    return delay_seconds * 1.0e6  # Convert to microseconds


def generate_publication_plot(output_path: str = "docs/dispersion_curve.png"):
    """Generates a high-DPI publication figure."""
    energies = np.linspace(1.0, 200.0, 500)  # 1 GeV to 200 GeV

    distances_ly = [1.0e8, 5.0e8, 1.0e9, 2.0e9]
    colors = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899']

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Plot Matrix Engine predictions for varying distances
    for dist, color in zip(distances_ly, colors):
        delays = calculate_delay_us(energies, dist)
        ax.plot(
            energies,
            delays,
            label=f"114-Node SO(13) Model (L = {dist:.1e} ly)",
            color=color,
            linewidth=2.0,
        )

    # Plot General Relativity baseline
    ax.axhline(0.0, color='#f59e0b', linestyle='--', linewidth=1.5, label="General Relativity (Δτ = 0.0 µs)")

    # Formatting
    ax.set_title("Photon Arrival Dispersion vs. Energy across Cosmological Distances", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Photon Energy E (GeV)", fontsize=10, labelpad=10)
    ax.set_ylabel("Quantum Phase Delay Δτ (µs)", fontsize=10, labelpad=10)
    ax.grid(True, linestyle=':', alpha=0.3, color='#475569')
    ax.legend(loc="upper left", framealpha=0.8, facecolor='#0f172a', edgecolor='#1e293b', fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"[*] High-resolution figure successfully exported to: {output_path}")


if __name__ == "__main__":
    generate_publication_plot()
    