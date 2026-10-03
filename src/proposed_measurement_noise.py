"""Saved finite Fourier measurement disturbances, not a white-noise SDE."""

import math

import numpy as np

FREQUENCIES_RAD_S = (0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 13.0)


def seeded_coefficients(seed):
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    return np.random.Generator(np.random.PCG64(int(seed))).normal(size=(4, 8, 2))


class FourierMeasurementNoise:
    """Four independent channels; coefficient last axis is cosine,sine.

    Coefficients are fixed for all evaluation times, including negative history.
    RNG is used only by the separate constructor helper, never at evaluation.
    """

    def __init__(self, coefficients, position_sigma_m, velocity_sigma_m_s):
        scales = (position_sigma_m, velocity_sigma_m_s)
        if any(isinstance(x, (bool, np.bool_)) or np.iscomplexobj(x) for x in scales):
            raise ValueError("noise sigmas must be finite nonnegative real scalars")
        if not all(np.ndim(x) == 0 and math.isfinite(float(x)) and float(x) >= 0 for x in scales):
            raise ValueError("noise sigmas must be finite nonnegative real scalars")
        if coefficients is None:
            if any(float(x) != 0 for x in scales):
                raise ValueError("nonzero noise requires explicit saved coefficients")
            coefficients = np.zeros((4, 8, 2))
        if np.iscomplexobj(coefficients):
            raise ValueError("coefficients must be finite real 4x8x2")
        array = np.array(coefficients, dtype=float, copy=True)
        if array.shape != (4, 8, 2) or not np.isfinite(array).all():
            raise ValueError("coefficients must be finite real 4x8x2")
        array.setflags(write=False)
        self.coefficients = array
        self.sigmas = np.array([float(scales[0])] * 2 + [float(scales[1])] * 2)
        self.enabled = bool(np.any(self.sigmas != 0))

    def __call__(self, time_s):
        phase = np.array(FREQUENCIES_RAD_S) * time_s
        return (
            self.sigmas
            / math.sqrt(8)
            * (
                self.coefficients[:, :, 0] @ np.cos(phase)
                + self.coefficients[:, :, 1] @ np.sin(phase)
            )
        )

    def metadata(self):
        return {
            "frequencies_rad_s": list(FREQUENCIES_RAD_S),
            "coefficients_cos_sin": self.coefficients.tolist(),
            "channel_sigmas": self.sigmas.tolist(),
            "channel_units": ["m", "m", "m/s", "m/s"],
            "coefficient_distribution": "Independent standard Gaussian before fixing realization",
            "scope": "Smooth finite spectral ensemble; not white noise, quantum bath or measured sensor spectrum",
        }
