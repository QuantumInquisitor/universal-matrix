import unittest

from scripts.analyze_grb_data import GRBDataIngestor, run_dispersion_analysis


class TestFITSIngestion(unittest.TestCase):
    def test_synthetic_null_pipeline(self):
        results = run_dispersion_analysis(fits_path=None)
        self.assertEqual(results["data_source"], "Synthetic Stream")
        self.assertGreater(results["total_events"], 100)
        self.assertIsNone(results["matrix_target_delay_us"])
        self.assertEqual(
            results["model_status"],
            "observational_regression_no_matrix_target",
        )
        # Null synthetic data should fit near zero, within statistical noise.
        self.assertLess(abs(results["measured_100gev_delay_us"]), 5.0)

    def test_known_synthetic_slope_is_recovered(self):
        injected = 2.5e-8
        results = run_dispersion_analysis(
            fits_path=None,
            synthetic_slope_s_per_gev=injected,
        )
        self.assertAlmostEqual(
            results["fitted_slope_s_per_gev"],
            injected,
            delta=2e-9,
        )

    def test_ingestor_initialization(self):
        ingestor = GRBDataIngestor()
        energies, times = ingestor.load_data(num_photons=500)
        self.assertEqual(len(energies), 500)
        self.assertEqual(len(times), 500)


if __name__ == "__main__":
    unittest.main()
