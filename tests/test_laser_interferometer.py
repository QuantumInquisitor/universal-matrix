import unittest
from src.laser_interferometer import OpticalFieldInterferometer, InterferometerTelemetry

class TestOpticalFieldInterferometer(unittest.TestCase):
    def setUp(self):
        self.interferometer = OpticalFieldInterferometer()

    def test_interferometric_displacement_calculation(self):
        payload = InterferometerTelemetry(
            wavelength_nm=632.8,
            fringe_shift_count=0.5,  # Half fringe = ~158.2 nm displacement
            phase_difference_rad=3.14159,
            ambient_temp_c=22.0
        )
        res = self.interferometer.process_interferometry(payload)
        self.assertAlmostEqual(res["displacement_nanometers"], 158.2, places=1)
        self.assertGreater(res["so13_phase_compensation_rad"], 0.0)
        self.assertFalse(res["chassis_stable"])

if __name__ == '__main__':
    unittest.main()
