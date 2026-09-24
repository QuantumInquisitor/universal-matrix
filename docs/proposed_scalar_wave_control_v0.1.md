# Proposed scalar standing-wave control v0.1

## Working hypothesis

This is **our M4-inspired working hypothesis**, formulated here to make the
standing-wave suggestion testable. The equation is not attributed to an
original M4 author. It is an optional, synthetic linear onset experiment;
it does not fit a Higgs mass, identify particles, or model nonlinear
saturation. The distinction between the supplied claims and verified
sources remains in [the M4 source audit](m4_source_and_claim_audit_v0.1.md).

As motivation, the primary experiment
[Drifting Faraday patterns under localised driving](https://www.nature.com/articles/s42005-023-01170-8)
studies driven fluid-surface patterns. That supports studying parametric
forcing as a physical mechanism. The present ring equation, parameters,
dispersion, and scale transformation are our declarations, not values
extracted from that experiment.

For arc coordinate ell on a periodic ring of circumference L, take one
real mode u(ell,t) = q(t) cos(2 pi n ell / L). For n >= 1 this is a standing
spatial profile; n = 0 is the uniform mode and requires a nonzero gap.
The degenerate sine profile obeys the same declared equation. We propose

```text
q'' + 2 gamma q' + omega_n^2 [1 + h cos(Omega t)] q = 0
omega_n^2 = omega_gap^2 + (2 pi v n / L)^2
```

| Parameter | Meaning and units | Domain |
| --- | --- | --- |
| q | Modal displacement, m | Real; amplitude is arbitrary in this linear model |
| L | Ring circumference, m | Positive |
| v | Wave speed, m/s | Positive |
| n | Integer spatial mode number | Nonnegative |
| omega_gap | Prescribed gap angular frequency, rad/s | Nonnegative |
| gamma | Amplitude damping rate, 1/s | Nonnegative |
| h | Fractional modulation of stiffness, dimensionless | 0 <= h < 1 |
| Omega | Drive angular frequency, rad/s | Positive |

The derived omega_n must be positive and numerically resolved. All inputs
and derived numerical scales must be finite. The h constraint keeps
instantaneous stiffness positive. Growth can still occur because varying
the stiffness supplies work; a negative instantaneous stiffness is not
required. These frequencies are angular frequencies, not cycles per second.

## Computation and independent identities

`src/proposed_scalar_wave_control.py` integrates the 2 by 2 fundamental
matrix over one drive period T = 2 pi / Omega using classical RK4.
The initial matrix is the identity at drive phase zero. Computation uses
phase phi = Omega t and normalized velocity q'/omega_n to reduce unit
conditioning; the returned monodromy acts on physical coordinates (q,q').

The eigenvalues of that matrix are the Floquet multipliers. Their largest
magnitude rho > 1 indicates a growing linear solution; rho < 1 indicates
asymptotic decay over repeated drive periods. The dimensional growth rate
is log(rho)/T. These statements concern the exact equation; numerical
decisions near rho = 1 require additional refinement and are not certified
by a single run. Transient amplification and the initial state's projection
onto each Floquet mode are separate questions.

The implementation rejects nonzero damping when 2 gamma T / N is at or
below float64 machine epsilon: such a per-step decay can disappear in
roundoff and falsely return zero growth even when the exact rate is
negative. An unresolved-scale rejection is not a stability result.
This narrow guard does not replace refinement or provide a full error bound.

Liouville's identity gives the independent exact check

```text
det M(T) = exp(-2 gamma T).
```

That identity alone does not check phase accuracy. For h = 0, tests also
compare the entire monodromy with the analytic damped-oscillator matrix
exponential in the undamped, underdamped, critical, and overdamped cases.
An unmodulated refinement test checks fourth-order matrix convergence.

For a trajectory, energy and work are **per unit effective modal mass**,
in m^2/s^2. No measured modal mass is assumed:

```text
E = 1/2 q'^2 + 1/2 omega_n^2 [1 + h cos(Omega t)] q^2
dE/dt = -2 gamma q'^2 - 1/2 h omega_n^2 Omega sin(Omega t) q^2
loss = integral 2 gamma q'^2 dt
drive_work = integral -1/2 h omega_n^2 Omega sin(Omega t) q^2 dt
balance_residual = E_final - E_initial - drive_work + loss.
```

The work and loss are accumulated from the local powers using RK4 stages;
they are not defined from the measured energy change. This supplies a
separate balance check within the same integrator, not an independent
solver. Work can have either sign; damping loss is nonnegative for the
exact trajectory. The initial state, final state, and reported energy
quantities must remain finite.

## Synthetic onset experiment

Choose L = 2 pi m, v = 1 m/s, n = 1, omega_gap = 0, gamma = 0.02 /s,
and h = 0.2. Then omega_n = 1 rad/s. The following computations use N
steps per drive period. Energy residuals use eight periods with
q(0) = 1 m and q'(0) = 0 m/s; determinant checks use one period.
Figures below are numerical outputs, not physical measurements.

| Omega / omega_n | N | Largest multiplier magnitude | Absolute determinant error | Absolute energy balance residual, m^2/s^2 |
| --- | --- | --- | --- | --- |
| 1.5 | 256 | 0.919637412126 | 3.683e-10 | 5.181e-10 |
| 1.5 | 512 | 0.919637411939 | 2.498e-11 | 3.976e-11 |
| 1.5 | 1024 | 0.919637411927 | 1.622e-12 | 2.711e-12 |
| 2.0 | 256 | 1.098654725389 | 9.473e-11 | 3.196e-11 |
| 2.0 | 512 | 1.098654725496 | 6.294e-12 | 9.162e-13 |
| 2.0 | 1024 | 1.098654725503 | 4.050e-13 | 1.464e-13 |
| 2.5 | 256 | 0.950976923311 | 3.254e-11 | 1.034e-10 |
| 2.5 | 512 | 0.950976923295 | 2.137e-12 | 6.852e-12 |
| 2.5 | 1024 | 0.950976923294 | 1.353e-13 | 4.428e-13 |

At drive ratio 2 the refined growth rate is about 0.029948648637 /s.
At ratios 1.5 and 2.5 it is about -0.02 /s. Removing modulation gives
-0.02 /s, and increasing gamma to 0.08 /s suppresses growth at ratio 2.
These are three tested frequencies and two controls, not a complete
stability diagram or a threshold estimate.

For the resonant trajectory at N = 1024, energy rises from 0.6 to
1.250065401885 m^2/s^2. Drive work is 1.291346929633 m^2/s^2 and damping
loss is 0.641281527748 m^2/s^2. Thus growth is powered by the imposed
drive. The balance residual decreases on refinement; cancellation over
complete periods can make that residual converge faster than the state
error, so it is not used to claim the trajectory has the same precision.

## Scale hypothesis and its negative control

For positive s, explicitly transform

```text
L_new = s L; t_new = s t; v_new = v; n_new = n; h_new = h
omega_gap_new = omega_gap/s
gamma_new = gamma/s; Omega_new = Omega/s
q_new(t_new) = q(t_new/s).
```

Then omega_n_new = omega_n/s. At fixed displacement amplitude the
velocity scales by 1/s, T scales by s, and the physical monodromy obeys
M_new = D M D^-1 with D = diag(1,1/s). Multipliers remain the same,
growth rates scale by 1/s, and all energies, drive work, and damping loss
scale by 1/s^2. Multiplying q_new by any constant a is a separate linear
amplitude freedom, multiplying those energy quantities by a^2; the test
uses a = 1 rather than assuming an amplitude law from ring size.

Tests exercise s = 0.2, 3, and 100 with a nonzero gap. This is an exact
similarity of the proposed equation under the stated joint transform.
It is not evidence that real systems at different scales automatically
have the required damping, gap, and drive frequencies.

The negative control starts with omega_gap = 0.75 rad/s, giving
omega_n = 1.25 rad/s, and Omega = 2.5 rad/s. Scaling L by 3 and damping
and drive rates by 1/3 **while keeping the gap fixed** gives
omega_n = sqrt((1/3)^2 + 0.75^2), which is not 1.25/3. In this tested
case the original mode grows and the fixed-gap scaled mode decays.
Changing geometry alone does not establish scale invariance; the gap
introduces a frequency scale that must also transform for this hypothesis.

## Reproduction and next discriminating step

```python
import math
from src.proposed_scalar_wave_control import RingMode, floquet_audit, energy_audit

for ratio in (1.5, 2.0, 2.5):
    mode = RingMode(2 * math.pi, 1, 1, 0, 0.02, 0.2, ratio)
    for steps in (256, 512, 1024):
        print(ratio, steps, floquet_audit(mode, steps=steps))
        print(energy_audit(mode, steps=steps, periods=8))
```

Run `python -m pytest tests/test_proposed_scalar_wave_control.py -q`.
There are no changes to the toroidal geometry, core evolution, reference
frequency catalog, or microplane constitutive laws. No recursive hierarchy,
coupling between spatial modes, nonlinear saturation, quantization, or
particle identification has been implemented here.

The next focused extension would measure the onset boundary as modulation
and detuning vary, then introduce one explicitly chosen nonlinear term
only if saturation is the next proposed observable. A physical comparison
would additionally require a specified medium, parameter estimates, and
observations with uncertainties. The present result already tests the
working hypothesis's onset, energy supply, and conditional scale symmetry.
