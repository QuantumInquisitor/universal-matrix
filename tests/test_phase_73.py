import unittest
from src.drivers.evm_driver import EVMDriver

class TestPhase73EVMDriver(unittest.TestCase):
    def setUp(self):
        self.driver = EVMDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "EVMDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_chain_state_query(self):
        res = self.driver.query_chain_state()
        self.assertIn("status", res)
        self.assertIn("latest_block", res)

if __name__ == "__main__":
    unittest.main()

