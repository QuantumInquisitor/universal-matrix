# Instantaneous distributed-inertia graph contract

`scripts.fold_distributed_graph` is an optional mechanics adapter with no
trajectory solver. Existing point-inertia graphs, production imports, material
laws, geometry and historical numerical criteria are unchanged.

Each module retains the existing two generalized coordinates, 22 synthetic body
mass owners and 82 reference quadrature points. Panels have uniform reference
surface mass, bridges uniform line mass and hubs remain point masses. At scale
`a` the original body masses multiply by `a**3` and the reference length is
`.1*a` metres. The existing scale guard `[.25,1]`, coordinate rectangle, mass
validation and finite velocity/magnitude guards remain enforced. This is a
declared homothetic model, not measured material calibration.

`mechanical(q, velocity, scale)` returns the distributed quadrature state,
geometric bias and Cartesian kinetic plus existing constitutive energy.
`body_rhs(y, scale)` uses the distributed mass matrix and bias for a five-state
node `[q(2), velocity(2), damping_loss]`. `rhs(y, sizes, edges)` also uses that
same distributed matrix for connector forces. Mapped connector potential and
reciprocal generalized forces come directly from the existing implementation.
There are two signed endpoint-work states per edge, after all node states.

`measure(y, sizes, edges, layout)` returns node mechanical energies, edge
potentials, incident work and hierarchy accounts. Supply a layout compiled
from the same topology with the existing `compile_hierarchy` function. Kinetic
energy is evaluated from Cartesian quadrature velocities, independently of
the mass-matrix solve. Group accounts include node energy and damping loss
plus internal edge potential; boundary endpoint work is separate. Connector
potential is never assigned twice or silently included in node energy.

The existing residual signs are retained:

```text
node:  change(E_node) + damping_loss - incident_endpoint_work
edge:  change(U_edge) + work_at_a + work_at_b
group: change(sum(E_node + damping_loss) + internal_U) - boundary_work
```

At fixed coordinates and rates, mass matrix and bias scale as `a**5`. Under
`time -> a*time`, rates scale as `1/a`, energy and bias as `a**3`, and
acceleration as `1/a**2`; the existing damping matrix scales as `a**4`.
A depth-two half-size tree already reaches `.25`, so globally halving that
tree would violate the preserved scale guard.

The tests evaluate instantaneous states only. They check one-node equations,
owner masses, homothetic scaling, disconnected independence, zero-edge
accounts, connector power, hierarchy ownership and independent directional
energy derivatives at two differencing steps. At the declared nonstationary
three-node fixture, healthy energy-rate residuals must remain below `1e-10`
watts and three deliberate defects must exceed `1e-8` watts: omitted bias,
flipped connector reaction and point inertia used only for connector force.
These are finite-difference discrimination bounds, not trajectory tolerances.

Run `python -m pytest tests/test_fold_distributed_graph.py` for these controls.
The existing quadrature moment/derivative controls remain in
`tests/test_fold_distributed_inertia.py`.

No recursive trajectories, depth convergence, physical attachment frames,
contact law, finite-thickness inertia, hub rotation, electrical coupling,
powered reserve/restart adaptation or stable breathing are established here.
Single-specimen distributed trajectories already exist separately. A future
graph trajectory comparison must match their initial conditions explicitly:
the graph and single-specimen default states and ledger indexing differ.
