from src.matter_branch_scan import (
    BranchPoint,
    converged_nodeless,
    lowest_energy_per_charge,
    stable_candidates,
)


def _point(
    amplitude,
    *,
    status=0,
    nodeless=True,
    eq=1.1,
    stable=False,
):
    return BranchPoint(
        central_amplitude=amplitude,
        omega=0.9,
        solver_status=status,
        nodeless=nodeless,
        energy=10.0,
        charge=10.0 / eq,
        energy_per_charge=eq,
        below_free_mass_threshold=stable,
        solver_message="test",
    )


def test_filters_converged_nodeless_branch_points():
    points = [
        _point(0.3),
        _point(0.4, status=1),
        _point(0.5, nodeless=False),
    ]
    kept = converged_nodeless(points)
    assert [p.central_amplitude for p in kept] == [0.3]


def test_stable_candidate_filter_is_explicit():
    points = [
        _point(0.3, eq=1.05, stable=False),
        _point(0.4, eq=0.95, stable=True),
    ]
    stable = stable_candidates(points)
    assert len(stable) == 1
    assert stable[0].central_amplitude == 0.4


def test_lowest_energy_per_charge_ignores_failed_points():
    points = [
        _point(0.3, eq=1.02),
        _point(0.4, status=1, eq=0.2),
        _point(0.5, eq=0.98, stable=True),
    ]
    best = lowest_energy_per_charge(points)
    assert best is not None
    assert best.central_amplitude == 0.5


def test_lowest_energy_per_charge_returns_none_without_valid_points():
    assert lowest_energy_per_charge(
        [_point(0.2, status=1)]
    ) is None
