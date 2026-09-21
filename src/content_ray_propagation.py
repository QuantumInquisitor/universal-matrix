"""Ray propagation in a content-dependent travel-time index.

Given the experimental content-clock law

    n(x) = exp(g * (C(x) - C_ref)),

treat n as an isotropic travel-time/refractive index for the propagation
hypothesis "one fixed physical link per local canonical tick".

For a ray parameterized by Euclidean arc length s with unit tangent u,

    dx/ds = u

and Fermat/eikonal optics gives

    du/ds = grad(log n) - u * (u . grad(log n)).

The second term removes the tangent component, so only the transverse gradient
bends the ray.

Since

    log n = g * (C - C_ref),

we have

    grad(log n) = g * grad(C).

Thus the direction of bending is controlled by the gradient of content, while
the absolute reference content cancels from the local deflection equation.

This is an experimental propagation adapter. It is not a gravitational field
equation and does not establish gravitational lensing.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Callable, Sequence

import numpy as np


Vector = np.ndarray
ContentFn = Callable[[Vector], float]
GradientFn = Callable[[Vector], Vector]


def normalize(vector: Sequence[float] | Vector) -> Vector:
    v = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(v))
    if norm <= 0:
        raise ValueError("direction vector must be nonzero")
    return v / norm


def content_index(
    content: float,
    coupling: float,
    reference_content: float = 0.0,
) -> float:
    if content < 0 or reference_content < 0:
        raise ValueError("content values must be non-negative")
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    return math.exp(coupling * (content - reference_content))


def log_index_gradient(
    content_gradient: Sequence[float] | Vector,
    coupling: float,
) -> Vector:
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    return coupling * np.asarray(content_gradient, dtype=float)


def ray_direction_derivative(
    direction: Sequence[float] | Vector,
    content_gradient: Sequence[float] | Vector,
    coupling: float,
) -> Vector:
    """Fermat ray curvature in an isotropic content-dependent index."""
    u = normalize(direction)
    grad_log_n = log_index_gradient(content_gradient, coupling)
    return grad_log_n - u * float(np.dot(u, grad_log_n))


@dataclass
class RayState:
    position: Vector
    direction: Vector
    path_length: float = 0.0
    travel_time_index_integral: float = 0.0

    def __post_init__(self) -> None:
        self.position = np.asarray(self.position, dtype=float)
        self.direction = normalize(self.direction)
        if self.position.ndim != 1:
            raise ValueError("position must be a 1D vector")
        if self.direction.shape != self.position.shape:
            raise ValueError("position and direction dimensions must match")
        if self.path_length < 0:
            raise ValueError("path_length must be non-negative")


def _derivatives(
    position: Vector,
    direction: Vector,
    content_fn: ContentFn,
    gradient_fn: GradientFn,
    coupling: float,
    reference_content: float,
) -> tuple[Vector, Vector, float]:
    u = normalize(direction)
    content = float(content_fn(position))
    grad_content = np.asarray(gradient_fn(position), dtype=float)
    if grad_content.shape != position.shape:
        raise ValueError("gradient dimension mismatch")
    if content < 0:
        raise ValueError("content_fn returned negative content")
    du = ray_direction_derivative(u, grad_content, coupling)
    n = content_index(content, coupling, reference_content)
    return u, du, n


def rk4_ray_step(
    state: RayState,
    ds: float,
    content_fn: ContentFn,
    gradient_fn: GradientFn,
    coupling: float,
    reference_content: float = 0.0,
) -> RayState:
    """Fourth-order step for the Fermat ray equations."""
    if ds <= 0:
        raise ValueError("ds must be positive")

    x0 = state.position
    u0 = state.direction

    k1x, k1u, n1 = _derivatives(
        x0, u0, content_fn, gradient_fn, coupling, reference_content
    )
    k2x, k2u, n2 = _derivatives(
        x0 + 0.5 * ds * k1x,
        normalize(u0 + 0.5 * ds * k1u),
        content_fn,
        gradient_fn,
        coupling,
        reference_content,
    )
    k3x, k3u, n3 = _derivatives(
        x0 + 0.5 * ds * k2x,
        normalize(u0 + 0.5 * ds * k2u),
        content_fn,
        gradient_fn,
        coupling,
        reference_content,
    )
    k4x, k4u, n4 = _derivatives(
        x0 + ds * k3x,
        normalize(u0 + ds * k3u),
        content_fn,
        gradient_fn,
        coupling,
        reference_content,
    )

    position = x0 + (ds / 6.0) * (k1x + 2*k2x + 2*k3x + k4x)
    direction = normalize(
        u0 + (ds / 6.0) * (k1u + 2*k2u + 2*k3u + k4u)
    )
    optical_increment = (ds / 6.0) * (n1 + 2*n2 + 2*n3 + n4)

    return RayState(
        position=position,
        direction=direction,
        path_length=state.path_length + ds,
        travel_time_index_integral=(
            state.travel_time_index_integral + optical_increment
        ),
    )


def trace_ray(
    initial_state: RayState,
    steps: int,
    ds: float,
    content_fn: ContentFn,
    gradient_fn: GradientFn,
    coupling: float,
    reference_content: float = 0.0,
) -> list[RayState]:
    if steps < 0:
        raise ValueError("steps must be non-negative")
    states = [initial_state]
    current = initial_state
    for _ in range(steps):
        current = rk4_ray_step(
            current,
            ds,
            content_fn,
            gradient_fn,
            coupling,
            reference_content,
        )
        states.append(current)
    return states
