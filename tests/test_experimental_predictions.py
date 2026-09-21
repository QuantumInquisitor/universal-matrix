import math
import unittest

from src.gauge_dispersion import (
    long_wavelength_speed,
    routing_wave_number,
    weak_field_angular_frequency,
)


class TestExperimentalPredictions(unittest.TestCase):
    def test_current_dimensionless_lattice_dispersion(self):
        beta = 1.0
        mode = 1
        q = routing_wave_number(mode)
        omega = weak_field_angular_frequency(mode, beta=beta)
        expected = 2.0 * math.sqrt(beta) * abs(math.sin(q / 2.0))
        self.assertAlmostEqual(omega, expected, places=14)

    def test_long_wavelength_speed_is_lattice_quantity(self):
        beta = 2.25
        self.assertEqual(long_wavelength_speed(beta), 1.5)

    def test_continuum_second_difference_convergence(self):
        dx = 1e-5
        x = 1.0
        step = 21 * dx

        def f(z):
            return z**3

        discrete_d2 = (
            f(x + step) - 2 * f(x) + f(x - step)
        ) / (step**2)
        self.assertAlmostEqual(discrete_d2, 6.0 * x, places=4)


if __name__ == "__main__":
    unittest.main()
