# Directed phase transport controls

This optional, dimensionless experiment tests a mechanism that can favor one circulation direction: unequal forward/backward neighbor response. It is a constructed alternative model, not a measurement of time as energy, material dynamics, or the whole breathing assembly.

## Model and independently checkable predictions

On a periodic N-node ring let e_i be phase error relative to an explicitly encoded target pattern, d_i=e_(i+1)-e_i, and K >= 0. Set

    V = sum_i K (1-cos(d_i))
    F_i = K (sin(d_i)-sin(d_(i-1))) = -partial_i V
    H_i = eta K (sin(d_i)+sin(d_(i-1)))
    velocity_i = F_i + H_i

The forward and backward response coefficients are K(1+eta) and K(1-eta), respectively; |eta| <= 1 keeps both nonnegative. Eta=0 recovers the reciprocal baseline exactly. Nonzero eta is an imposed constitutive choice; the ring does not invent handedness spontaneously.

With unit dimensionless mobility, the model work rate is sum H_i velocity_i and dissipation rate is sum velocity_i^2. Thus

    dV/dt = model_work_rate - model_dissipation_rate.

For this specific uniform ring, sum F_i H_i = eta K^2 sum(sin(d_i)^2-sin(d_(i-1))^2)=0. Consequently dV/dt=-sum F_i^2 <= 0 even when eta is nonzero. Positive work in this bookkeeping is balanced by additional dissipation; it is not energy produced by time. A physical interpretation requires an actuator/bath, units, mobility, and a measured constitutive law, all absent here. Other nonreciprocal graphs need not satisfy this telescoping identity.

For a small Fourier perturbation with q=2pi/N, linearization predicts eigenvalue -2K(1-cos(q)) + i 2 eta K sin(q). Its complex Fourier angle should propagate at 2 eta K sin(q); eta sign reverses transport and eta=0 has no angular transport. All runs advance positive time. Opposite transport direction is not reversal of dissipative time evolution.

## Executable controls and results

The reporter runs 36 cases: N=8/16/24, coupling off/on, eta=-0.5/0/+0.5, and perturbation amplitudes 0.001/0.2. A sinusoidal error is initialized explicitly. There is no special claim for 16 nodes. Each record contains initial/final errors, a trace, integrated work/dissipation, and the analytic small-amplitude rate. Model work and dissipation use the same RK4 stages as the state update.

The accompanying tests independently check the potential directional derivative, telescoping cancellation, exact baseline reduction, spatial reflection under eta sign reversal, coupling-off immobility, small-amplitude prediction, numerical balance, time-step convergence and observability limits. All 13 tests pass. Halving dt from 0.05 to 0.025 reduces the default balance residual from 8.22e-11 to 5.17e-12, with maximum final error-coordinate difference 2.72e-10. These are numerical checks, not experimental evidence for a physical substrate.

Phase unwrapping is restricted to this resolved benchmark regime: initial amplitude must be above 1e-12 and at most 0.5 radians, and dt*K must be at most 0.1. These are conservative numerical restrictions, not a general nonlinear stability theorem. Once the normalized Fourier amplitude drops to 1e-12 or below, the accumulated angle and full-interval measured rate become unavailable (`null`), and the first unobservable time is recorded. State integration and energy bookkeeping continue. The floor is a chosen numerical reporting threshold, not an instrument sensitivity. Tiny input and long-decay tests prevent interpreting a vanished mode's angle as a measured transport direction.

Reproduce from repository root:

```text
python scripts/report_chiral_phase_controls.py --output docs/experiments/chiral-phase-controls-summary.json
python -m pytest tests/test_chiral_phase_controls.py -q
```

The JSON includes a normalized-text SHA-256 of its standalone standard-library reporter. Remaining work includes noise/delay robustness, a realizable directional coupling mechanism and energy reservoir, linking phases to actual moving geometry, and determining whether any coupled material model develops autonomous sustained motion. Targets and signed couplings here are inputs, not discoveries of those mechanisms.

The committed JSON is a compact outcome snapshot with per-case traces omitted. Run the reporter with --output into artifacts to regenerate full traces.
