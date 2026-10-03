"""Independent physical identities and public-input regression controls."""

import json
import math
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from scripts.report_coupled_lc_reference import audit_case, build_report
from src.coupled_lc_reference import CoupledLC

MODEL = CoupledLC(1e-3, 4e-3, 10e-9, 4e-9, 0.5e-3)
invalid_scalars = {
    "python_complex": 1e-3 + 2j,
    "numpy_complex": np.complex128(1e-3 + 2j),
    "zero_imaginary_complex": complex(1e-3, 0),
    "nan": float("nan"),
    "inf": float("inf"),
    "python_bool": True,
    "numpy_bool": np.bool_(True),
    "numeric_string": "0.001",
    "scalar_array": np.array(0.001),
}
invalid_vectors = {
    "complex": np.array([1j, 0j]),
    "zero_imaginary_complex": np.array([1.0 + 0j, 0j]),
    "mixed_complex_list": [1.0, 1j],
    "nan": np.array([np.nan, 0.0]),
    "inf": np.array([0.0, np.inf]),
    "boolean": np.array([True, False]),
    "mixed_boolean_list": [True, 1.0],
    "mixed_boolean_object_array": np.array([1.0, False], dtype=object),
    "wrong_length": np.zeros(3),
    "column": np.zeros((2, 1)),
    "row": np.zeros((1, 2)),
    "scalar": 1.0,
    "ragged": [[1], [1, 2]],
    "numeric_strings": ["1", "2"],
}


@pytest.mark.parametrize("field", ["L1_h", "L2_h", "C1_f", "C2_f", "M_h", "R1_ohm", "R2_ohm"])
@pytest.mark.parametrize("value", invalid_scalars.values(), ids=invalid_scalars.keys())
def test_reject_invalid_scalars(field, value):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(ValueError, match=field):
            replace(MODEL, **{field: value})


@pytest.mark.parametrize("port", ["q", "i"])
@pytest.mark.parametrize("value", invalid_vectors.values(), ids=invalid_vectors.keys())
def test_reject_invalid_states(port, value):
    state = {"q": np.zeros(2), "i": np.zeros(2), port: value}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(ValueError, match=port):
            MODEL.energy(**state)


@pytest.mark.parametrize(
    "q",
    [
        [1, -2],
        (1, -2),
        np.array([1.0, -2.0]),
        np.array([1, -2]),
        np.array([1.0, -2.0], dtype=object),
    ],
)
def test_real_states_match_expanded_energy(q):
    i = np.array([0.1, -0.2])
    expected = (
        MODEL.L1_h * i[0] ** 2 / 2
        + MODEL.M_h * i[0] * i[1]
        + MODEL.L2_h * i[1] ** 2 / 2
        + 1 / (2 * MODEL.C1_f)
        + 4 / (2 * MODEL.C2_f)
    )
    assert MODEL.energy(q, i) == expected
    assert MODEL.energy(np.zeros(2), np.zeros(2)) == 0


@pytest.mark.parametrize(
    "model",
    [
        CoupledLC(1e-3, 1e-3, 10e-9, 10e-9, 0.3e-3),
        MODEL,
        replace(MODEL, R1_ohm=2.0, R2_ohm=5.0),
        replace(MODEL, M_h=0),
    ],
)
def test_independent_modal_energy_and_winding_controls(model):
    # Audit independently checks Cholesky modes against the analytic polynomial,
    # matrix energy identity, signed forced work, poles and winding covariance.
    report = audit_case("pytest", model)
    assert report["winding_reversal_frequency_and_state_covariance"] == "passed"


def test_equal_normal_coordinates_and_decoupled_limit():
    symmetric = CoupledLC(1e-3, 1e-3, 10e-9, 10e-9, 0.3e-3)
    roots, vectors = symmetric.numerical_modes()
    expected = [
        1 / (symmetric.C1_f * (symmetric.L1_h + symmetric.M_h)),
        1 / (symmetric.C1_f * (symmetric.L1_h - symmetric.M_h)),
    ]
    np.testing.assert_allclose(roots, expected, rtol=2e-14, atol=0)
    np.testing.assert_allclose(vectors[1] / vectors[0], [1, -1], rtol=2e-14, atol=0)
    decoupled = replace(MODEL, M_h=0)
    expected = sorted(
        [1 / (decoupled.L1_h * decoupled.C1_f), 1 / (decoupled.L2_h * decoupled.C2_f)]
    )
    np.testing.assert_allclose(decoupled.numerical_modes()[0], expected, rtol=2e-14, atol=0)
    assert decoupled.state_matrix()[2, 1] == decoupled.state_matrix()[3, 0] == 0
    near = replace(decoupled, M_h=1e-6 * math.sqrt(decoupled.L1_h * decoupled.L2_h))
    np.testing.assert_allclose(near.numerical_modes()[0], expected, rtol=3e-12, atol=0)


@pytest.mark.parametrize("port", ["q", "i"])
def test_finite_extreme_energy_raises_instead_of_returning_infinity(port):
    state = {"q": np.zeros(2), "i": np.zeros(2), port: np.array([1e308, 1e308])}
    with pytest.raises(ValueError, match="finite and resolved"):
        MODEL.energy(**state)


def test_reject_unrepresentable_derived_matrices_and_frequencies():
    with pytest.raises(ValueError, match="finite and resolved"):
        replace(MODEL, C1_f=np.nextafter(0.0, 1.0))
    extreme = CoupledLC(1e-300, 1e-300, 1e-300, 1e-300, 0.0)
    with pytest.raises(ValueError, match="finite and resolved"):
        extreme.analytic_omega_squared()
    with pytest.raises(ValueError, match="finite and resolved"):
        extreme.state_matrix()
    with pytest.raises(ValueError, match="finite and resolved"):
        extreme.numerical_modes()


def test_report_reproduces_archived_numerical_values():
    report = build_report()
    recorded = json.loads(
        (
            Path(__file__).parents[1] / "docs/experiments/coupled-lc-reference-summary.json"
        ).read_text()
    )
    assert report["case_count"] == 4
    assert report["invalid_input_cases_rejected"] == 13
    for key in ["symmetric_bare_frequency_hz", "symmetric_split_hz"]:
        assert report[key] == pytest.approx(recorded[key], rel=2e-13)
    for fresh, saved in zip(report["cases"], recorded["cases"], strict=True):
        assert fresh["parameters"] == saved["parameters"]
        for key in ["lossless_frequency_hz", "lossless_omega_squared_analytic"]:
            np.testing.assert_allclose(fresh[key], saved[key], rtol=2e-13, atol=0)
