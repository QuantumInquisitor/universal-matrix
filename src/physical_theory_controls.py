"""Bounded established-theory controls for spectra and periodic fields.

The hydrogen comparison is a nonrelativistic approximation to evaluated NIST
reference values. The ABC field lives on a periodic three-dimensional box.
Neither control fits the Matrix geometry or identifies a physical ring mode.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# CODATA 2022, SI; these constants are supplied, not fitted to this catalog.
RYDBERG_INFINITY_PER_M = 10973731.568157
ELECTRON_PROTON_MASS_RATIO = 5.446170214889e-4
LIGHT_SPEED_M_PER_S = 299792458.0

# Explicit Lyman-series assignments, not a nearest-frequency search. The last
# two rows resolve fine structure which this principal-quantum-number model
# deliberately cannot resolve. n=6,7,8 are the series assignments of the three
# nonpersistent rows; n=2..5 also have configurations in NIST's persistent table.
NIST_VACUUM_UPPER_N = {
    "926.2256": 8, "930.7482": 7, "937.8034": 6, "949.7430": 5,
    "972.5367": 4, "1025.7222": 3, "1215.66824": 2, "1215.67364": 2,
}


def _finite(value, name: str) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be finite and real")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be finite and real") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite and real")
    return result


def _positive(value, name: str) -> float:
    result = _finite(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def hydrogen_rydberg_wavelength_A(lower_n: int, upper_n: int, *, reduced_mass: bool) -> float:
    """Vacuum wavelength in angstroms for nonrelativistic, field-free 1H.

    No fine structure, Lamb shift, hyperfine structure, external-field shift,
    linewidth, or transition intensity is predicted by this approximation.
    """
    if type(lower_n) is not int or type(upper_n) is not int or not 1 <= lower_n < upper_n:
        raise ValueError("quantum numbers must be integers with 1 <= lower_n < upper_n")
    if type(reduced_mass) is not bool:
        raise ValueError("reduced_mass must be an explicit boolean")
    constant = RYDBERG_INFINITY_PER_M
    if reduced_mass:
        constant /= 1.0 + ELECTRON_PROTON_MASS_RATIO
    # This form avoids subtracting nearly equal reciprocal squares.
    try:
        separation = ((upper_n - lower_n) * (upper_n + lower_n)
                      / (lower_n * lower_n * upper_n * upper_n))
        wavenumber = _positive(constant * separation, "transition wavenumber")
        return _positive(1e10 / wavenumber, "wavelength")
    except OverflowError as error:
        raise ValueError("quantum numbers exceed finite numerical range") from error


@dataclass(frozen=True)
class HydrogenLineResidual:
    wavelength_A: str
    upper_n: int
    infinite_mass_wavelength_A: float
    reduced_mass_wavelength_A: float
    infinite_mass_residual_ppm: float
    reduced_mass_residual_ppm: float


@dataclass(frozen=True)
class HydrogenReferenceAudit:
    lines: tuple[HydrogenLineResidual, ...]
    excluded_air_rows: int
    infinite_mass_rms_ppm: float
    reduced_mass_rms_ppm: float


def audit_hydrogen_vacuum_rows(rows) -> HydrogenReferenceAudit:
    """Compare explicit NIST vacuum assignments; retain each fine component.

    Air wavelengths are counted but never treated as vacuum wavelengths.
    RMS is an unweighted descriptive discrepancy, not a statistical fit.
    """
    comparisons, excluded = [], 0
    for row in rows:
        if row.get("isotope") != "1H" or row.get("spectrum") != "H I":
            raise ValueError("comparison requires the declared 1H H I reference")
        reported = row.get("wavelength_A")
        wavelength = _positive(reported, "reference wavelength")
        if row.get("medium") == "air":
            excluded += 1
            continue
        if row.get("medium") != "vacuum":
            raise ValueError("reference wavelength medium must be explicit")
        if reported not in NIST_VACUUM_UPPER_N:
            raise ValueError("vacuum row lacks an explicit declared series assignment")
        upper = NIST_VACUUM_UPPER_N[reported]
        infinite = hydrogen_rydberg_wavelength_A(1, upper, reduced_mass=False)
        reduced = hydrogen_rydberg_wavelength_A(1, upper, reduced_mass=True)
        comparisons.append(HydrogenLineResidual(reported, upper, infinite, reduced,
            (infinite - wavelength) / wavelength * 1e6, (reduced - wavelength) / wavelength * 1e6))
    if not comparisons:
        raise ValueError("comparison needs at least one assigned vacuum row")
    def rms(attribute):
        return math.sqrt(math.fsum(getattr(row, attribute)**2 for row in comparisons) / len(comparisons))
    return HydrogenReferenceAudit(tuple(comparisons), excluded,
                                   rms("infinite_mass_residual_ppm"), rms("reduced_mass_residual_ppm"))


@dataclass(frozen=True)
class ABCField:
    """A curl eigenfield on a periodic cube, not an embedded solid torus.

    period_length and coordinates use the same length unit; amplitudes use one
    common field unit. Defaults define a dimensionless numerical control.
    A magnetic interpretation additionally requires an explicit permeability.
    """

    amplitudes: tuple[float, float, float] = (1.0, 1.0, 1.0)
    period_length: float = 2.0 * math.pi
    mode_number: int = 1

    def __post_init__(self) -> None:
        if len(self.amplitudes) != 3:
            raise ValueError("ABC requires three amplitudes")
        object.__setattr__(self, "amplitudes", tuple(_finite(a, "amplitude") for a in self.amplitudes))
        object.__setattr__(self, "period_length", _positive(self.period_length, "period_length"))
        if type(self.mode_number) is not int or self.mode_number < 1:
            raise ValueError("mode_number must be a positive integer")
        _positive(self.wavenumber, "wavenumber")

    @property
    def wavenumber(self) -> float:
        try:
            return 2.0 * math.pi * self.mode_number / self.period_length
        except OverflowError as error:
            raise ValueError("wavenumber exceeds finite numerical range") from error

    def value(self, points) -> np.ndarray:
        points = np.asarray(points, dtype=float)
        if points.ndim < 1 or points.shape[-1] != 3 or not np.all(np.isfinite(points)):
            raise ValueError("points must have three finite coordinates")
        # Reduction limits phase growth and explicitly implements the quotient.
        angles = np.remainder(points, self.period_length) * self.wavenumber
        if not np.all(np.isfinite(angles)):
            raise ValueError("field phase exceeds finite numerical range")
        x, y, z = np.moveaxis(angles, -1, 0)
        a, b, c = self.amplitudes
        result = np.stack((a * np.sin(z) + c * np.cos(y),
                           b * np.sin(x) + a * np.cos(z),
                           c * np.sin(y) + b * np.cos(x)), axis=-1)
        if not np.all(np.isfinite(result)):
            raise ValueError("field exceeds finite numerical range")
        return result

    def current_density(self, points, *, permeability) -> np.ndarray:
        """Magnetostatic J=(curl B)/mu; caller supplies consistent SI inputs."""
        permeability = _positive(permeability, "permeability")
        coefficient = _positive(self.wavenumber / permeability, "resolved current coefficient")
        current = self.value(points) * coefficient
        if not np.all(np.isfinite(current)):
            raise ValueError("current exceeds finite numerical range")
        return current


def periodic_grid(grid_size: int, period_length: float) -> np.ndarray:
    if type(grid_size) is not int or grid_size < 4:
        raise ValueError("grid_size must be an integer at least four")
    period = _positive(period_length, "period_length")
    coordinates = (np.arange(grid_size) + 0.37) * (period / grid_size)
    return np.stack(np.meshgrid(coordinates, coordinates, coordinates, indexing="ij"), axis=-1)


@dataclass(frozen=True)
class PeriodicFieldAudit:
    grid_size: int
    relative_divergence_error: float
    relative_curl_error: float
    relative_force_free_error: float
    mean_squared_field: float
    magnetic_helicity: float


def audit_periodic_field(values, *, period_length, curl_eigenvalue) -> PeriodicFieldAudit:
    """Independent periodic centered differences, with resolved signed curl k.

    The helicity uses A=B/k, which is a vector potential only for a curl
    eigenfield. Its interpretation is conditional on the curl residual.
    """
    values = np.asarray(values, dtype=float)
    if (values.ndim != 4 or values.shape[-1] != 3 or len(set(values.shape[:3])) != 1
            or values.shape[0] < 4 or not np.all(np.isfinite(values))):
        raise ValueError("values must form a finite cubic N by N by N vector grid")
    period = _positive(period_length, "period_length")
    eigenvalue = _finite(curl_eigenvalue, "curl_eigenvalue")
    if eigenvalue == 0:
        raise ValueError("curl_eigenvalue must be nonzero")
    size = values.shape[0]
    step = _positive(period / size, "grid spacing")
    grid_eigenvalue = _finite(eigenvalue * step, "curl eigenvalue times grid spacing")
    if abs(grid_eigenvalue) >= math.pi:
        raise ValueError("curl mode must lie below the grid Nyquist frequency")
    _positive(abs(grid_eigenvalue), "resolved curl eigenvalue times grid spacing")
    amplitude = _positive(float(np.max(np.abs(values))), "nonzero field amplitude")
    # Scale relative diagnostics before taking products. Otherwise an entirely
    # ordinary small field can underflow the fourth-order force normalization.
    normalized = values / amplitude
    derivatives = [(np.roll(normalized, -1, axis=axis) - np.roll(normalized, 1, axis=axis)) / 2.0
                   for axis in range(3)]
    divergence = sum(derivatives[axis][..., axis] for axis in range(3))
    curl = np.stack((derivatives[1][..., 2] - derivatives[2][..., 1],
                     derivatives[2][..., 0] - derivatives[0][..., 2],
                     derivatives[0][..., 1] - derivatives[1][..., 0]), axis=-1)
    squared = np.sum(normalized * normalized, axis=-1)
    normalized_mean = float(np.mean(squared))
    mean_squared = _positive(amplitude * amplitude * normalized_mean, "resolved mean squared field")
    curl_scale = _positive(abs(grid_eigenvalue) * math.sqrt(normalized_mean), "curl normalization")
    divergence_error = float(np.sqrt(np.mean(divergence**2))) / curl_scale
    curl_error = float(np.sqrt(np.mean(np.sum((curl - grid_eigenvalue * normalized)**2, axis=-1)))) / curl_scale
    force_scale = _positive(abs(grid_eigenvalue) * math.sqrt(float(np.mean(squared**2))), "force normalization")
    force_error = float(np.sqrt(np.mean(np.sum(np.cross(curl, normalized)**2, axis=-1)))) / force_scale
    try:
        helicity = period**3 * mean_squared / eigenvalue
    except OverflowError as error:
        raise ValueError("helicity exceeds finite numerical range") from error
    _positive(abs(helicity), "resolved magnetic helicity")
    for name, value in (("divergence residual", divergence_error), ("curl residual", curl_error),
                        ("force residual", force_error), ("helicity", helicity)):
        _finite(value, name)
    return PeriodicFieldAudit(size, divergence_error, curl_error, force_error, mean_squared, helicity)


def main() -> None:
    path = Path(__file__).parent / "reference_data" / "nist_hydrogen_lines.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    hydrogen = audit_hydrogen_vacuum_rows(data["rows"])
    print("ESTABLISHED THEORY CONTROLS; NO FIT TO MATRIX GEOMETRY")
    print(f"hydrogen_vacuum_rows={len(hydrogen.lines)}; excluded_air_rows={hydrogen.excluded_air_rows}")
    print(f"infinite_mass_rms_ppm={hydrogen.infinite_mass_rms_ppm:.9g}; "
          f"reduced_mass_rms_ppm={hydrogen.reduced_mass_rms_ppm:.9g}")
    for line in hydrogen.lines:
        print(f"reference_A={line.wavelength_A}; upper_n={line.upper_n}; "
              f"reduced_mass_discrepancy_ppm={line.reduced_mass_residual_ppm:.9g}")
    field = ABCField()
    for size in (16, 32, 64):
        audit = audit_periodic_field(field.value(periodic_grid(size, field.period_length)),
            period_length=field.period_length, curl_eigenvalue=field.wavenumber)
        print(f"ABC_grid={size}; divergence={audit.relative_divergence_error:.3g}; "
              f"curl_error={audit.relative_curl_error:.9g}; force_free={audit.relative_force_free_error:.3g}")
    print("scope=nonrelativistic_hydrogen_reference_and_periodic_cube_curl_eigenfield")
    print("not_QED_accuracy_or_embedded_torus_boundary_solution_or_physical_ring_validation")


if __name__ == "__main__":
    main()
