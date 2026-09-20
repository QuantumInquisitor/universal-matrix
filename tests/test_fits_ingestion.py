#!/usr/bin/env python3
"""
tests/test_fits_ingestion.py
=============================
Unit tests for NASA FITS data parser and GRB dispersion pipeline.
"""

import os
import sys
import unittest

# Ensure repository root is in sys.path before importing scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.analyze_grb_data import run_dispersion_analysis, GRBDataIngestor


class TestFITSIngestion(unittest.TestCase):

    def test_synthetic_fallback_pipeline(self):
        results = run_dispersion_analysis(fits_path=None)
        self.assertEqual(results["data_source"], "Synthetic Stream")
        self.assertGreater(results["total_events"], 100)
        self.assertAlmostEqual(results["measured_100gev_delay_us"], 15.8336, delta=1.5)

    def test_ingestor_initialization(self):
        ingestor = GRBDataIngestor()
        energies, times = ingestor.load_data(num_photons=500)
        self.assertEqual(len(energies), 500)
        self.assertEqual(len(times), 500)


if __name__ == "__main__":
    unittest.main()
    