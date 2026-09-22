"""Normal-mode analysis for the polarity-aware rotor lattice.

The exact canonical polarity bit enters the independent-phase representation as

    phi_eff = phi + pi * p.

This module asks a precise dynamical question: does that exact pi offset create
new linear collective-mode bands?

For a background that minimizes every zero-link rotor interaction, the answer
is no.  The independent base phase compensates the branch offset,

    phi_0 = phi_ref - pi * p,

so phi_eff is spatially uniform.  The Hessian is then the ordinary cubic-lattice
rotor Hessian and the spectrum is isospectral to the polarity-free model.

If the base phase is not compensated, opposite-branch links may sit at
Delta = pi.  Such links have curvature kappa*cos(pi) = -kappa and can make the
stationary background linearly unstable.  That is a background-instability
statement, not a new stable particle band.
"""

from __future__ import annotations

import math

import numpy as np

from .matrix_polarity_rotor_transition import effective_phase_field


AXES = (0, 1, 2)


def _validate_shape(shape: tuple[int, int, int]) -> tuple[int, int, int]:
    if len(shape) != 3:
        raise ValueError("shape must contain exactly three dimensions")
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 2 for v in shape):
        raise ValueError("each shape dimension must be an integer >= 2")
    return shape


def compensated_phase_for_polarity(
    polarity_bits: np.ndarray,
    reference_phase: float = 0.0,
    phase_representation: str = "independent",
) -> np.ndarray:
    """Return a zero-link equilibrium base phase for a given polarity pattern."""
    bits = np.asarray(polarity_bits)
    if bits.ndim != 3:
        raise ValueError("polarity_bits must be a three-dimensional array")
    if not np.all(np.isin(bits, (0, 1))):
        raise ValueError("polarity_bits must contain only 0 or 1")
    if not math.isfinite(reference_phase):
        raise ValueError("reference_phase must be finite")
    if phase_representation == "independent":
        phase = reference_phase - math.pi * bits.astype(float)
    elif phase_representation == "canonical_clock":
        phase = np.full(bits.shape, reference_phase, dtype=float)
    else:
        raise ValueError(
            "phase_representation must be 'independent' or 'canonical_clock'"
        )
    return (phase + np.pi) % (2.0 * np.pi) - np.pi


def analytic_cubic_omega_squared(
    wavevector: tuple[float, float, float] | np.ndarray,
    *,
    coupling: float = 1.0,
    inertia: float = 1.0,
) -> float:
    """Exact linear rotor dispersion on a unit-spacing cubic lattice."""
    k = np.asarray(wavevector, dtype=float)
    if k.shape != (3,) or not np.all(np.isfinite(k)):
        raise ValueError("wavevector must contain three finite components")
    if not math.isfinite(coupling) or coupling <= 0:
        raise ValueError("coupling must be finite and positive")
    if not math.isfinite(inertia) or inertia <= 0:
        raise ValueError("inertia must be finite and positive")
    return float(
        4.0
        * coupling
        / inertia
        * np.sum(np.sin(0.5 * k) ** 2)
    )


def periodic_wavevectors(
    shape: tuple[int, int, int],
) -> np.ndarray:
    """Return all discrete periodic wavevectors in the first FFT ordering."""
    shape = _validate_shape(shape)
    components = [
        2.0 * math.pi * np.fft.fftfreq(n)
        for n in shape
    ]
    grid = np.meshgrid(*components, indexing="ij")
    return np.stack([g.reshape(-1) for g in grid], axis=1)


def analytic_periodic_spectrum(
    shape: tuple[int, int, int],
    *,
    coupling: float = 1.0,
    inertia: float = 1.0,
) -> np.ndarray:
    """Return sorted omega^2 values for the finite periodic cubic lattice."""
    values = [
        analytic_cubic_omega_squared(
            k,
            coupling=coupling,
            inertia=inertia,
        )
        for k in periodic_wavevectors(shape)
    ]
    return np.sort(np.asarray(values, dtype=float))


def linearized_hessian_periodic(
    phase: np.ndarray,
    polarity_bits: np.ndarray,
    links: dict[str, np.ndarray] | None = None,
    *,
    coupling: float = 1.0,
    phase_representation: str = "independent",
) -> np.ndarray:
    """Return the potential Hessian around a periodic background.

    Every positive-oriented nearest-neighbor link contributes

        kappa*cos(Delta_ij) [[1, -1], [-1, 1]]

    to the two endpoint coordinates.
    """
    phase = np.asarray(phase, dtype=float)
    bits = np.asarray(polarity_bits)
    if phase.ndim != 3:
        raise ValueError("phase must be a three-dimensional array")
    shape = _validate_shape(tuple(int(v) for v in phase.shape))
    if bits.shape != shape:
        raise ValueError("polarity_bits shape mismatch")
    if not math.isfinite(coupling) or coupling <= 0:
        raise ValueError("coupling must be finite and positive")

    eff = effective_phase_field(
        phase,
        bits,
        phase_representation,
    )

    if links is None:
        links = {
            "x": np.zeros(shape, dtype=float),
            "y": np.zeros(shape, dtype=float),
            "z": np.zeros(shape, dtype=float),
        }
    for name in ("x", "y", "z"):
        if name not in links:
            raise ValueError(f"missing link field {name}")
        arr = np.asarray(links[name], dtype=float)
        if arr.shape != shape:
            raise ValueError(f"periodic link shape mismatch on axis {name}")
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"link field {name} must be finite")

    size = int(np.prod(shape))
    hessian = np.zeros((size, size), dtype=float)

    def index(coord: tuple[int, int, int]) -> int:
        return int(np.ravel_multi_index(coord, shape))

    axis_names = ("x", "y", "z")
    for coord in np.ndindex(shape):
        i = index(coord)
        for axis, name in zip(AXES, axis_names, strict=True):
            target = list(coord)
            target[axis] = (target[axis] + 1) % shape[axis]
            target_t = tuple(target)
            j = index(target_t)

            delta = (
                eff[target_t]
                - eff[coord]
                + np.asarray(links[name], dtype=float)[coord]
            )
            weight = coupling * math.cos(float(delta))

            hessian[i, i] += weight
            hessian[j, j] += weight
            hessian[i, j] -= weight
            hessian[j, i] -= weight

    return hessian


def normal_mode_omega_squared(
    phase: np.ndarray,
    polarity_bits: np.ndarray,
    links: dict[str, np.ndarray] | None = None,
    *,
    coupling: float = 1.0,
    inertia: float = 1.0,
    phase_representation: str = "independent",
) -> np.ndarray:
    """Return sorted linearized omega^2 eigenvalues, including negatives."""
    if not math.isfinite(inertia) or inertia <= 0:
        raise ValueError("inertia must be finite and positive")
    hessian = linearized_hessian_periodic(
        phase,
        polarity_bits,
        links,
        coupling=coupling,
        phase_representation=phase_representation,
    )
    return np.linalg.eigvalsh(hessian / inertia)


def stability_summary(omega_squared: np.ndarray, tolerance: float = 1e-10) -> dict[str, int | float | bool]:
    """Classify a linearized spectrum by negative, zero, and positive modes."""
    values = np.asarray(omega_squared, dtype=float)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("omega_squared must be a finite one-dimensional array")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")

    negative = int(np.count_nonzero(values < -tolerance))
    zero = int(np.count_nonzero(np.abs(values) <= tolerance))
    positive = int(np.count_nonzero(values > tolerance))
    return {
        "stable": negative == 0,
        "negative_modes": negative,
        "zero_modes": zero,
        "positive_modes": positive,
        "minimum_omega_squared": float(np.min(values)),
        "maximum_omega_squared": float(np.max(values)),
    }
