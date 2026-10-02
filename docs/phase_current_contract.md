# Mechanical phase and gauge current: comparison contract

The circle/phase work in PR #137 measures modal phase and endpoint mechanical
power. The existing U(1) matter sector computes a gauge-invariant charge current.
This audit makes their conservation and symmetry differences executable before
attempting a fitted or physical bridge. All underlying equations are unchanged.

## Conserved quantities and units

With powers positive into each module, connector energy satisfies
`dU/dt + P_parent + P_child = 0`. Both powers can be negative while the connector
stores energy. By comparison an oriented gauge link current satisfies
`J_ab = -J_ba` and the lattice charge satisfies `rho_dot = -div J`.

Mechanical power is measured in synthetic SI watts (J/s). The gauge adapter has
model charge and model time units, without an independently supplied conversion
to amperes. Setting a plotted value of one equal to one in the other sector would
not establish dimensional or physical equivalence. A watts-to-amperes bridge
would additionally need an independently specified energy-per-charge scale and
compatible charge/time normalization. None is selected here.

## Explicit storage allocation

For comparison of symmetry alone, define `S = -(P_parent + P_child)` and
`T = (P_child - P_parent)/2`. Then

- `P_parent = -T - S/2`
- `P_child = T - S/2`

Exchanging endpoints reverses T and preserves S. This splits storage equally
between endpoint accounts; it is a bookkeeping convention, not a unique physical
energy-current definition. It does not modify forces or allocate charge. More
generally a chosen fraction a gives `T_a = P_child + (1-a)*S`; without a physical
allocation rule, different choices differ by storage terms. T is therefore not
automatically identified with the gauge current.

## Phase and gauge contracts

The mechanical diagnostic uses `atan2(-modal_rate/omega, modal_displacement)`;
phase is undefined below its existing amplitude floor. The gauge phase is
`phi_target - phi_source + theta_link`. Local changes of site phases require
the compensating link change `theta -> theta + alpha_source - alpha_target`.
Using only the phase difference after local transformations changes the current.

No sign flips, arbitrary phase offsets, amplitude rescaling or conversion factor
are fitted. Five fixed phase differences and both target polarities are tested
with the actual gauge-current implementation. A deliberately missing link
transformation serves as a negative control.

## Reproduction and acceptance

Run `python -m scripts.report_phase_current_contract --output artifacts/phase-current/report.json`
and `python -m pytest tests/test_phase_current_contract.py tests/test_gauge_matter.py tests/test_fold_recursive_phase_power.py`.

Twelve mechanical fixtures cover three 1:2 size pairs and stationary/moving
endpoints. Three finite-difference steps independently check storage derivatives.
The acceptance limits were fixed before execution: healthy power
balance <1e-10 W; wrong child sign >1e-8 W for both-moving fixtures; gauge and
orientation errors <1e-12 model-current units; omitted-link error >0.1 in at least
one fixture. These are diagnostic controls, not manufacturing tolerances.

The report records source hashes normalized to UTF-8/LF for reproducibility
across operating systems. Existing gauge tests also cover periodic charge
continuity and the sourced Gauss constraint. No full recursive trajectory is
rerun and no physical cross-sector adapter or plasma model is validated.

## Next gate

Any proposed physical adapter must supply its state map, conserved quantity,
units, energy-per-charge scale, link connection and storage allocation before
comparison. Until then, compare symmetry/accounting contracts separately and
preserve failed controls. Viewer work may display both sectors with distinct
units and provenance; it must not label mechanical power as electric current.
