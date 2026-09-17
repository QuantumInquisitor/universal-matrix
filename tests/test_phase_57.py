import unittest
from src.photonic_tensor_coprocessor import PhotonicTensorCoprocessor

class TestPhase57PhotonicCoprocessor(unittest.TestCase):
    def setUp(self):
        self.coprocessor = PhotonicTensorCoprocessor(wavelength_nm=1550.0, mesh_size=13)

    def test_optical_multiplication_success(self):
        vec = [1.0] * 13
        phases = [0.0] * 13
        res = self.coprocessor.simulate_optical_matrix_multiplication(vec, phases)
        self.assertEqual(res["status"], "OPTICAL_COMPUTATION_SUCCESS")
        self.assertEqual(len(res["transformed_vector"]), 13)
        self.assertEqual(res["transformed_vector"][0], 1.0)

    def test_optical_multiplication_dimension_mismatch(self):
        res = self.coprocessor.simulate_optical_matrix_multiplication([1.0], [0.0])
        self.assertEqual(res["status"], "DIMENSION_MISMATCH")

if __name__ == "__main__":
    unittest.main()

