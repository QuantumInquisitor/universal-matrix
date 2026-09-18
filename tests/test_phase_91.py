import unittest
from src.core.photonic_engine import PhotonicTensorEngine

class TestPhase91Photonic(unittest.TestCase):
    def setUp(self):
        self.engine = PhotonicTensorEngine()

    def test_optical_transform(self):
        res = self.engine.execute_optical_transform([[1.0, 0.0], [0.0, 1.0]], 0.785)
        self.assertEqual(res["status"], "PHOTONIC_COMPUTE_COMPLETE")
        self.assertIn("result_matrix", res)
        self.assertEqual(len(res["result_matrix"]), 2)

if __name__ == "__main__":
    unittest.main()
