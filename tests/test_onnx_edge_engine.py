import unittest
from src.onnx_edge_drift_engine import ONNXEdgeDriftEngine, EdgeInferenceInput

class TestONNXEdgeDriftEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ONNXEdgeDriftEngine()

    def test_edge_inference_quantized(self):
        payload = EdgeInferenceInput(
            clock_drift_vector=[0.1, 0.2, 0.3],
            magnetic_delta_vector=[0.01, 0.02, 0.03],
            quantized_int8_mode=True
        )
        res = self.engine.predict_edge_decoherence(payload)
        self.assertEqual(res["status"], "ONNX_INFERENCE_COMPLETE")
        self.assertTrue(res["quantized_int8_mode"])
        self.assertGreaterEqual(res["decoherence_risk_score"], 0.0)
        self.assertLessEqual(res["decoherence_risk_score"], 1.0)
        self.assertGreater(res["predicted_time_to_collapse_us"], 0)

if __name__ == '__main__':
    unittest.main()
