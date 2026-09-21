# Open Six-Gate Boundary Solver v0.1

## Purpose

This extension replaces the periodic zero-mode workaround with a finite-volume
open-boundary Gauss solver attached directly to the six canonical gates:

[
{+X,-X,+Y,-Y,+Z,-Z}.
]

Implementation:

`src/open_boundary_solver.py`

Unified integration:

`src/unified_engine.py`

Tests:

`tests/test_open_boundary_solver.py`

## 1. Open-domain Gauss problem

The electric field satisfies

[

abla_{m lat}cdot E=ho
]

inside a finite three-dimensional cell complex.

At each physical boundary face, the outward electric flux is prescribed.

The global compatibility condition is

[
oxed{
sum_x ho(x)
=
Phi_{+X}+Phi_{-X}
+Phi_{+Y}+Phi_{-Y}
+Phi_{+Z}+Phi_{-Z}.
}
]

This is the discrete divergence theorem.

Unlike the previous periodic solver, nonzero total enclosed charge is therefore
allowed.

## 2. Finite-volume potential formulation

The interior field is represented as

[
E=-
abla_{m lat}phi.
]

The cell equation is

[
L_Nphi
=
ho-b,
]

where (L_N) is the Neumann graph Laplacian formed only from interior
neighbor links and (b) contains the prescribed outward boundary flux
contributions.

Because

[
L_N mathbf 1=0,
]

the potential has an arbitrary additive constant.

The numerical solver removes this null mode by enforcing

[
langlephiangle=0.
]

## 3. Numerical method

The system is solved without forming a dense matrix.

The implementation uses:

- matrix-free Neumann Laplacian application;
- projection onto the mean-zero subspace;
- Jacobi preconditioning based on local interior-neighbor degree;
- preconditioned conjugate gradients;
- explicit residual and compatibility checks.

This approach scales substantially better than direct dense inversion.

## 4. Boundary flux conventions

The solver variable (Phi_g) means **outward electric field flux** through
gate (g).

The existing `BoundaryFlux` object in the source engine uses a different
bookkeeping convention:

- positive value means electric charge enters the internal domain.

Those are not the same physical variable.

The unified engine preserves the source-engine charge accounting, then chooses
an outward electric-flux distribution whose total equals the enclosed electric
charge required by Gauss law.

When the source bookkeeping supplies nonzero gate activity, the current adapter
uses the magnitudes of those activities as relative face weights. If no gate
activity is present, the required outward electric flux is shared equally by
the six faces.

This weighting rule is an adapter convention, not a derived boundary law.

## 5. Nonzero total charge

Under open boundaries, the engine no longer needs to replace

[
ho
]

with

[
ho-langlehoangle.
]

Instead, the full source is used:

[
oxed{
ho_{m field}=ho_E.
}
]

and

[
oxed{
Q_0=0
}
]

for the open solver.

The required boundary electric flux carries the global Gauss balance.

The old periodic mode remains available explicitly as

`boundary_mode="periodic"`

for comparison and regression testing.

## 6. Tests

The solver tests verify:

1. nonzero total charge is solved successfully when six-face flux satisfies the
   discrete divergence theorem;
2. incompatible charge/flux data are rejected;
3. equal and weighted six-gate flux allocation preserve the exact required
   total;
4. zero source and zero flux produce zero field;
5. the compatibility residual is exactly charge minus outward flux.

The unified-engine tests also verify that:

- open mode supports initially nonzero free charge;
- boundary injection remains in the physical source rather than a periodic zero
  mode;
- Gauss residual remains small;
- legacy periodic mode still reproduces the old zero-mode decomposition.

## 7. Remaining boundary problem

The current open solver treats the six face fluxes as prescribed Neumann data.

A more complete dynamical theory would derive those face fluxes from the nested
micro-to-macro boundary dynamics themselves rather than selecting a weighting
rule.

That future step should connect

[
mathcal T_{ell}
leftrightarrow
B_6
leftrightarrow
mathcal T_{ell+1}
]

so that boundary flux is generated dynamically by inter-scale polarity and
injection rather than externally specified.

## Status

The Universal Matrix engine now has a genuine finite-domain six-gate Gauss
solver capable of representing nonzero enclosed electric charge.

The previous periodic compensating-background construction is no longer the
default field solution.
