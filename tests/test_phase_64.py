import os
import unittest


class TestPhase64GitHubActions(unittest.TestCase):
    WORKFLOW = ".github/workflows/verification.yml"

    def test_workflow_file_exists(self):
        self.assertTrue(os.path.exists(self.WORKFLOW))

    def test_workflow_contents(self):
        with open(self.WORKFLOW, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("Universal Matrix Verification", content)
        self.assertIn("actions/checkout@v7", content)
        self.assertIn("astral-sh/setup-uv@v10.1.0", content)
        self.assertIn("uv run pytest", content)
        self.assertIn("tests/test_canonical_kernel.py", content)


if __name__ == "__main__":
    unittest.main()
