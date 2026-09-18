import unittest
import os

class TestPhase64GitHubActions(unittest.TestCase):
    def test_workflow_file_exists(self):
        self.assertTrue(os.path.exists(".github/workflows/ci-cd.yml"))

    def test_workflow_contents(self):
        with open(".github/workflows/ci-cd.yml", "r") as f:
            content = f.read()
        self.assertIn("Universal Matrix CI/CD Pipeline", content)
        self.assertIn("unittest discover", content)
        self.assertIn("docker/build-push-action", content)
        self.assertIn("helm lint", content)

if __name__ == "__main__":
    unittest.main()

