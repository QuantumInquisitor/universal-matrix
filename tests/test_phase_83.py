import unittest
from src.core.native_matrix import NativeMatrixEngine

class TestPhase83NativeMatrix(unittest.TestCase):
    def setUp(self):
        self.engine = NativeMatrixEngine()

    def test_matrix_processing(self):
        input_mat = [[1.0, 2.0], [3.0, 4.0]]
        res = self.engine.process_high_dim_matrix(input_mat)
        self.assertIn("execution_engine", res)
        self.assertIn("result_matrix", res)

if __name__ == "__main__":
    unittest.main()

