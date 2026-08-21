import os
import sys
import unittest

# Force python to map the src directory paths cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import calculator as mc

class TestDummyCompiler(unittest.TestCase):
    def test_compiler_load(self):
        self.assertIsNotNone(mc.MatrixFieldEngine)

if __name__ == "__main__":
    unittest.main()
