import unittest
from src.core.quantum_hybrid import QuantumClassicalEngine

class TestPhase89Quantum(unittest.TestCase):
    def setUp(self):
        self.engine = QuantumClassicalEngine()

    def test_vqe_hybrid_execution(self):
        res = self.engine.execute_hybrid_vqe([1.57, 0.0], [[1.0, 2.0], [3.0, 4.0]])
        self.assertEqual(res["status"], "HYBRID_EXECUTION_COMPLETE")
        self.assertIn("quantum_expectation", res)
        self.assertEqual(res["hybrid_tensor_shape"], [2, 2])

if __name__ == "__main__":
    unittest.main()
