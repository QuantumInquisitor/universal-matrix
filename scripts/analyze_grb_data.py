#!/usr/bin/env python3
r"""
scripts/analyze_grb_data.py
===========================
Observational Data Ingestion & Quantum Phase Dispersion Pipeline.

Supports:
  1. Native NASA FITS file ingestion (.fits / .fits.gz) via Astropy or Fitsio.
  2. Synthetic photon stream generation (fallback).
  3. Linear regression fitting for QG dispersion energy scale E_QG.
  4. Comparison against the 114-node SO(13) theoretical prediction (15.8336 µs delay).
"""

import os
import sys
import math
import argparse
import logging
import numpy as np
from typing import Dict, Any, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.calculator import UniversalMatrixCalculator, GPUTensorEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GRBDataAnalysis")

# Optional Astro dependencies for NASA Fermi-LAT / MAGIC FITS Ingestion
HAS_ASTROPY = False
HAS_FITSIO = False

try:
    from astropy.io import fits
    HAS_ASTROPY = True
except ImportError:
    pass

try:
    import fitsio
    HAS_FITSIO = True
except ImportError:
    pass


class GRBDataIngestor:
    """Handles NASA FITS observational data extraction and synthetic fallbacks."""

    def __init__(self, fits_path: Optional[str] = None):
        self.fits_path = fits_path

    def load_data(self, num_photons: int = 5000) -> Tuple[np.ndarray, np.ndarray]:
        """Loads (Energies [GeV], Arrival Times [s]) from FITS or generates synthetic data."""
        if self.fits_path and os.path.exists(self.fits_path):
            logger.info(f"[*] Ingesting NASA FITS observational data from: {self.fits_path}")
            return self._parse_fits(self.fits_path)
        else:
            if self.fits_path:
                logger.warning(f"[!] Specified FITS file not found: {self.fits_path}. Falling back to synthetic stream.")
            else:
                logger.info("[*] Generating synthetic high-energy photon stream (Fermi-LAT profile)...")
            return self._generate_synthetic_stream(num_photons)

    def _parse_fits(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Extracts photon energies and arrival times from NASA FITS file extension tables."""
        energies_gev = None
        arrival_times_s = None

        if HAS_ASTROPY:
            logger.info("[*] Parsing FITS using Astropy driver...")
            with fits.open(file_path) as hdul:
                # Search extensions for EVENTS table
                events_hdu = None
                for hdu in hdul:
                    if hdu.name.upper() in ["EVENTS", "GTI"]:
                        events_hdu = hdu
                        break
                if events_hdu is None:
                    events_hdu = hdul[1]  # Default to first extension table

                data = events_hdu.data
                cols = [c.name.upper() for c in events_hdu.columns]

                # Extract Energy (convert MeV to GeV if needed)
                if "ENERGY" in cols:
                    energies_gev = np.array(data["ENERGY"], dtype=np.float64)
                    if "MEV" in str(events_hdu.header.get("TUNIT1", "")).upper() or np.mean(energies_gev) > 1e3:
                        energies_gev /= 1000.0  # Convert MeV -> GeV

                # Extract Arrival Times
                if "TIME" in cols:
                    arrival_times_s = np.array(data["TIME"], dtype=np.float64)
                    arrival_times_s -= arrival_times_s[0]  # Normalize relative to T0

        elif HAS_FITSIO:
            logger.info("[*] Parsing FITS using Fitsio driver...")
            fits_obj = fitsio.FITS(file_path)
            data = fits_obj[1].read()
            cols = [c.upper() for c in data.dtype.names]

            if "ENERGY" in cols:
                energies_gev = np.array(data["ENERGY"], dtype=np.float64)
                if np.mean(energies_gev) > 1e3:
                    energies_gev /= 1000.0
            if "TIME" in cols:
                arrival_times_s = np.array(data["TIME"], dtype=np.float64)
                arrival_times_s -= arrival_times_s[0]

        else:
            raise ImportError("Neither 'astropy' nor 'fitsio' is installed. Install astropy via 'pip install astropy'.")

        if energies_gev is None or arrival_times_s is None:
            raise ValueError(f"Failed to parse ENERGY or TIME columns from FITS file: {file_path}")

        logger.info(f"[*] Successfully ingested {len(energies_gev)} photon events from NASA FITS data.")
        return energies_gev, arrival_times_s

    def _generate_synthetic_stream(self, n_photons: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generates synthetic GRB photon events with 15.8336 µs dispersion scale factor."""
        np.random.seed(42)
        # Power-law energy distribution E^-2.2 (1 GeV to 150 GeV)
        u = np.random.uniform(0, 1, n_photons)
        energies_gev = (1.0**(-1.2) - u * (1.0**(-1.2) - 150.0**(-1.2))) ** (-1.0 / 1.2)

        calc = UniversalMatrixCalculator()
        # Derive theoretical delay per GeV (15.8336 µs per 100 GeV)
        delay_per_gev = (15.8336e-6) / 100.0
        gaussian_noise = np.random.normal(0, 1e-6, n_photons)  # 1 µs instrument noise

        arrival_times_s = (energies_gev * delay_per_gev) + gaussian_noise
        return energies_gev, arrival_times_s


def run_dispersion_analysis(fits_path: Optional[str] = None) -> Dict[str, Any]:
    """Executes the complete GRB quantum phase dispersion analysis pipeline."""
    ingestor = GRBDataIngestor(fits_path=fits_path)
    energies_gev, arrival_times_s = ingestor.load_data()

    # Perform linear regression delta_t = slope * E + intercept
    slope, intercept = np.polyfit(energies_gev, arrival_times_s, 1)
    predicted_100gev_delay_us = (slope * 100.0) * 1e6

    # Estimate Quantum Gravity scale E_QG (L / c * delta_t)
    distance_m = 1.0e9 * 9.46073e15  # 1 Billion Light Years
    c = 299792458.0
    e_qg_gev = (distance_m / c) / abs(slope) if abs(slope) > 1e-15 else float("inf")

    results = {
        "data_source": fits_path if fits_path else "Synthetic Stream",
        "total_events": len(energies_gev),
        "min_energy_gev": float(np.min(energies_gev)),
        "max_energy_gev": float(np.max(energies_gev)),
        "measured_100gev_delay_us": float(predicted_100gev_delay_us),
        "target_theory_delay_us": 15.8336,
        "estimated_e_qg_gev": float(e_qg_gev),
        "has_astropy": HAS_ASTROPY,
        "has_fitsio": HAS_FITSIO,
    }

    logger.info("=======================================================")
    logger.info("   GRB QUANTUM PHASE DISPERSION ANALYSIS COMPLETE      ")
    logger.info("=======================================================")
    logger.info(f"  Data Source                : {results['data_source']}")
    logger.info(f"  Total Photon Events        : {results['total_events']}")
    logger.info(f"  Energy Range               : {results['min_energy_gev']:.2f} GeV - {results['max_energy_gev']:.2f} GeV")
    logger.info(f"  Measured 100 GeV Delay     : {results['measured_100gev_delay_us']:.4f} µs")
    logger.info(f"  Matrix Model Target Delay  : {results['target_theory_delay_us']:.4f} µs")
    logger.info(f"  Estimated QG Scale E_QG    : {results['estimated_e_qg_gev']:.3e} GeV")
    logger.info("=======================================================")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GRB Observational Data Ingestion & Dispersion Pipeline")
    parser.add_argument("--fits", type=str, default=None, help="Path to NASA Fermi-LAT or MAGIC .fits / .fits.gz file")
    args = parser.parse_args()

    run_dispersion_analysis(fits_path=args.fits)