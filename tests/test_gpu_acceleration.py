import unittest
from src.gpu_batch_accelerator import GPUBatchAccelerator

class TestGPUBatchAccelerator(unittest.TestCase):
    def setUp(self):
        self.accelerator = GPUBatchAccelerator(prefer_gpu=False)

    def test_batch_rotation_shape(self):
        sample_batch = [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.7071, -0.7071], [0.7071, 0.7071]]
        ]
        result = self.accelerator.execute_so13_batch_rotation(sample_batch, 0.5)
        self.assertEqual(result["batch_size"], 2)
        self.assertIn("device_used", result)
        self.assertEqual(len(result["transformed_tensors"]), 2)

if __name__ == '__main__':
    unittest.main()
