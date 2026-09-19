import unittest
from src.core.quantum_hybrid import QuantumClassicalEngine

class TestQuantumHITLRemedy(unittest.TestCase):
    def setUp(self):
        self.engine = QuantumClassicalEngine()

    def test_quantum_hybrid_vqe_execution(self):
        quantum_params = [0.785, 1.570]
        classical_matrix = [[1.0, 0.0], [0.0, 1.0]]
        
        # Pass both quantum parameters and classical matrix to execute_hybrid_vqe
        result = self.engine.execute_hybrid_vqe(quantum_params, classical_matrix)
        print(f"\n[Quantum Engine] Hybrid VQE Computation Result: {result}")

        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
