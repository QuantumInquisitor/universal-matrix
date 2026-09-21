"""Candidate massive-motion laws from the content-clock scalar.

The content-clock law defines

    ln n = g * (C - C_ref).

That relation alone does not determine a massive-particle action.

A broad minimal scalar-potential family is

    U/m = s * v_*^2 * ln n,

where
    s = -1  -> acceleration toward increasing content,
    s = +1  -> acceleration toward decreasing content.

Then

    a = -grad(U/m)
      = -s * v_*^2 * grad(ln n)
      = -s * v_*^2 * g * grad(C).

The inertial mass cancels, so either branch has universal test-particle
acceleration. However, the sign s is not fixed by the content-clock law.

This module intentionally requires the branch to be named explicitly. There is
no default "gravity" choice.

It is an experimental diagnostic of what remains underdetermined.
"""

from __future__ import annotations

from typing import Literal, Sequence
import math
import numpy as np


MotionBranch = Literal["toward_higher_content", "toward_lower_content"]


def branch_sign(branch: MotionBranch) -> float:
    if branch == "toward_higher_content":
        return -1.0
    if branch == "toward_lower_content":
        return 1.0
    raise ValueError("unknown motion branch")


def specific_potential(
    content: float,
    coupling: float,
    speed_scale: float,
    branch: MotionBranch,
    reference_content: float = 0.0,
) -> float:
    """Potential energy per unit inertial mass."""
    if content < 0 or reference_content < 0:
        raise ValueError("content values must be non-negative")
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    if speed_scale <= 0:
        raise ValueError("speed_scale must be positive")
    s = branch_sign(branch)
    return (
        s
        * speed_scale**2
        * coupling
        * (content - reference_content)
    )


def acceleration_from_content_gradient(
    content_gradient: Sequence[float],
    coupling: float,
    speed_scale: float,
    branch: MotionBranch,
) -> np.ndarray:
    """Universal test-particle acceleration for the selected scalar branch."""
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    if speed_scale <= 0:
        raise ValueError("speed_scale must be positive")
    grad = np.asarray(content_gradient, dtype=float)
    s = branch_sign(branch)
    return -s * speed_scale**2 * coupling * grad


def massive_force(
    inertial_mass: float,
    content_gradient: Sequence[float],
    coupling: float,
    speed_scale: float,
    branch: MotionBranch,
) -> np.ndarray:
    """Force is m*a; acceleration itself is independent of inertial mass."""
    if inertial_mass <= 0:
        raise ValueError("inertial_mass must be positive")
    return inertial_mass * acceleration_from_content_gradient(
        content_gradient,
        coupling,
        speed_scale,
        branch,
    )


def escape_speed_from_potential_drop(
    content_start: float,
    content_reference: float,
    coupling: float,
    speed_scale: float,
    branch: MotionBranch,
) -> float:
    """Newtonian-energy analogue for a static scalar-potential candidate.

    Returns sqrt(max(0, 2*(V_ref - V_start))) for specific potential V=U/m.
    This helper does not imply that the branch is physically correct.
    """
    v_start = specific_potential(
        content_start,
        coupling,
        speed_scale,
        branch,
        reference_content=0.0,
    )
    v_ref = specific_potential(
        content_reference,
        coupling,
        speed_scale,
        branch,
        reference_content=0.0,
    )
    delta = v_ref - v_start
    return math.sqrt(max(0.0, 2.0 * delta))
