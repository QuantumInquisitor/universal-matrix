import unittest
import os

class TestPhase63DockerHelm(unittest.TestCase):
    def test_dockerfile_exists(self):
        self.assertTrue(os.path.exists("Dockerfile"))

    def test_helm_chart_exists(self):
        self.assertTrue(os.path.exists("charts/universal-matrix/Chart.yaml"))
        self.assertTrue(os.path.exists("charts/universal-matrix/values.yaml"))
        self.assertTrue(os.path.exists("charts/universal-matrix/templates/deployment.yaml"))
        self.assertTrue(os.path.exists("charts/universal-matrix/templates/service.yaml"))

if __name__ == "__main__":
    unittest.main()

