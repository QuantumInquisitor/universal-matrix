# Unified Gauge Engine v0.1

## Purpose

This extension combines the current experimental source and gauge modules into a single synchronized evolution step.

Implementation:

`src/unified_engine.py`

Tests:

`tests/test_unified_engine.py`

The engine integrates:

- polarization-induced electric charge;
- polarization current;
- conserved free electric charge/current;
- six-gate boundary charge exchange;
- 3D U(1) gauge evolution;
- Gauss-constraint projection;
- compact topological magnetic-charge diagnostics.

## 1. Total electric source

The instantaneous electric source is

[
ho_E
=
ho_{m pol}
+
ho_{m free}.
]

The polarization part remains

[
ho_{m pol}
=
-
abla_{m lat}cdot P.
]

The free-charge part obeys

[
dotho_{m free}
+

abla_{m lat}cdot J_{m free}
=
0
]

for internal current flow.

Boundary inflow changes the integrated free charge according to

[
Delta Q_{m boundary}
=
Delta t
sum_{gin B_6}Phi_g.
]

## 2. Combined current

During one timestep the engine forms

[
J_{m total}
=
J_{m pol}
+
J_{m free}.
]

The polarization current is

[
J_{m pol}
=
rac{P^{n+1}-P^n}{Delta t}.
]

The source-coupled gauge update uses this combined internal current.

## 3. Periodic Gauss-law zero mode

The present 3D gauge adapter remains periodic.

Therefore

[
sum_x 
abla_{m lat}cdot E(x)=0
]

identically.

A periodic Gauss equation

[

abla_{m lat}cdot E=ho
]

can therefore only be solved if

[
sum_xho(x)=0.
]

However, six-gate boundary inflow can produce nonzero integrated electric charge.

The unified engine handles this explicitly instead of hiding the inconsistency.

It decomposes the source into

[
ho_E
=
ho_{m field}
+
ho_0,
]

where

[
ho_{m field}
=
ho_E-langleho_Eangle
]

has zero spatial mean, and the removed zero mode is tracked separately by

[
oxed{
Q_0=sum_xho_E(x).
}
]

The periodic gauge field responds only to (ho_{m field}).

This is mathematically equivalent to introducing a uniform compensating background for the periodic field problem. It is not the same thing as a true open-boundary electromagnetic solution.

## 4. Gauss projection

After source evolution, the engine computes the residual

[
R_G
=

abla_{m lat}cdot E
-
ho_{m field}.
]

It then solves a minimum-energy discrete Poisson problem for a longitudinal correction field (delta E) satisfying

[

abla_{m lat}cdotdelta E
=
-R_G.
]

The updated electric field is

[
Eightarrow E+delta E.
]

This preserves any existing transverse electric component while restoring the periodic Gauss constraint.

The engine reports the maximum post-projection Gauss residual every timestep.

## 5. Synchronized timestep

One unified step performs:

1. build the new polarization field from the new polarity configuration;
2. derive polarization current;
3. derive new polarization charge;
4. evolve free charge under free current;
5. apply six-gate boundary injection;
6. form total internal current;
7. evolve the U(1) gauge field with that current;
8. form the new total electric source;
9. split off the periodic zero mode;
10. project the electric field back onto the Gauss constraint;
11. recompute compact topological magnetic charge;
12. report conservation diagnostics.

## 6. Charge accounting

The engine verifies

[
Q_{m new}
-
Q_{m old}
=
Delta t
sum_g Phi_g
]

up to floating-point error.

Internal polarization and free currents do not change total electric charge.

Only explicit boundary exchange changes the integrated internal charge.

The reported charge-balance residual is

[
R_Q
=
Q_{m new}
-
Q_{m old}
-
Delta tsum_gPhi_g.
]

## 7. Topological sector

Compact magnetic charge remains separate from electric charge.

Every timestep the engine recomputes the integer cube charge

[
m(x)inmathbb Z
]

from compact plaquette winding.

Diagnostics include:

- total topological magnetic charge;
- number of cubes with nonzero topological charge.

This allows electric-source evolution and topological gauge defects to be monitored simultaneously without identifying them as the same source.

## 8. Tests

The regression suite verifies:

1. closed polarization evolution preserves zero total electric charge;
2. internal free current conserves total electric charge;
3. six-gate inflow changes total electric charge by the exact integrated boundary flux;
4. injected nonzero charge appears in the tracked periodic zero mode;
5. the mean-subtracted field source remains neutral;
6. Gauss projection restores the periodic constraint;
7. topological magnetic diagnostics remain separate and integer valued;
8. an initially nonzero free charge is decomposed into neutral field source plus tracked zero mode.

## 9. What this changes conceptually

The previous modules could each satisfy their own conservation law while still being mutually inconsistent when combined.

The unified engine removes that ambiguity.

The dynamical state now has the explicit structure

[
oxed{
(P,ho_{m pol},
ho_{m free},
Phi_{B_6},
E,
B,
m_{m topo},
Q_0)
}
]

with one synchronized update and one diagnostic report.

## 10. Remaining limitation

The largest remaining field-theory limitation is now the periodic spatial domain.

A true physical treatment of boundary injection should eventually replace the periodic zero-mode workaround with an open-boundary or finite-volume gauge solver in which field flux can genuinely terminate on or cross the six external boundary faces.

That is the next structurally important upgrade.

## Status

All currently implemented source channels and the 3D gauge field now evolve through one synchronized engine.

The integrated system conserves internal source flow, accounts exactly for six-gate charge exchange, restores periodic Gauss consistency, and tracks topological magnetic defects separately.
