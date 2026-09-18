import unittest
from src.drivers.photonic_driver import PhotonicCoprocessorDriver

class TestPhase78PhotonicDriver(unittest.TestCase):
    def setUp(self):
        self.driver = PhotonicCoprocessorDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "PhotonicCoprocessorDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_optical_processing(self):
        mat = [[2.0, 4.0], [6.0, 8.0]]
        res = self.driver.process_optical_matrix(mat, 0.5)
        self.assertIn("status", res)
        self.assertEqual(res["processed_matrix"], [[1.0, 2.0], [3.0, 4.0]])

if __name__ == "__main__":
    unittest.main()

