"""Optional passive linear fluid-compliance network in SI units.

This is our modern storage/transfer control, not a reconstruction of Russell's
apparatus or a nonlinear gas model. There are no external sources or reservoirs.
"""

import json
import math
from dataclasses import dataclass, field

import numpy as np

MAX_NODES = 128
MAX_EDGES = 4096


def _array(value, name, ndim):
    try:
        raw = np.asarray(value)
        if raw.dtype.kind not in "fiu" or raw.ndim != ndim:
            raise ValueError
        result = np.array(raw, dtype=float, copy=True)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite real {ndim}-dimensional array") from error
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must be finite")
    # Immutable backing prevents a caller from re-enabling writes and making
    # the public parameters disagree with the cached component eigensystems.
    return np.frombuffer(result.tobytes(), dtype=float).reshape(result.shape)


def _time(value):
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError("time_s must be a finite nonnegative real scalar")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("time_s must be a finite nonnegative real scalar") from error
    if not math.isfinite(result) or result < 0:
        raise ValueError("time_s must be a finite nonnegative real scalar")
    return result


def _finite_result(value):
    if not np.isfinite(value).all():
        raise ValueError("derived storage quantities must remain finite")
    return value


@dataclass(frozen=True, eq=False)
class PressureStorageNetwork:
    """C_i > 0 [m^3/Pa], G_e >= 0 [m^3/(Pa s)], B with +tail/-head.

    Each incidence column must have exactly one +1 and one -1. An (n,0)
    incidence matrix is allowed. Zero-conductance links do not join components.
    Pressures are signed increments [Pa] about one fixed reference state.
    """

    compliance_m3_per_pa: np.ndarray
    conductance_m3_per_pa_s: np.ndarray
    incidence: np.ndarray
    _components: tuple = field(init=False, repr=False)
    _spectra: tuple = field(init=False, repr=False)

    def __post_init__(self):
        c = _array(self.compliance_m3_per_pa, "compliance", 1)
        g = _array(self.conductance_m3_per_pa_s, "conductance", 1)
        b = _array(self.incidence, "incidence", 2)
        n, e = len(c), len(g)
        if not 1 <= n <= MAX_NODES or e > MAX_EDGES or b.shape != (n, e):
            raise ValueError("expected 1..128 nodes, <=4096 edges, and incidence shape (nodes, edges)")
        if np.any(c <= 0) or np.any(g < 0):
            raise ValueError("compliance must be positive and conductance nonnegative")
        if (not np.isin(b, (-1, 0, 1)).all() or
                np.any(np.sum(b == 1, axis=0) != 1) or np.any(np.sum(b == -1, axis=0) != 1)):
            raise ValueError("each incidence column must have exactly one +1 and one -1")
        for name, value in (("compliance_m3_per_pa", c), ("conductance_m3_per_pa_s", g), ("incidence", b)):
            object.__setattr__(self, name, value)

        neighbors = [set() for _ in c]
        for edge in np.flatnonzero(g > 0):
            tail, head = np.flatnonzero(b[:, edge])
            neighbors[tail].add(head)
            neighbors[head].add(tail)
        unseen, components = set(range(n)), []
        while unseen:
            todo, found = [min(unseen)], set()
            while todo:
                node = todo.pop()
                if node not in found:
                    found.add(node)
                    todo.extend(neighbors[node] - found)
            unseen -= found
            components.append(tuple(sorted(found)))
        object.__setattr__(self, "_components", tuple(components))

        spectra = []
        for component in components:
            indices = np.array(component)
            root = np.sqrt(c[indices])
            if len(indices) == 1:
                spectra.append((indices, root, np.empty(0), np.empty((1, 0))))
                continue
            # Remove exactly the known component-constant pressure mode before
            # solving. No numerically selected eigenvalue is forced to zero.
            unit = root / np.max(root)
            unit /= np.linalg.norm(unit)
            reflector = unit.copy()
            reflector[0] += 1
            complement = (np.eye(len(root)) - 2 * np.outer(reflector, reflector) /
                          np.dot(reflector, reflector))[:, 1:]
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                weighted = b[indices] * np.sqrt(g) / root[:, None]
                reduced = complement.T @ weighted
                matrix = reduced @ reduced.T
            _finite_result(matrix)
            rates, vectors = np.linalg.eigh(matrix)
            tolerance = 64 * np.finfo(float).eps * len(root) * np.max(np.abs(rates))
            if np.any(rates <= tolerance):
                raise ValueError("positive component decay rates are numerically unresolved")
            spectra.append((indices, root, rates, complement @ vectors))
        object.__setattr__(self, "_spectra", tuple(spectra))

    @property
    def components(self):
        """Node-index components connected by strictly positive conductance."""
        return self._components

    @property
    def relaxation_rates_per_s(self):
        """Positive decay rates; one exact stationary mode per component is omitted."""
        return np.sort(np.concatenate([item[2] for item in self._spectra]))

    def _pressure(self, value):
        p = _array(value, "pressure_pa", 1)
        if p.shape != self.compliance_m3_per_pa.shape:
            raise ValueError("pressure must have one value per node")
        return p

    def equilibrium_pressure(self, initial_pressure_pa):
        p = self._pressure(initial_pressure_pa)
        result = np.empty_like(p)
        for indices, _, _, _ in self._spectra:
            weights = self.compliance_m3_per_pa[indices]
            weights = weights / np.max(weights)
            weights /= np.sum(weights)
            result[indices] = np.dot(weights, p[indices])
        return _finite_result(result)

    def _evolve(self, initial_pressure_pa, time_s):
        p = self._pressure(initial_pressure_pa)
        time = _time(time_s)
        equilibrium = self.equilibrium_pressure(p)
        result, loss = equilibrium.copy(), 0.0
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            for indices, root, rates, modes in self._spectra:
                coefficients = modes.T @ (root * (p[indices] - equilibrium[indices]))
                _finite_result(coefficients)
                exponent = -rates * time  # -inf represents fully decayed modes.
                result[indices] += (modes @ (np.exp(exponent) * coefficients)) / root
                loss += 0.5 * np.dot(coefficients**2, -np.expm1(2 * exponent))
        _finite_result(result)
        _finite_result(loss)
        return (p.copy() if time == 0 else result), float(loss)

    def pressure_at(self, initial_pressure_pa, time_s):
        """Exact modal evolution of the declared linear model, in float64."""
        return self._evolve(initial_pressure_pa, time_s)[0]

    def flow_m3_per_s(self, pressure_pa):
        p = self._pressure(pressure_pa)
        with np.errstate(over="ignore", invalid="ignore"):
            return _finite_result(self.conductance_m3_per_pa_s * (self.incidence.T @ p))

    def pressure_rate_pa_per_s(self, pressure_pa):
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            return _finite_result(-(self.incidence @ self.flow_m3_per_s(pressure_pa)) /
                                  self.compliance_m3_per_pa)

    def energy_j(self, pressure_pa):
        p = self._pressure(pressure_pa)
        with np.errstate(over="ignore", invalid="ignore"):
            energy_coordinates = np.sqrt(self.compliance_m3_per_pa) * p
            return float(_finite_result(0.5 * np.dot(energy_coordinates, energy_coordinates)))

    def audit(self, initial_pressure_pa, time_s):
        """Independent modal loss integral plus endpoint energy/volume balance.

        Energy is relative to the selected reference. Uniform residual pressure
        is not energy available to internal links with zero pressure difference.
        """
        initial = self._pressure(initial_pressure_pa)
        final, loss = self._evolve(initial, time_s)
        flow = self.flow_m3_per_s(final)
        rate = self.pressure_rate_pa_per_s(final)
        before, after = self.energy_j(initial), self.energy_j(final)
        with np.errstate(over="ignore", invalid="ignore"):
            volume_residuals = [float(np.dot(self.compliance_m3_per_pa[list(nodes)],
                                           (final - initial)[list(nodes)])) for nodes in self.components]
            dissipation = float(np.dot(flow, self.incidence.T @ final))
            power_balance = float(np.dot(self.compliance_m3_per_pa * final, rate) + dissipation)
        _finite_result(volume_residuals)
        _finite_result((dissipation, power_balance, after - before + loss))
        return {"pressure_pa": final, "equilibrium_pressure_pa": self.equilibrium_pressure(initial),
                "flow_m3_per_s": flow, "energy_before_j": before, "energy_after_j": after,
                "dissipated_energy_j": loss, "energy_balance_residual_j": after - before + loss,
                "component_volume_residuals_m3": np.array(volume_residuals),
                "dissipation_power_w": dissipation, "power_balance_residual_w": power_balance}


def main():
    network = PressureStorageNetwork(np.array([2, 3, 5]) * 1e-10,
                                     np.array([0.5, 0.8, 0.3]) * 1e-12,
                                     [[1, 0, -1], [-1, 1, 0], [0, -1, 1]])
    result = network.audit([100000, 20000, 0], 1000)
    print(json.dumps({"scope": "synthetic passive linear storage; no apparatus fit",
                      **{key: value.tolist() if isinstance(value, np.ndarray) else value
                         for key, value in result.items()}}, indent=2))


if __name__ == "__main__":
    main()
