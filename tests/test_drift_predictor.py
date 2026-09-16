import unittest
from src.drift_predictor import QuantumDriftPredictor, TelemetryHistoryPayload

class TestQuantumDriftPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = QuantumDriftPredictor()

    def test_drift_prediction_low_risk(self):
        payload = TelemetryHistoryPayload(
            clock_drift_series_ns=[0.1, 0.2, 0.3, 0.4],
            magnetic_delta_series_uT=[0.01, 0.02, 0.03, 0.04]
        )
        res = self.predictor.predict_decoherence_risk(payload)
        self.assertLess(res["decoherence_risk_score"], 0.5)
        self.assertFalse(res["intervention_recommended"])

    def test_drift_prediction_high_risk(self):
        payload = TelemetryHistoryPayload(
            clock_drift_series_ns=[1.0, 5.0, 15.0, 45.0],
            magnetic_delta_series_uT=[0.5, 2.5, 8.0, 20.0]
        )
        res = self.predictor.predict_decoherence_risk(payload)
        self.assertGreaterEqual(res["decoherence_risk_score"], 0.65)
        self.assertTrue(res["intervention_recommended"])

if __name__ == '__main__':
    unittest.main()
