#!/usr/bin/env python3
r"""
scripts/analyze_grb_data.py
===========================
Observational Data Analysis Pipeline for Gamma-Ray Burst (GRB) Events.

Evaluates high-energy photon arrival time dispersion against the 114-node
SO(13) discrete quantum gravity prediction (\Delta \tau = 15.8336 µs for 100 GeV
photons over 10^9 light-years) versus standard General Relativity (\Delta \tau = 0.0 s).
"""

import os
import sys
import json
import math
import argparse
from typing import Dict, List, Tuple, Optional

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import constants directly from src.calculator
import src.calculator as calc

# Physical & Cosmological Constants
E_PLANCK = getattr(calc, "E_PLANCK", getattr(calc, "PLANCK_ENERGY", 1.9561e9))  # Joules
LIGHT_SPEED = getattr(calc, "LIGHT_SPEED", getattr(calc, "SPEED_OF_LIGHT", 299792458.0))
ALPHA_GEOMETRIC = getattr(calc, "ALPHA_GEOMETRIC", 1.0 / (54.0 * (math.pi ** 2)))
N_CORE = getattr(calc, "N_CORE", 108)
B_BOUNDARY = getattr(calc, "B_BOUNDARY", 6)

LY_TO_METERS = 9.4607304725808e15  # 1 light-year in meters
GEV_TO_JOULES = 1.602176634e-10    # 1 GeV in Joules


class GRBDataAnalyzer:
    """
    Parses GRB photon event streams and evaluates observed energy-dependent time delays
    against the 114-node discrete lattice dispersion formula.
    """

    def __init__(self, distance_ly: float = 1.0e9):
        """
        :param distance_ly: Luminosity/comoving distance to GRB source in light-years.
        """
        self.distance_ly = distance_ly
        self.distance_meters = distance_ly * LY_TO_METERS

    def calculate_predicted_delay(self, energy_gev: float) -> float:
        r"""
        Calculates predicted time-of-flight phase dispersion delay (in seconds)
        for a photon of energy E (GeV) crossing distance L (meters).

        Formula:
          \Delta \tau = (E / E_Planck) * (B_boundary / N_core)^2 * \alpha_geometric * (L / c) * 10.0
        """
        energy_joules = energy_gev * GEV_TO_JOULES
        energy_ratio = energy_joules / E_PLANCK
        boundary_ratio = (B_BOUNDARY / N_CORE) ** 2
        time_of_flight = self.distance_meters / LIGHT_SPEED

        delay_seconds = (
            energy_ratio * boundary_ratio * ALPHA_GEOMETRIC * time_of_flight * 10.0
        )
        return delay_seconds

    def generate_synthetic_grb_data(
        self, num_photons: int = 500, inject_signal: bool = True
    ) -> List[Dict[str, float]]:
        """
        Generates benchmark GRB photon event stream for pipeline verification.
        """
        import random

        events = []
        base_time = 1000.0  # Burst onset time in seconds

        for i in range(num_photons):
            # Power-law energy distribution E^-2.0 between 1 GeV and 150 GeV
            u = random.random()
            energy_gev = 1.0 / (1.0 - u * (1.0 - 1.0 / 150.0))

            # Expected delay from SO(13) discrete lattice
            true_delay = self.calculate_predicted_delay(energy_gev) if inject_signal else 0.0

            # Add observational detector timing jitter (~1 µs Gaussian noise)
            noise = random.gauss(0.0, 1.0e-6)
            arrival_time = base_time + true_delay + noise

            events.append(
                {
                    "event_id": i + 1,
                    "energy_gev": round(energy_gev, 4),
                    "arrival_time_s": arrival_time,
                    "predicted_delay_us": true_delay * 1.0e6,
                }
            )

        return sorted(events, key=lambda x: x["energy_gev"])

    def process_dataset(
        self, events: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Evaluates event stream against GR (\Delta \tau = 0) vs Universal Matrix prediction.
        """
        if not events:
            raise ValueError("Event dataset is empty.")

        # Reference low-energy anchor (lowest energy photon assumed near-zero delay)
        anchor_event = min(events, key=lambda x: x["energy_gev"])
        anchor_energy = anchor_event["energy_gev"]
        anchor_time = anchor_event["arrival_time_s"]

        residuals_gr = []
        residuals_matrix = []

        for ev in events:
            if ev["event_id"] == anchor_event["event_id"]:
                continue

            delta_e = ev["energy_gev"] - anchor_energy
            measured_dt = ev["arrival_time_s"] - anchor_time

            # Theoretical delay difference relative to anchor
            expected_dt = self.calculate_predicted_delay(ev["energy_gev"]) - self.calculate_predicted_delay(anchor_energy)

            # Residuals
            residuals_gr.append(measured_dt ** 2)
            residuals_matrix.append((measured_dt - expected_dt) ** 2)

        mse_gr = sum(residuals_gr) / len(residuals_gr)
        mse_matrix = sum(residuals_matrix) / len(residuals_matrix)

        # High-energy 100 GeV benchmark prediction
        delay_100gev_us = self.calculate_predicted_delay(100.0) * 1.0e6

        return {
            "total_events": len(events),
            "distance_ly": self.distance_ly,
            "predicted_100gev_delay_us": delay_100gev_us,
            "mse_general_relativity": mse_gr,
            "mse_universal_matrix": mse_matrix,
            "matrix_favored": mse_matrix < mse_gr,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze GRB Astronomical Event Data against 114-Node SO(13) Quantum Gravity Predictions."
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to JSON event stream file. If omitted, synthetic benchmark data is generated.",
    )
    parser.add_argument(
        "--distance-ly",
        type=float,
        default=1.0e9,
        help="Comoving distance to GRB source in light-years (default: 1e9).",
    )
    parser.add_argument(
        "--inject-null",
        action="store_true",
        help="Inject null GR hypothesis (zero delay) to test falsification resilience.",
    )

    args = parser.parse_args()

    analyzer = GRBDataAnalyzer(distance_ly=args.distance_ly)

    if args.input and os.path.exists(args.input):
        print(f"[*] Loading observational GRB dataset from: {args.input}")
        with open(args.input, "r", encoding="utf-8") as f:
            events = json.load(f)
    else:
        print("[*] Generating synthetic high-energy GRB photon event stream...")
        inject_signal = not args.inject_null
        events = analyzer.generate_synthetic_grb_data(
            num_photons=1000, inject_signal=inject_signal
        )

    results = analyzer.process_dataset(events)

    print("\n=======================================================")
    print("      GRB OBSERVATIONAL DATA ANALYSIS REPORT           ")
    print("=======================================================")
    print(f" Total Photons Analyzed       : {results['total_events']}")
    print(f" Source Distance              : {results['distance_ly']:.2e} light-years")
    print(f" Predicted 100 GeV Phase Delay: {results['predicted_100gev_delay_us']:.4f} µs")
    print("-------------------------------------------------------")
    print(f" Mean Squared Error (GR)     : {results['mse_general_relativity']:.6e}")
    print(f" Mean Squared Error (Matrix) : {results['mse_universal_matrix']:.6e}")
    print("-------------------------------------------------------")
    if results["matrix_favored"]:
        print(" VERDICT: DATA FAVORS 114-NODE SO(13) DISPERSION MODEL")
    else:
        print(" VERDICT: DATA FAVORS STANDARD GENERAL RELATIVITY (NULL)")
    print("=======================================================\n")


if __name__ == "__main__":
    main()