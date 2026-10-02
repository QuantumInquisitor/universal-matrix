# Distributed panel and bridge inertia

This isolated P07 audit replaces the location of each synthetic body mass with
an explicitly declared reference distribution. Existing point-mass dynamics,
potential, collision geometry and production solvers are unchanged.

Each of six panels owns its original 0.1 kg, uniformly distributed over its
reference coefficient polygon. Each of twelve bridges owns its original
0.005 kg uniformly along its centerline. Each of four hubs remains a 0.02 kg
point mass. Total mass is still 0.74 kg. These are synthetic assignments, not
density integration over overlapping solid envelopes or measured materials.

The affine material map is the existing `x=length*s*sum(c_i*r_i(theta))`.
The polygon is triangulated and integrated with a degree-two triangle rule;
bridge lines use two-point Gauss quadrature. Since the map and its q derivatives
are linear in c, this exactly integrates kinetic energy for these distributions
up to floating-point arithmetic. Reference weights stay fixed as the body
deforms, preserving mass. No current-area mass renormalization is used.

The generalized mass and geometric bias are
`M_ab=sum(m_n*J_na dot J_nb)` and
`b_a=sum(m_n*J_na dot H_n[v,v])`.
Tests independently compare polygon boundary-integral moments, rod moments,
finite-difference position/Jacobian derivatives and conservative energy rate.
Omitting the bias produces a detectable energy-rate error.

Mass-weighted body-centroid inertia omits a positive-semidefinite covariance
term from within-body motion. The historical panel lump uses a vertex mean,
not an area centroid, so no universal positive ordering against that historical
matrix is assumed. Both matrices are reported for comparison.

With all lengths halved and masses divided by eight, inertia scales by 1/32.
This is a declared homothetic control, not justification for fixed-thickness
physical scaling.

Reproduce with `python -m scripts.report_fold_distributed_inertia --output artifacts/distributed-inertia/report.json`
and `python -m pytest tests/test_fold_distributed_inertia.py tests/test_fold_kinematics.py`.

This advances panel/bridge distributed inertia only. Hub rotational inertia,
finite-thickness shell/solid inertia, joint/contact laws, calibration, a physical
mass partition and integration into trajectories remain open. The two-coordinate
reduction cannot establish stability of modes it excludes. P07 remains in progress.
