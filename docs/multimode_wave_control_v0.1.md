# Two-mode wave coupling and competition control

Local numerical experiment, 30 September 2026. This advances the W1 multimode
gate with a declared, reproducible two-mode Galerkin model. It is independent
of the proposed time-crystal subsystem and does not establish material behavior.

## Model and physical scope

For a ring of circumference 2 pi metres, keep the degenerate spatial modes
`u(x,t) = q1(t) cos(x) + q2(t) sin(x)`. Project a local cubic restoring
term `alpha*u^3` onto these two modes. Orthogonality gives

```text
q_i'' + 2 gamma q_i' + omega^2 [1+h cos(Omega t)] q_i
      + beta q_i (q_i^2 + c q_j^2) = 0,
beta = 3 alpha / 4; c = 1 for the projected local cubic model.
```

Both amplitudes evolve from their initial states. Base scales match the prior
single-mode control: omega=1 rad/s, gamma=.02/s, h=.2, Omega=2 rad/s,
alpha=4/3 m^-2 s^-2. Seed amplitudes are (.01,.007) metres with zero velocity.
The `c=0` comparison removes cross coupling, producing two independent cubic
oscillators. It is deliberately not claimed to represent the same local PDE.

This is a truncation: the cubic field also generates spatial third harmonics,
which are omitted. The calculation tests sharing between two degenerate basis
modes, not competition across all wavelengths or convergence of a spatial PDE.

The model's O(2) symmetry predicts a major limitation before computation:
for collinear initial position and velocity, direction in the `(q1,q2)` plane
is preserved. Changing the seed direction changes the orientation of the
standing-wave pattern. A zero seed in one mode remains exactly zero. This
model cannot select a unique spatial orientation from an exactly symmetric
configuration. Simulated saturation must not be described as unique pattern
selection.

## Energy and numerical controls

With unit modal masses, define energy in m^2/s^2:

```text
E = (v1^2+v2^2)/2 + k(t)(q1^2+q2^2)/2
    + beta(q1^4+q2^4)/4 + beta*c*q1^2*q2^2/2.
k(t) = omega^2 [1+h cos(Omega t)]
dE/dt = k'(t)(q1^2+q2^2)/2 - 2 gamma(v1^2+v2^2).
```

Pump work and damping loss are integrated as additional states and compared
against energy reconstructed from positions and velocities. This is accounting
for this two-mode control only, not the full folding structure's energy model.
When `c=1`, modal angular momentum `q1*v2-q2*v1` obeys
`L(t)=L(0) exp(-2 gamma t)`, even with parametric driving. No pump and no
damping conserve both energy and angular momentum.

DOP853 runs for 400 drive periods with maximum step T/32 and relative/absolute
tolerances 1e-9/1e-11. Controls include T/64 with 1e-11/1e-13 tolerances,
800-period duration, a rotated seed, a single-mode seed, halved nonlinearity,
and no pump. Reported amplitudes are RMS of `(q_i,v_i/omega)` over the final
128 stroboscopic samples; they are not time-averaged physical displacement RMS.

Twelve tests cover analytic cubic projection by independent spatial quadrature,
agreement with the existing independent oscillator integrator, conserved energy,
the damped angular momentum law, pump/dissipation balance, radial reduction,
zero-mode invariance and invalid inputs.

## Reproduce and remaining gates

```text
uv run python scripts/report_multimode_wave_control.py
uv run python -m pytest -q -p no:cacheprovider tests/test_proposed_multimode_wave_control.py
```

Results and source hashes are in `artifacts/waves/multimode-wave-control.json`; the
companion summary is `artifacts/waves/multimode-wave-result.md`. This bounded experiment
does not close W1: independent spatial mode-count refinement including generated
harmonics, several wavelength families, explicit symmetry-breaking or noise
ensembles, finite boundaries and empirical coupling remain. It also does not
complete material forces, emergent whole-structure motion or recursive coupling.
