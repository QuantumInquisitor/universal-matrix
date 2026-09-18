import unittest
from src.cuda_accelerator import CUDAFieldAccelerator

class TestPhase68CUDAAccelerator(unittest.TestCase):
    def setUp(self):
        self.accelerator = CUDAFieldAccelerator(device_id=0)

    def test_cuda_initialization(self):
        self.assertTrue(self.accelerator.is_cuda_available)

    def test_matrix_transform(self):
        tensor = [1.0, 2.0, 3.0]
        res = self.accelerator.execute_matrix_transform(tensor, scale_factor=2.0)
        self.assertEqual(res["status"], "CUDA_EXECUTION_SUCCESS")
        self.assertEqual(res["transformed_tensor"], [2.0, 4.0, 6.0])
        self.assertEqual(res["tensor_size"], 3)

if __name__ == "__main__":
    unittest.main()

