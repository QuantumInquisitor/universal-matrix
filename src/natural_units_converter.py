import math

# Universal Physical Constants (SI)
SPEED_OF_LIGHT = 299792458.0  # m/s
REDUCED_PLANCK = 1.054571817e-34  # J*s
ELEMENTARY_CHARGE = 1.602176634e-19  # C
ELECTRON_MASS = 9.1093837015e-31  # kg

class NaturalUnitsConverter:
    def __init__(self, node_count: int = 114):
        self.node_count = node_count
        self.so13_scale_factor = 1.0 / (54.0 * (math.pi ** 2))

    def si_to_natural_energy(self, energy_joules: float) -> dict:
        ev = energy_joules / ELEMENTARY_CHARGE
        planck_energy_j = math.sqrt((REDUCED_PLANCK * (SPEED_OF_LIGHT ** 5)) / 6.67430e-11)
        planck_units = energy_joules / planck_energy_j
        matrix_units = (energy_joules * self.so13_scale_factor) / REDUCED_PLANCK

        return {
            "energy_joules": energy_joules,
            "energy_ev": ev,
            "energy_planck": planck_units,
            "energy_matrix_units": matrix_units,
            "so13_scale_factor": self.so13_scale_factor
        }

    def frequency_to_wavelength_natural(self, frequency_hz: float) -> dict:
        wavelength_m = SPEED_OF_LIGHT / frequency_hz if frequency_hz > 0 else 0.0
        lattice_spacing_m = wavelength_m / self.node_count

        return {
            "frequency_hz": frequency_hz,
            "wavelength_m": wavelength_m,
            "lattice_node_spacing_m": lattice_spacing_m,
            "nodes": self.node_count
        }