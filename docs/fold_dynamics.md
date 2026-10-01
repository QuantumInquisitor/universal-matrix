# Force-driven reduced folding

This experiment drives the existing 22-body geometry using generalized forces.
It uses the unchanged `report_fold_kinematics.kinematics(q)` map, its derivatives,
and its synthetic point-mass ownership. Coordinates are scale s and fold angle theta.
The declared rectangle is s in [0.9,1.1], theta in [0,pi/6].

The restoring potential is V=(q-q0)^T K(q-q0)/2, with q0=(1,pi/12),
K=[[.02,.002],[.002,.006]]. The positive definite synthetic stiffness includes
cross-coordinate restoring coupling. D=diag(.0004,.0001) is positive damping.
These values are modeling assumptions, not calibrated material constants.

M(q) qddot = Q(t) - D qdot - grad V - b(q,qdot), where
b_a=sum_i m_i J_ia dot H_i[qdot,qdot]. This coordinate-dependent inertia term is
essential: omitting it breaks the continuous energy identity. The stored energy
is E=qdot^T M qdot/2+V; the ledger integrates external work Q dot qdot and loss
qdot^T D qdot. Therefore E-E_initial-work+loss should approach zero as the
numerical step shrinks. No term treats time itself as an energy supply.

Time is in seconds, positions in meters, masses in kilograms, energy in joules.
The scale force has units joules per unit scale and the angle force joules per
radian; stiffness and damping entries carry the corresponding coordinate units.
Q(t)=drive*[1e-4 sin(2t),4e-5 cos(2t)]. The drive-off case multiplies this by a
sin-squared envelope over the first second and zero thereafter, avoiding a force
jump at shutoff. Positive-time RK4 integrates q, rates, work and loss together.
Every derivative stage and accepted endpoint must stay within the rectangle;
the runner rejects violations without clipping. These checks do not certify
continuous collision clearance between stages.

The report covers equilibrium, conservative, damped, driven, drive-off and an
intentionally incorrect omitted-inertia control. Three time steps (.02,.01,.005 s)
over two seconds test refinement. Drive zero is the external-force-off control;
the restoring cross term is retained in all cases, so this is not a coupling
ablation study. Independent tests differentiate the mass matrix to construct
Christoffel terms and compare a finite directional energy derivative against
input-minus-loss power. The latter must fail detectably when b is omitted.

The report exports all 22 stable body IDs and sampled actual trajectory positions,
as well as normalized-text hashes of both model scripts. Driven and drive-off cases
also contain every accepted endpoint's coordinates and energy ledger for plotting.
This is not a restart file. Refinement differences retain each coordinate's own
units, without combining scale and angle into a mixed-unit norm. This reduction omits body rotational inertia,
distributed strain, material calibration and recursive whole-assembly coupling.
Damped drive-off relaxation is not autonomous sustained breathing.

Run `python scripts/report_fold_dynamics.py --output artifacts/fold-dynamics/report.json`.
The output directory is created and JSON rejects nonfinite values. The committed
summary is `docs/experiments/fold-dynamics-summary.json`.

The committed snapshot omits full endpoint traces to keep review manageable;
the reproduction command emits them. Generate the scientific figure with
`python scripts/plot_fold_dynamics.py --input artifacts/fold-dynamics/report.json
--output artifacts/fold-dynamics/motion-and-energy.png` (matplotlib required).
The plot verifies both model-source hashes before reading the stored results.
It performs no new integration and no curve fitting.

## Recorded result

The 18 runs (six cases at three step sizes) completed inside the admitted domain.
At .005 s steps the largest correct-model balance residual is 6.37e-17 J;
the intentionally omitted-b conservative case has 1.33e-7 J residual.
The independent directional derivative agrees with power to 5.57e-14 J/s;
omitting b gives a 1.11e-5 J/s discrepancy. The damped case falls from
6.1762e-6 J to 5.4463e-6 J over two seconds. The chosen sinusoidal forcing
extracts net work in this particular run; an external drive need not always add
energy. These numerical results validate the declared reduction and ledger,
not the synthetic material assumptions or real autonomous breathing.

## Exact passive-domain control

There is also a model-specific analytical check for the conservative and damped
unforced cases. Minimizing the quadratic potential over each boundary line
gives a lower bound for reaching the admitted rectangle's boundary. For the
scale boundaries it is
`(Kss-Kst^2/Ktt)*(0.1)^2/2 = 9.6666667e-5 J`.
For the angle boundaries it is
`(Ktt-Kst^2/Kss)*(pi/12)^2/2`, which is larger. Minimizing over the entire
boundary line instead of just its admissible segment makes these valid lower
bounds. The default initial energy is only `6.17618e-6 J`.

Because kinetic energy is nonnegative and total energy cannot increase in the
exact unforced/damped equations, those exact trajectories cannot reach the
boundary. This deduction assumes the declared restoring/damping laws; it is
not a measured strain limit or a certificate for driven numerical trajectories.
