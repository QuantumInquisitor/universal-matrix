"""Reproducible mathematical controls for the eight-image review.

These are counterexamples and unit conversions, not reconstructions of an
unspecified physical device. No engine constants or defaults are modified.
"""

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np


def report():
    c, h, electron_volt = 299792458.0, 6.62607015e-34, 1.602176634e-19
    frequency = 613e12
    delta = Fraction("0.018451")
    # This recurrence is conditional on exact turns per discrete update.
    assert (delta * delta.denominator).denominator == 1
    phases = math.tau * np.arange(16) / 16
    coherence = abs(np.mean(np.exp(1j * phases)))
    target_alignment = abs(np.mean(np.exp(1j * (phases - phases))))
    rng = np.random.default_rng(743)
    raw = rng.normal(size=(16, 16))
    R = (raw + raw.T) / 2
    D = np.diag(np.exp(1j * phases))
    C = D @ R @ D.conj().T
    eig_error = float(np.max(np.abs(np.linalg.eigvalsh(C) - np.linalg.eigvalsh(R))))
    hermitian_error = float(np.max(np.abs(C - C.conj().T)))
    asymmetric = D @ raw @ D.conj().T
    asymmetric_error = float(np.max(np.abs(asymmetric - asymmetric.conj().T)))
    assert eig_error < 1e-12 and hermitian_error < 1e-12 and asymmetric_error > 0.1
    assert coherence < 1e-12 and target_alignment == 1
    psi = np.array((math.sqrt(0.01), math.sqrt(0.99)))
    target_projector = np.diag((1.0, 0.0))
    rejected_projector = np.eye(2) - target_projector
    np.testing.assert_allclose(
        target_projector.T @ target_projector + rejected_projector.T @ rejected_projector, np.eye(2)
    )
    filtered = target_projector @ psi
    success = float(np.dot(filtered, filtered))
    conditional = filtered / np.linalg.norm(filtered)
    assert math.isclose(success, 0.01) and conditional[0] ** 2 == 1
    reflection_path = []
    rotation_path = []
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        reflection_path.append(
            {"phase": t, "determinant": float(np.linalg.det(np.diag((1, 1, 1 - 2 * t))))}
        )
        angle = math.pi * t
        rotation = np.array(
            (
                (1, 0, 0),
                (0, math.cos(angle), -math.sin(angle)),
                (0, math.sin(angle), math.cos(angle)),
            )
        )
        rotation_path.append(
            {
                "phase": t,
                "determinant": float(np.linalg.det(rotation)),
                "direction": (rotation @ np.array((0, 0, 1))).tolist(),
            }
        )
    assert reflection_path[2]["determinant"] == 0
    assert all(abs(row["determinant"] - 1) < 1e-12 for row in rotation_path)
    weight = 4200 * 9.80665
    return {
        "scope": "Literal-image algebra controls and explicitly conditional examples; no claimed image device validated",
        "optical_frequency": {
            "frequency_Hz": frequency,
            "vacuum_wavelength_nm": c / frequency * 1e9,
            "quantum_energy_eV": h * frequency / electron_volt,
        },
        "phase_offset": {
            "displayed_decimal": str(delta.numerator / delta.denominator),
            "exact_fraction": str(delta),
            "return_steps_if_exact_turns_per_update": delta.denominator,
            "actual_image_units": "unspecified",
        },
        "orientation": {
            "identity_to_reflection_linear_path": reflection_path,
            "proper_rotation_direction_reversal": rotation_path,
            "limit": "A_b is undefined in image; deformation interpretation is conditional",
        },
        "lattice": {
            "literal_azimuths_degrees": sorted(set(30 * (n % 4) for n in range(16))),
            "all_possible_undirected_nonself_pairs": math.comb(16, 2),
            "claimed_links": 64,
            "adjacency_supplied": False,
            "claimed_octave_formula_12_step_ratio": 12.0,
            "actual_octave_12_step_ratio": 2.0,
        },
        "coupling": {
            "hermitian_error_symmetric_R": hermitian_error,
            "hermitian_error_asymmetric_R": asymmetric_error,
            "phase_decoration_eigenvalue_error": eig_error,
            "seed": 743,
        },
        "phase_pattern": {
            "sixteen_node_traveling_pattern_common_phase_order": float(coherence),
            "target_relative_alignment": float(target_alignment),
            "dynamical_stability_tested": False,
        },
        "conditional_measurement": {
            "success_probability": success,
            "conditional_target_probability": float(conditional[0] ** 2),
            "failure_probability": 1 - success,
            "mechanism": "two-outcome projective measurement toy example, not material synthesis",
        },
        "blueprint_accounting": {
            "displayed_mass_kg": 4200,
            "assumed_standard_gravity_m_s2": 9.80665,
            "required_hover_force_N": weight,
            "displayed_stored_energy_J": 5e6,
            "storage_duration_at_assumed_1MW_s": 5.0,
            "power_W_if_thrust_only_from_one_way_photons": weight * c,
            "limit": "No thrust mechanism or power demand is derived from the picture; examples do not bound other propulsion mechanisms",
        },
        "position_not_state": {
            "same_position": [1, 0, 0],
            "first_velocity": [0, 1, 0],
            "second_velocity": [0, -1, 0],
            "position_return_error": 0,
            "velocity_return_error": 2,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
