import unittest
from src.drivers.qpu_driver import QPUDriver

class TestPhase75QPUDriver(unittest.TestCase):
    def setUp(self):
        self.driver = QPUDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "QPUDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_quantum_circuit_execution(self):
        res = self.driver.execute_quantum_circuit(num_qubits=2, shots=1024)
        self.assertIn("status", res)
        self.assertEqual(res["num_qubits"], 2)
        self.assertIn("counts", res)

if __name__ == "__main__":
    unittest.main()

