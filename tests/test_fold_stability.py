"""Short independent checks for rebased checkpoint continuation."""

import json

import numpy as np
import pytest

from scripts import report_fold_stability as m
from scripts.report_fold_scaling import scaled_mechanical


def state():
    return m.load_seed()[0]


def test_rebase_preserves_dynamics_and_zeroes_every_ledger():
    y = state()
    z, energy = m.prepare(y)
    assert energy == 0
    np.testing.assert_array_equal(m.rhs(y), m.rhs(z))
    np.testing.assert_array_equal(z[:36].reshape(4, 9)[:, 5:], 0)
    np.testing.assert_array_equal(z[36:], 0)


def test_kick_energy_independent_quadratic():
    y = state()
    z, kick = m.prepare(y, 1.01)
    kinetic = 0.0
    for b, s in zip(y[:36].reshape(4, 9), m.BASE_SIZES, strict=True):
        mass = scaled_mechanical(b[:2], b[2:4], s)[0]["mass_matrix"]
        kinetic += 0.5 * b[2:4] @ mass @ b[2:4]
    assert kick == pytest.approx((1.01**2 - 1) * kinetic, rel=2e-12)
    np.testing.assert_array_equal(y[:36].reshape(4, 9)[:, 4], z[:36].reshape(4, 9)[:, 4])


@pytest.mark.parametrize("kind", ["hash", "inventory", "time", "state"])
def test_seed_tamper(tmp_path, kind, monkeypatch):
    data = json.loads(m.SEED.read_text())
    if kind == "hash":
        data["sources"]["report_fold_supply.py"] = "0" * 64
    if kind == "inventory":
        data["sources"].pop("report_fold_supply.py")
    if kind == "time":
        data["cases"]["powered"]["termination"]["last_accepted_time_s"] = 19
    if kind == "state":
        data["cases"]["powered"]["final_state"][0] = float("nan")
    p = tmp_path / "seed.json"
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="content hash"):
        m.load_seed(p)
    monkeypatch.setattr(m, "SEED_SHA256", m.text_hash(p))
    with pytest.raises(ValueError):
        m.load_seed(p)


def test_group_account_derivative_finite_difference():
    y, _ = m.prepare(state())
    d = m.rhs(y)
    layout = m.compile_hierarchy(4, m.EDGES, m.TREE)

    def account(z):
        return np.array(
            [
                v["accounted_energy_j"] - v["boundary_work_j"] - sum(z[44:][layout["groups"][p]])
                for p, v in m.measure(z[:44], m.BASE_SIZES, m.EDGES, layout)[3].items()
            ]
        )

    h = 1e-5
    np.testing.assert_allclose((account(y + h * d) - account(y - h * d)) / (2 * h), 0, atol=1e-14)


def test_short_rk4_agreement_and_dense_sample():
    y, _ = m.prepare(state())
    z = y.copy()
    h = 0.002
    for _ in range(25):
        a = m.rhs(z)
        b = m.rhs(z + h * a / 2)
        c = m.rhs(z + h * b / 2)
        d = m.rhs(z + h * c)
        z += h * (a + 2 * b + 2 * c + d) / 6
    run = m.simulate(y, 0.05)
    np.testing.assert_allclose(run["final_state"], z, atol=1e-10, rtol=1e-8)
    assert max(run["max_group_residual_j"].values()) < 1e-12
    assert not run["late_window"]["complete"]
    assert run["late_window"]["covered_physical_interval_s"] is None
    sample = m.simulate(y, 0.51, max_step=0.1)["samples"]
    assert [r["time_s"] for r in sample] == [0, 0.25, 0.5, 0.51]
    assert m.compare(run, run)["maximum_mechanical_difference_j"] == 0


@pytest.mark.parametrize(
    "reason", ["negative reservoir: injected", "outside declared scope: injected"]
)
def test_known_stage_rejection_retains_last_accepted(monkeypatch, reason):
    y, _ = m.prepare(state())
    original = m.rhs
    calls = 0

    def injected(*a, **kw):
        nonlocal calls
        calls += 1
        if calls > 20:
            raise ValueError(reason)
        return original(*a, **kw)

    monkeypatch.setattr(m, "rhs", injected)
    run = m.simulate(y, 0.1, max_step=0.01)
    assert run["termination"]["status"] == "scope_termination"
    assert 0 < run["termination"]["last_accepted_time_s"] < 0.1
    assert run["samples"][-1]["time_s"] == run["termination"]["last_accepted_time_s"]
    np.testing.assert_array_equal(run["samples"][-1]["input_j"], run["final_state"][44:])


def test_unknown_errors_propagate(monkeypatch):
    y, _ = m.prepare(state())
    original = m.rhs
    calls = 0

    def injected(*a, **kw):
        nonlocal calls
        calls += 1
        if calls > 2:
            raise ValueError("unexpected defect")
        return original(*a, **kw)

    monkeypatch.setattr(m, "rhs", injected)
    with pytest.raises(ValueError, match="unexpected"):
        m.simulate(y, 0.1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": 41},
        {"duration": True},
        {"max_step": 0},
        {"rtol": 0},
        {"power_density": -1},
    ],
)
def test_invalid(kwargs):
    y, _ = m.prepare(state())
    with pytest.raises(ValueError):
        m.simulate(y, **kwargs)


def historical_modules():
    """Execute exact seed-era sources; override links with their old counterparts."""
    manifest = json.loads(m.COMPATIBILITY.read_text(encoding="utf-8"))
    modules = {}
    for short in ("dynamics", "reservoir", "coupling"):
        name = f"report_fold_{short}.py"
        entry = manifest["source_transitions"][name]
        path = m.ROOT / entry["historical_snapshot"]
        assert m.text_hash(path) == entry["historical_sha256"]
        namespace = {"__name__": f"scripts._historical_{short}", "__package__": "scripts"}
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
        if short in ("reservoir", "coupling"):
            namespace["mechanical"] = modules["dynamics"]["mechanical"]
        if short == "coupling":
            namespace["reservoir_rhs"] = modules["reservoir"]["rhs"]
        modules[short] = namespace
    return modules


def test_reviewed_defaults_match_exact_historical_sources():
    from scripts import report_fold_coupling as coupling
    from scripts import report_fold_dynamics as dynamics
    from scripts import report_fold_reservoir as reservoir

    old = historical_modules()
    # Bounded regression probes, not a claim of global formal equivalence.
    for index in range(9):
        q = dynamics.Q0 + np.array((0.003 * (index - 4), -0.004 * (index - 4)))
        v = np.array((0.002 * index, -0.003 * (index - 3)))
        y = np.r_[q, v, 0.0, 0.0]
        np.testing.assert_allclose(
            dynamics.mechanical(q, v)[2],
            old["dynamics"]["mechanical"](q, v)[2],
            atol=2e-18,
            rtol=2e-14,
        )
        np.testing.assert_allclose(
            dynamics.rhs(0.3, y), old["dynamics"]["rhs"](0.3, y), atol=1e-15, rtol=2e-14
        )
        block = np.r_[q, v, index * 1e-6, 0.0, 0.0, 0.0, 0.0]
        np.testing.assert_allclose(
            reservoir.rhs(block), old["reservoir"]["rhs"](block), atol=1e-15, rtol=2e-14
        )
        pair = np.r_[block, np.r_[dynamics.Q0, 0.0, 0.0, 1e-5, 0.0, 0.0, 0.0, 0.0], 0, 0]
        np.testing.assert_allclose(
            coupling.rhs(pair), old["coupling"]["rhs"](pair), atol=1e-15, rtol=2e-14
        )
        np.testing.assert_allclose(
            coupling.measure(pair)[0],
            old["coupling"]["measure"](pair)[0],
            atol=2e-18,
            rtol=2e-14,
        )
    np.testing.assert_allclose(
        coupling.simulate(duration=0.04, dt=0.01)["final_state"],
        old["coupling"]["simulate"](duration=0.04, dt=0.01)["final_state"],
        atol=1e-15,
        rtol=2e-14,
    )


def test_seed_keeps_historical_and_current_provenance_separate():
    _, provenance, current = m.load_seed()
    historical = json.loads(m.SEED.read_text(encoding="utf-8"))["sources"]
    assert provenance["normalized_utf8_sha256"] == m.SEED_SHA256
    assert provenance["historical_sources"] == historical
    assert provenance["current_sources"] == current
    assert current != historical
    assert provenance["compatibility"]["normalized_utf8_sha256"] == m.COMPATIBILITY_SHA256
    assert current == {name: m.text_hash(m.ROOT / "scripts" / name) for name in historical}


@pytest.mark.parametrize(
    "target",
    [
        "report_fold_dynamics.py",
        "report_fold_reservoir.py",
        "report_fold_coupling.py",
        "report_fold_supply.py",
        "report_fold_kinematics.py",
    ],
)
def test_unreviewed_source_changes_still_rejected(monkeypatch, target):
    original = m.text_hash

    def altered(path):
        return "0" * 64 if path == m.ROOT / "scripts" / target else original(path)

    monkeypatch.setattr(m, "text_hash", altered)
    with pytest.raises(ValueError, match="source hash mismatch"):
        m.load_seed()


def test_compatibility_manifest_cannot_authorize_itself(tmp_path, monkeypatch):
    data = json.loads(m.COMPATIBILITY.read_text(encoding="utf-8"))
    data["scope"] = "tampered"
    path = tmp_path / "compatibility.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(m, "COMPATIBILITY", path)
    with pytest.raises(ValueError, match="manifest hash mismatch"):
        m.load_seed()


def test_historical_snapshot_tamper_rejected(monkeypatch):
    original = m.text_hash

    def altered(path):
        return "0" * 64 if path.name == "report_fold_dynamics.py.txt" else original(path)

    monkeypatch.setattr(m, "text_hash", altered)
    with pytest.raises(ValueError, match="historical source snapshot mismatch"):
        m.load_seed()
