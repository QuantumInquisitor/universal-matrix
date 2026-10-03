# Bounded distributed-inertia graph trajectories

This optional report advances the existing instantaneous graph contract through
0.1 seconds for one module (depth 0) and three modules (depth 1, scales 1/.5/.5).
It reuses the declared distributed quadrature masses, constitutive membrane and
bridge laws, inertial bias, reciprocal mapped connector, and scale guards.
The existing point-model reports and production defaults are unchanged.

Run from the repository root:

```text
python -m scripts.report_fold_distributed_graph_trajectories --output artifacts/distributed-graph-trajectories.json
python -m pytest tests/test_fold_distributed_graph_trajectories.py tests/test_fold_distributed_graph.py -q
```

The report runs six cases: passive depths 0 and 1 at RK4 steps .001 and .0005 s,
conservative depth 1 at .0005 s, and disconnected depth 1 at .001 s. The initial
root is `Q0 + (.005,-.008)` with rates `(.002,.004)`; children start at `Q0` and
rest. All cumulative losses and endpoint works start at zero. No drive is added.
The conservative case switches off only the declared damping term.

The optional derivative evaluates each node's distributed mass matrix once per
stage; passive-stage tests compare it to the established graph derivative at
nonstationary connected and disconnected states. Forces, constitutive gradients,
inertial bias, and damping use the same scale and mass-matrix contract. The
reference is the existing DOP853 single-specimen solver with unchanged tolerances
(rtol 1e-10, atol 1e-13), explicitly matched initial conditions and 201 common
times. Graph loss index 4 maps to reference loss index 5; reference work index 4
is zero and is not compared as loss.

Energy ownership remains separate:

- Node balance: Cartesian quadrature kinetic plus constitutive energy change,
  plus damping loss, minus incident endpoint work.
- Edge balance: connector potential change plus both signed endpoint works.
- Group balance: member energy plus loss and internal connector potential change,
  minus boundary endpoint work. Internal works are not counted again.

At every RK4 sample the report checks those balances. It compares coarse and
fine states at every common time, verifies disconnected root independence, and
requires a nonzero connected-child root response. Sampled damping and connector
powers are independently recomputed from positions/rates and integrated by the
trapezoidal rule; their errors against evolved ledgers must decrease on step
halving. These sampled integrals have second-order quadrature error and are not
confused with the fourth-order state integrator's balance residual.

The saved-ledger negative control reverses one endpoint-work sign and measures
the resulting edge-balance signal. This is a ledger sign-sensitivity control,
not a new faulty-force trajectory. The established instantaneous adapter tests
already exercise missing bias, wrong endpoint reaction, and point/distributed
matrix mismatch.

The retained numerical checks are maximum node/edge/group residual below 1e-12 J,
maximum passive/conservative energy sample increase below 1e-12 J, coarse/fine
common-time state difference below 1e-7, and matched DOP853 difference below
1e-8. The negative ledger signal must exceed 1e-13 J and 100 times the healthy
edge residual. These are numerical acceptance bounds for this finite experiment;
no existing report threshold is changed. State differences mix generalized
positions, rates, and ledger units and are reported only as componentwise
absolute numerical comparisons, not a physical norm.

Focused tests use .002 s evolutions; the full report separately runs the complete
.1 s experiment once, avoiding duplicate expensive integration in CI. Source
hashes are normalized UTF-8/LF. The JSON records every state and scope flags.

This result does not validate arbitrary depth, physical attachments or spatial
clearance, solid overlap partition, finite-thickness shell inertia, measured
material calibration, powered recursion/restart compatibility, or stable
breathing. Connector potential remains abstract mapped-port energy. Depth-1
response is not depth convergence. The optional graph state is not a new
persistence format and must not be used to relabel point-model checkpoints.
