import unittest
import os

class TestPhase86WebGPU(unittest.TestCase):
    def test_index_has_webgpu_compute(self):
        self.assertTrue(os.path.exists("public/index.html"))
        with open("public/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("navigator.gpu", content)
        self.assertIn("@compute", content)
        self.assertIn("dataBuffer", content)

if __name__ == "__main__":
    unittest.main()
