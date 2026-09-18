import unittest
import os

class TestPhase66EVMDeployment(unittest.TestCase):
    def test_hardhat_config_exists(self):
        self.assertTrue(os.path.exists("hardhat.config.js"))

    def test_deploy_script_exists(self):
        self.assertTrue(os.path.exists("scripts/deploy_licensing.js"))

    def test_deploy_script_contents(self):
        with open("scripts/deploy_licensing.js", "r") as f:
            content = f.read()
        self.assertIn("UniversalMatrixLicensing", content)
        self.assertIn("waitForDeployment", content)

if __name__ == "__main__":
    unittest.main()

