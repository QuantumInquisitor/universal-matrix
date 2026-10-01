# Geometry-derived material forces in motion

The existing 22-body reduced integrator now accepts an explicit constitutive
potential as an alternative to its historical quadratic law. The default stays
quadratic. The selected potential supplies both stored energy and its analytic
negative gradient; the two restoring laws are never added together.

For q=(scale, angle), the equation is

`M(q) qddot + b(q,qdot) + grad U(q) + D qdot = applied force`.

M and the geometric inertial bias b retain the existing one-owner-per-body
point masses. U comprises six membrane and twelve axial bridge contributions
at the corrected reference q=(1,pi/12). Four hubs still have mass but no
constitutive energy. Synthetic defaults are E=1000 Pa, nu=0.3, effective
reference thickness=0.1 mm, bridge EA=0.1 N and reference length unit=0.1 m.
These are exploratory parameters, not calibrated material measurements.

The independently integrated work and damping loss check
`kinetic + potential - initial energy - work + loss = 0`.
A directional finite-difference energy derivative checks the force/energy
identity, including an intentionally omitted inertial-bias negative control.

## Reproduce

```sh
uv run python scripts/report_fold_material_dynamics.py --output artifacts/fold-material-dynamics/report.json
uv run python -m pytest tests/test_fold_dynamics.py tests/test_fold_constitutive.py tests/test_fold_constitutive_dynamics.py
```

The report runs equilibrium, conservative, passive, driven and drive-shutoff
controls over 0.4 seconds with three step sizes (0.01, 0.005, 0.0025 seconds).
Saved source hashes and explicit potential labels make the model reproducible.
Trajectory samples represent integrated physical model time, rather than the
prescribed phase samples in the earlier geometry overlay.

This checkpoint does not provide distributed panel rotational inertia, bending,
hub/joint stiffness, contact forces, a continuous collision certificate, measured
material coefficients, a finite power supply or a stable autonomous cycle.
The separate 69-domain flow assembly and the XR viewer are not integrated here.
Existing coupled/reservoir experiments retain their historical potential until
an explicit model choice and compatible energy account are added there.

## Validation checkpoint

61 tests passed (12 new, 16 historical dynamics, 33 constitutive). At the
0.01-second step, the conservative balance residual over 0.4 seconds was
2.86e-15 J; passive and driven residuals were 1.19e-15 and 1.14e-15 J.
The independent directional energy-rate error was 1.23e-13 J/s, while
omitting geometric inertial bias produced 1.11e-5 J/s error. These are
numerical consistency results for this declared short-duration model.
