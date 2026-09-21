"""Open-boundary finite-volume Gauss solver for the six canonical Matrix gates.

The domain is a finite 3D cell complex with six physical faces corresponding to
+X,-X,+Y,-Y,+Z,-Z. The scalar potential is solved from

    div(E) = rho,
    E = -grad(phi),

with prescribed outward electric flux on the six boundary faces.

Discretization
--------------
Interior link flux:
    E_i(x) = phi(x) - phi(x+e_i)

At a boundary face, the outward electric flux is prescribed directly.

The resulting cell equation is

    L_N phi = rho - b,

where L_N is the graph/Neumann Laplacian containing only interior neighbor
differences and b is the sum of prescribed outward boundary flux densities
touching each boundary cell.

Compatibility requires

    sum_x rho(x) = total outward boundary flux.

Because pure Neumann problems have an additive constant nullspace, the solver
works in the mean-zero subspace.

Numerics
--------
A matrix-free projected preconditioned conjugate-gradient method is used. The
Jacobi preconditioner is the inverse interior-neighbor degree. No dense matrix
is formed, so the solver scales to substantially larger grids than a direct
factorization.

This is an experimental field solver. Mapping lattice units to SI units remains
a separate physical problem.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


FACE_NAMES = ("x_pos", "x_neg", "y_pos", "y_neg", "z_pos", "z_neg")


@dataclass(frozen=True)
class GateFieldFlux:
    """Total outward electric flux through each canonical boundary gate.

    Positive means electric field flux leaves the internal domain.
    """

    x_pos: float = 0.0
    x_neg: float = 0.0
    y_pos: float = 0.0
    y_neg: float = 0.0
    z_pos: float = 0.0
    z_neg: float = 0.0

    def total_outward_flux(self) -> float:
        return (
            self.x_pos + self.x_neg
            + self.y_pos + self.y_neg
            + self.z_pos + self.z_neg
        )

    def as_dict(self) -> dict[str, float]:
        return {name: getattr(self, name) for name in FACE_NAMES}


@dataclass
class OpenBoundarySolution:
    potential: np.ndarray
    electric_links: dict[str, np.ndarray]
    boundary_flux_density: dict[str, np.ndarray]
    iterations: int
    residual_norm: float
    compatibility_residual: float

    def max_abs_gauss_residual(self, rho: np.ndarray) -> float:
        residual = gauss_residual(
            rho,
            self.electric_links,
            self.boundary_flux_density,
        )
        return float(np.max(np.abs(residual)))

    def field_energy(self) -> float:
        interior = 0.5 * sum(
            float(np.sum(e * e))
            for e in self.electric_links.values()
        )
        # Boundary flux is prescribed Neumann data, not an independent interior
        # link degree of freedom, so it is excluded from this cell-link energy.
        return interior


def _project_mean_zero(a: np.ndarray) -> np.ndarray:
    return a - np.mean(a)


def _neighbor_degree(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = shape
    degree = np.zeros(shape, dtype=float)
    if nx > 1:
        degree[:-1, :, :] += 1
        degree[1:, :, :] += 1
    if ny > 1:
        degree[:, :-1, :] += 1
        degree[:, 1:, :] += 1
    if nz > 1:
        degree[:, :, :-1] += 1
        degree[:, :, 1:] += 1
    return degree


def neumann_laplacian(phi: np.ndarray) -> np.ndarray:
    """Positive graph Laplacian using only internal nearest-neighbor links."""
    if phi.ndim != 3:
        raise ValueError("phi must be a 3D array")
    out = np.zeros_like(phi, dtype=float)

    dx = phi[:-1, :, :] - phi[1:, :, :]
    out[:-1, :, :] += dx
    out[1:, :, :] -= dx

    dy = phi[:, :-1, :] - phi[:, 1:, :]
    out[:, :-1, :] += dy
    out[:, 1:, :] -= dy

    dz = phi[:, :, :-1] - phi[:, :, 1:]
    out[:, :, :-1] += dz
    out[:, :, 1:] -= dz

    return out


def boundary_flux_density(
    shape: tuple[int, int, int],
    flux: GateFieldFlux,
) -> dict[str, np.ndarray]:
    """Uniformly distribute each gate's total flux over that physical face."""
    nx, ny, nz = shape
    if min(shape) < 1:
        raise ValueError("shape entries must be positive")
    return {
        "x_pos": np.full((ny, nz), flux.x_pos / (ny * nz), dtype=float),
        "x_neg": np.full((ny, nz), flux.x_neg / (ny * nz), dtype=float),
        "y_pos": np.full((nx, nz), flux.y_pos / (nx * nz), dtype=float),
        "y_neg": np.full((nx, nz), flux.y_neg / (nx * nz), dtype=float),
        "z_pos": np.full((nx, ny), flux.z_pos / (nx * ny), dtype=float),
        "z_neg": np.full((nx, ny), flux.z_neg / (nx * ny), dtype=float),
    }


def boundary_source_array(
    shape: tuple[int, int, int],
    face_flux: dict[str, np.ndarray],
) -> np.ndarray:
    """Per-cell outward boundary-flux contribution b(x)."""
    nx, ny, nz = shape
    b = np.zeros(shape, dtype=float)
    b[nx - 1, :, :] += face_flux["x_pos"]
    b[0, :, :] += face_flux["x_neg"]
    b[:, ny - 1, :] += face_flux["y_pos"]
    b[:, 0, :] += face_flux["y_neg"]
    b[:, :, nz - 1] += face_flux["z_pos"]
    b[:, :, 0] += face_flux["z_neg"]
    return b


def compatibility_residual(rho: np.ndarray, flux: GateFieldFlux) -> float:
    return float(np.sum(rho) - flux.total_outward_flux())


def solve_open_gauss(
    rho: np.ndarray,
    flux: GateFieldFlux,
    tolerance: float = 1e-11,
    max_iterations: int = 20000,
) -> OpenBoundarySolution:
    """Solve the finite-volume open-boundary Gauss problem with projected PCG."""
    rho = np.asarray(rho, dtype=float)
    if rho.ndim != 3:
        raise ValueError("rho must be a 3D array")
    if min(rho.shape) < 2:
        raise ValueError("each dimension must be at least 2")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    compat = compatibility_residual(rho, flux)
    scale = max(1.0, abs(float(np.sum(rho))), abs(flux.total_outward_flux()))
    if abs(compat) > tolerance * scale:
        raise ValueError(
            "incompatible Neumann data: total charge must equal total outward flux"
        )

    face_flux = boundary_flux_density(rho.shape, flux)
    bnd = boundary_source_array(rho.shape, face_flux)
    rhs = _project_mean_zero(rho - bnd)

    degree = _neighbor_degree(rho.shape)
    inv_diag = np.zeros_like(degree)
    mask = degree > 0
    inv_diag[mask] = 1.0 / degree[mask]

    x = np.zeros_like(rho)
    r = _project_mean_zero(rhs - neumann_laplacian(x))
    z = _project_mean_zero(inv_diag * r)
    p = np.array(z, copy=True)
    rz_old = float(np.vdot(r, z).real)

    rhs_norm = float(np.linalg.norm(rhs.ravel()))
    target = tolerance * max(1.0, rhs_norm)
    residual_norm = float(np.linalg.norm(r.ravel()))

    if residual_norm <= target:
        iterations = 0
    else:
        iterations = 0
        for iteration in range(1, max_iterations + 1):
            ap = _project_mean_zero(neumann_laplacian(p))
            denom = float(np.vdot(p, ap).real)
            if abs(denom) < 1e-30:
                raise RuntimeError("PCG breakdown in Neumann solve")
            alpha = rz_old / denom
            x = _project_mean_zero(x + alpha * p)
            r = _project_mean_zero(r - alpha * ap)
            residual_norm = float(np.linalg.norm(r.ravel()))
            iterations = iteration
            if residual_norm <= target:
                break

            z = _project_mean_zero(inv_diag * r)
            rz_new = float(np.vdot(r, z).real)
            if abs(rz_old) < 1e-30:
                raise RuntimeError("PCG breakdown in preconditioned residual")
            beta = rz_new / rz_old
            p = _project_mean_zero(z + beta * p)
            rz_old = rz_new
        else:
            raise RuntimeError(
                f"open-boundary PCG did not converge in {max_iterations} iterations"
            )

    phi = _project_mean_zero(x)

    electric = {
        "x": phi[:-1, :, :] - phi[1:, :, :],
        "y": phi[:, :-1, :] - phi[:, 1:, :],
        "z": phi[:, :, :-1] - phi[:, :, 1:],
    }

    solution = OpenBoundarySolution(
        potential=phi,
        electric_links=electric,
        boundary_flux_density=face_flux,
        iterations=iterations,
        residual_norm=residual_norm,
        compatibility_residual=compat,
    )

    return solution


def gauss_residual(
    rho: np.ndarray,
    electric_links: dict[str, np.ndarray],
    face_flux: dict[str, np.ndarray],
) -> np.ndarray:
    """Cellwise div(E)-rho including true open-boundary face flux."""
    rho = np.asarray(rho, dtype=float)
    nx, ny, nz = rho.shape
    div = np.zeros_like(rho)

    ex = electric_links["x"]
    div[:-1, :, :] += ex
    div[1:, :, :] -= ex

    ey = electric_links["y"]
    div[:, :-1, :] += ey
    div[:, 1:, :] -= ey

    ez = electric_links["z"]
    div[:, :, :-1] += ez
    div[:, :, 1:] -= ez

    div[nx - 1, :, :] += face_flux["x_pos"]
    div[0, :, :] += face_flux["x_neg"]
    div[:, ny - 1, :] += face_flux["y_pos"]
    div[:, 0, :] += face_flux["y_neg"]
    div[:, :, nz - 1] += face_flux["z_pos"]
    div[:, :, 0] += face_flux["z_neg"]

    return div - rho


def balanced_gate_flux(
    total_charge: float,
    weights: dict[str, float] | None = None,
) -> GateFieldFlux:
    """Distribute required outward flux across the six canonical gates.

    This helper is explicit policy, not a derived law. Default weights are equal.
    Negative weights are forbidden; at least one weight must be positive.
    """
    if weights is None:
        weights = {name: 1.0 for name in FACE_NAMES}
    missing = set(FACE_NAMES) - set(weights)
    if missing:
        raise ValueError(f"missing gate weights: {sorted(missing)}")
    vals = {name: float(weights[name]) for name in FACE_NAMES}
    if any(v < 0 for v in vals.values()):
        raise ValueError("gate weights must be non-negative")
    total_weight = sum(vals.values())
    if total_weight <= 0:
        raise ValueError("at least one gate weight must be positive")
    allocated = {
        name: total_charge * vals[name] / total_weight
        for name in FACE_NAMES
    }
    return GateFieldFlux(**allocated)
