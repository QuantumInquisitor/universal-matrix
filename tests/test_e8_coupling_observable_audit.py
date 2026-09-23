from __future__ import annotations

from src.e8_coupling_observable_audit import (
    ObservableCouplingStatus,
    admits_distinct_fixed_root_scalar_coupling,
    candidate_observable_audit,
    root_orbit_quadratic_invariants,
)


def test_e8_root_orbit_has_one_quadratic_invariant_value():
    assert root_orbit_quadratic_invariants() == (8.0,)


def test_matter_norm_couplings_are_classified_as_mass_parameter_shifts():
    ledger = {entry.observable: entry for entry in candidate_observable_audit()}
    for name in ("u1_matter_norm", "su2_matter_norm", "su3_matter_norm"):
        assert ledger[name].status is ObservableCouplingStatus.PARAMETER_RENORMALIZATION


def test_gauge_energy_coupling_is_only_a_coupling_rescaling_on_fixed_root_orbit():
    ledger = {entry.observable: entry for entry in candidate_observable_audit()}
    assert (
        ledger["gauge_energy_density"].status
        is ObservableCouplingStatus.PARAMETER_RENORMALIZATION
    )


def test_neutral_scalar_linear_coupling_is_only_a_source_shift_on_fixed_root_orbit():
    ledger = {entry.observable: entry for entry in candidate_observable_audit()}
    assert (
        ledger["neutral_reciprocity_or_content_scalar"].status
        is ObservableCouplingStatus.SOURCE_SHIFT
    )


def test_no_audited_fixed_root_scalar_coupling_is_promoted_as_new_e8_dynamics():
    assert not admits_distinct_fixed_root_scalar_coupling()


def test_orientation_sensitive_effect_requires_new_e8_structure():
    ledger = {entry.observable: entry for entry in candidate_observable_audit()}
    assert (
        ledger["e8_orientation_sensitive_effect"].status
        is ObservableCouplingStatus.REQUIRES_NEW_E8_DEGREE
    )
