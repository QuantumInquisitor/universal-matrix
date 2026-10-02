"""Optional synthetic two-loop passive LC model in SI units."""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import wraps
from numbers import Real

import numpy as np


def finite(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be finite and real")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be finite and real") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite and real")
    return result


def state_vector(value, name):
    """Accept exactly two finite real numbers without lossy type coercion."""
    try:
        # Object dtype preserves a boolean or complex element in mixed lists.
        raw = np.asarray(value, dtype=object)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must have shape (2,)") from error
    if raw.shape != (2,):
        raise ValueError(f"{name} must have shape (2,)")
    return np.array(
        [finite(item, f"{name}[{index}]") for index, item in enumerate(raw)], dtype=float
    )


def resolved(operation):
    """Reject unrepresentable derived results instead of returning NaN/infinity."""

    @wraps(operation)
    def checked(*args, **kwargs):
        try:
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                result = operation(*args, **kwargs)
        except (
            OverflowError,
            FloatingPointError,
            ZeroDivisionError,
            np.linalg.LinAlgError,
        ) as error:
            raise ValueError("derived quantities must be finite and resolved") from error
        if result is not None:
            values = result if isinstance(result, tuple) else (result,)
            if not all(np.isfinite(value).all() for value in values):
                raise ValueError("derived quantities must be finite and resolved")
        return result

    return checked


@dataclass(frozen=True)
class CoupledLC:
    L1_h: float
    L2_h: float
    C1_f: float
    C2_f: float
    M_h: float
    R1_ohm: float = 0.0
    R2_ohm: float = 0.0
    parameter_source: str = "synthetic numerical control; not measured apparatus"

    @resolved
    def __post_init__(self):
        for name in ("L1_h", "L2_h", "C1_f", "C2_f", "M_h", "R1_ohm", "R2_ohm"):
            object.__setattr__(self, name, finite(getattr(self, name), name))
        if min(self.L1_h, self.L2_h, self.C1_f, self.C2_f) <= 0:
            raise ValueError("self-inductances and capacitances must be positive")
        if min(self.R1_ohm, self.R2_ohm) < 0:
            raise ValueError("resistances must be nonnegative")
        if not isinstance(self.parameter_source, str) or not self.parameter_source.strip():
            raise ValueError("parameter_source must be explicit")
        if not abs(self.coupling) < 1:
            raise ValueError("positive magnetic energy requires |M| < sqrt(L1 L2)")
        L, K, R = self.matrices()
        if not all(np.isfinite(a).all() for a in (L, K, R)):
            raise ValueError("derived matrices must be finite and resolved")

    @property
    def coupling(self):
        return self.M_h / (math.sqrt(self.L1_h) * math.sqrt(self.L2_h))

    @resolved
    def matrices(self):
        return (
            np.array(((self.L1_h, self.M_h), (self.M_h, self.L2_h))),
            np.diag((1 / self.C1_f, 1 / self.C2_f)),
            np.diag((self.R1_ohm, self.R2_ohm)),
        )

    @resolved
    def analytic_omega_squared(self):
        """Lossless roots; stable lower-root evaluation avoids subtraction."""
        a = (1 / math.sqrt(self.L1_h) / math.sqrt(self.C1_f)) ** 2
        b = (1 / math.sqrt(self.L2_h) / math.sqrt(self.C2_f)) ** 2
        k = self.coupling
        discriminant = math.hypot(a - b, 2 * k * math.sqrt(a) * math.sqrt(b))
        upper_numerator = a + b + discriminant
        roots = np.array((2 * a * b / upper_numerator, upper_numerator / (2 * (1 - k * k))))
        if not np.isfinite(roots).all() or min(roots) <= 0:
            raise ValueError("derived mode frequencies must be finite and resolved")
        return roots

    @resolved
    def numerical_modes(self):
        """Independent symmetric generalized eigensystem K v = omega^2 L v."""
        L, K, _ = self.matrices()
        S = np.linalg.cholesky(L)
        inverse_S = np.linalg.solve(S, np.eye(2))
        squared, u = np.linalg.eigh(inverse_S @ K @ inverse_S.T)
        if min(squared) <= 0:
            raise ValueError("mode frequencies must be positive and resolved")
        v = np.linalg.solve(S.T, u)
        # Fix only each vector's arbitrary global sign; relative sign is data.
        for j in range(2):
            if v[0, j] < 0:
                v[:, j] *= -1
        return squared, v

    @resolved
    def state_matrix(self):
        L, K, R = self.matrices()
        return np.block(
            [[np.zeros((2, 2)), np.eye(2)], [-np.linalg.solve(L, K), -np.linalg.solve(L, R)]]
        )

    @resolved
    def energy(self, q, i):
        q = state_vector(q, "q")
        i = state_vector(i, "i")
        L, K, _ = self.matrices()
        value = float((q @ K @ q + i @ L @ i) / 2)
        if value < 0:
            raise ValueError("energy must be nonnegative and resolved")
        return value
