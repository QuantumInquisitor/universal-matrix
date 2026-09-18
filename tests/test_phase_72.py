import unittest
from src.drivers.cuda_driver import CUDADriver

class TestPhase72CUDADriver(unittest.TestCase):
    def setUp(self):
        self.driver = CUDADriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "CUDADriver")
        self.assertIn(status["active_mode"], ["MOCK", "CPU_FALLBACK", "REAL"])

    def test_tensor_transformation(self):
        res = self.driver.execute_tensor_transform([1.0, 2.0, 3.0], 3.0)
        self.assertIn("status", res)
        self.assertEqual(res["transformed_tensor"], [3.0, 6.0, 9.0])

if __name__ == "__main__":
    unittest.main()

