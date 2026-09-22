# Minimal Matrix Local Transition Law v0.1

## Purpose

This module answers the next creator-style design question after the primitive
ontology contract:

> What is the minimal transition law between neighboring Matrix cells that can
> support local propagation, conservative exchange, gauge transport, and a
> controlled long-distance wave limit?

Implementation:

- `src/matrix_local_transition.py`

Tests:

- `tests/test_matrix_local_transition.py`

This is an experimental ontology bridge. It does not replace the richer matter,
gauge, reciprocity, or fully coupled field systems already present in the
repository.

## 1. Site and link variables

The minimal site state used here is

[
(phi_x,Pi_x),
]

where

- (phi_x) is a dimensionless local phase;
- (Pi_x) is its conjugate momentum.

The exact canonical address

[
(a,p)
]

from the primitive ontology remains separate metadata. The canonical polarity
bit is not duplicated as another independent site variable.

Each positively oriented nearest-neighbor link carries a compact transport
phase

[
	heta_{xy}.
]

## 2. Gauge-covariant local difference

Under the local transformation

[
phi_xightarrowphi_x+alpha_x,
]

[
	heta_{xy}
ightarrow
	heta_{xy}+alpha_x-alpha_y,
]

the combination

[
Delta_{xy}
=
phi_y-phi_x+	heta_{xy}
]

is invariant.

Therefore a local interaction can depend on (Delta_{xy}) without depending
on an arbitrary local phase convention.

## 3. Minimal Hamiltonian

The current candidate law is

[
oxed{
H
=
sum_x
rac{Pi_x^2}{2I}
+
kappa
sum_{langle xyangle}
left[
1-cos(Delta_{xy})
ight]
}
]

with

[
I>0,
qquad
kappa>0.
]

Here (I) is a dimensionless inertia parameter and (kappa) is a
dimensionless nearest-neighbor coupling.

This is the compact rotor form of the minimal local exchange law.

## 4. Equations of motion

Hamilton's equations give

[
dotphi_x
=
rac{Pi_x}{I},
]

and

[
dotPi_x
=
-rac{partial H}{partialphi_x}.
]

Every link contributes equal and opposite momentum exchange to its two
endpoints.

Therefore

[
oxed{
rac{d}{dt}
sum_xPi_x
=
0
}
]

in continuous time.

This conservation law follows from global phase-shift symmetry.

## 5. Locality

Only nearest-neighbor links contribute to the force on one site.

A localized phase defect therefore produces an immediate force only on:

- the defect site;
- its (+X) and (-X) neighbors;
- its (+Y) and (-Y) neighbors;
- its (+Z) and (-Z) neighbors.

No direct one-step force is introduced between non-neighboring cells.

This realizes the six-gate repeated-cell locality hypothesis without requiring
long-range microscopic action.

## 6. Weak-field continuum candidate

For small gauge-covariant phase differences,

[
|Delta_{xy}|ll1,
]

we have

[
sinDelta_{xy}
approx
Delta_{xy}.
]

With zero background link phase, the site equation becomes

[
Iddotphi
=
kappaDelta_{m lat}phi,
]

where (Delta_{m lat}) is the nearest-neighbor graph Laplacian.

The characteristic lattice speed is therefore

[
oxed{
c_{m lat}
=
sqrt{rac{kappa}{I}}
}
]

in lattice sites per model-time unit.

This establishes a finite dimensionless propagation scale.

It does not yet establish the physical speed of light because the physical
length per site and physical duration per model-time unit remain unresolved.

## 7. Relation to existing gauge-matter systems

The repository already contains richer systems, including:

- `src/gauge_matter.py`;
- `src/classical_matter_dynamics.py`;
- `src/fully_coupled_classical_fields.py`;
- `src/fully_coupled_compact_fields.py`.

Those modules include additional structure such as:

- amplitude;
- complex matter fields;
- polarity-sensitive current ansätze;
- dynamical gauge fields;
- charge density;
- Gauss constraints;
- content/geometry-like scalar fields;
- self-interaction.

The local-transition module is intentionally simpler.

Its role is to identify the smallest local Hamiltonian skeleton that the richer
systems can be viewed as extending.

## 8. What this answers

The new law gives a first explicit answer to several creator questions.

### Local propagation

Yes, a strictly local six-neighbor law can propagate disturbances.

### Conservative exchange

Yes, the continuous-time law is Hamiltonian and pairwise momentum exchange is
antisymmetric.

### Gauge transport

Yes, local coupling can be written only through a gauge-invariant link
difference.

### Continuum candidate

Yes, the weak-field limit reduces to a discrete wave equation.

### Finite causal scale

Yes, a dimensionless lattice characteristic speed exists:

[
c_{m lat}=sqrt{kappa/I}.
]

## 9. What this does not answer

The following remain open:

1. Why should this rotor Hamiltonian be selected uniquely rather than merely be
   a minimal consistent candidate?
2. What fixes (I) and (kappa)?
3. What fixes physical lattice spacing?
4. What fixes physical time per model-time unit?
5. Are the link variables fundamental or emergent?
6. How should the exact canonical polarity branch affect local interaction, if
   at all?
7. How do nested scale levels couple to this spatial local law?
8. What dynamical law fixes the gauge-link electric field from the same
   ontology?
9. Does long-distance isotropy survive beyond the lowest-order cubic lattice
   approximation?
10. What stable nonlinear excitations exist under the minimal law?

## 10. Next creator question

The next highest-leverage question is:

> Can the site phase/momentum law and the dynamical gauge-link/electric-field
> law be derived from one local Hamiltonian with one exact Gauss constraint,
> rather than existing as separately motivated sectors?

The repository already contains much of the required machinery in the fully
coupled compact-field modules. The next task is therefore not to invent another
field sector, but to reduce those richer models back onto the ontology and
identify which terms are forced by symmetry, locality, and conservation and
which remain free hypotheses.

## Status

**Experimental ontology-level transition law.**

Internally verified properties:

- six-neighbor locality;
- gauge-invariant interaction energy;
- exact pairwise force antisymmetry;
- continuous-time total phase-momentum conservation;
- weak-field lattice-Laplacian limit;
- finite lattice characteristic speed;
- bounded symplectic energy error under tested integration conditions.

No physical dimensional scale or experimental confirmation is claimed.
