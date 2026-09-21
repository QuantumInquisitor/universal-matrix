#!/usr/bin/env python3
"""Neutral GRB energy/time regression utility.

This script can ingest FITS event data or generate a synthetic null dataset and
fit a linear energy-arrival-time trend. It does not contain a hard-coded
Universal Matrix photon-delay target.

Any comparison with the Matrix engine must be supplied separately from a
physical unit mapping derived independently of the GRB data.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger("GRBDataAnalysis")

HAS_ASTROPY = False
HAS_FITSIO = False

try:
    from astropy.io import fits
    HAS_ASTROPY = True
except ImportError:
    fits = None

try:
    import fitsio
    HAS_FITSIO = True
except ImportError:
    fitsio = None


class GRBDataIngestor:
    def __init__(
        self,
        fits_path: str | None = None,
        synthetic_slope_s_per_gev: float = 0.0,
        random_seed: int = 42,
    ):
        self.fits_path = fits_path
        self.synthetic_slope_s_per_gev = float(synthetic_slope_s_per_gev)
        self.random_seed = int(random_seed)

    def load_data(self, num_photons: int = 5000) -> tuple[np.ndarray, np.ndarray]:
        if self.fits_path:
            path = Path(self.fits_path)
            if not path.exists():
                raise FileNotFoundError(path)
            return self._parse_fits(path)
        return self._generate_synthetic_stream(num_photons)

    def _parse_fits(self, file_path: Path) -> tuple[np.ndarray, np.ndarray]:
        energies_gev = None
        arrival_times_s = None

        if HAS_ASTROPY:
            with fits.open(file_path) as hdul:
                events_hdu = next(
                    (hdu for hdu in hdul if hdu.name.upper() == "EVENTS"),
                    hdul[1],
                )
                data = events_hdu.data
                cols = [c.name.upper() for c in events_hdu.columns]

                if "ENERGY" in cols:
                    energies_gev = np.asarray(data["ENERGY"], dtype=np.float64)
                    unit = str(events_hdu.header.get("TUNIT1", "")).upper()
                    if "MEV" in unit or np.mean(energies_gev) > 1e3:
                        energies_gev = energies_gev / 1000.0

                if "TIME" in cols:
                    arrival_times_s = np.asarray(data["TIME"], dtype=np.float64)
                    arrival_times_s = arrival_times_s - arrival_times_s[0]

        elif HAS_FITSIO:
            with fitsio.FITS(str(file_path)) as handle:
                data = handle[1].read()
            cols = [c.upper() for c in data.dtype.names]
            if "ENERGY" in cols:
                energies_gev = np.asarray(data["ENERGY"], dtype=np.float64)
                if np.mean(energies_gev) > 1e3:
                    energies_gev = energies_gev / 1000.0
            if "TIME" in cols:
                arrival_times_s = np.asarray(data["TIME"], dtype=np.float64)
                arrival_times_s = arrival_times_s - arrival_times_s[0]
        else:
            raise ImportError(
                "Install the optional astronomy dependencies astropy or fitsio"
            )

        if energies_gev is None or arrival_times_s is None:
            raise ValueError("FITS input must contain ENERGY and TIME columns")
        if len(energies_gev) != len(arrival_times_s):
            raise ValueError("ENERGY and TIME arrays must have equal length")
        return energies_gev, arrival_times_s

    def _generate_synthetic_stream(
        self,
        n_photons: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        if n_photons < 2:
            raise ValueError("n_photons must be at least 2")

        rng = np.random.default_rng(self.random_seed)
        u = rng.uniform(0.0, 1.0, n_photons)
        energies_gev = (
            1.0 ** (-1.2)
            - u * (1.0 ** (-1.2) - 150.0 ** (-1.2))
        ) ** (-1.0 / 1.2)

        noise = rng.normal(0.0, 1e-6, n_photons)
        arrival_times_s = (
            energies_gev * self.synthetic_slope_s_per_gev
            + noise
        )
        return energies_gev, arrival_times_s


def run_dispersion_analysis(
    fits_path: str | None = None,
    synthetic_slope_s_per_gev: float = 0.0,
) -> dict[str, Any]:
    ingestor = GRBDataIngestor(
        fits_path=fits_path,
        synthetic_slope_s_per_gev=synthetic_slope_s_per_gev,
    )
    energies_gev, arrival_times_s = ingestor.load_data()

    slope, intercept = np.polyfit(energies_gev, arrival_times_s, 1)
    delay_100gev_us = slope * 100.0 * 1e6

    result = {
        "data_source": fits_path if fits_path else "Synthetic Stream",
        "total_events": int(len(energies_gev)),
        "min_energy_gev": float(np.min(energies_gev)),
        "max_energy_gev": float(np.max(energies_gev)),
        "fitted_slope_s_per_gev": float(slope),
        "fitted_intercept_s": float(intercept),
        "measured_100gev_delay_us": float(delay_100gev_us),
        "synthetic_injected_slope_s_per_gev": (
            float(synthetic_slope_s_per_gev) if not fits_path else None
        ),
        "matrix_target_delay_us": None,
        "model_status": "observational_regression_no_matrix_target",
        "has_astropy": HAS_ASTROPY,
        "has_fitsio": HAS_FITSIO,
    }

    logger.info("GRB regression result: %s", result)
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--fits", default=None)
    parser.add_argument(
        "--synthetic-slope-s-per-gev",
        type=float,
        default=0.0,
        help="Optional synthetic test injection. Not a physical prediction.",
    )
    args = parser.parse_args()
    run_dispersion_analysis(
        fits_path=args.fits,
        synthetic_slope_s_per_gev=args.synthetic_slope_s_per_gev,
    )
