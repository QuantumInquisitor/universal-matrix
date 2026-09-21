# Charged U(1) Overlap Index and Anomaly Ledger v0.1

## Purpose

This extension separates two different layers that must not be conflated in a
chiral gauge theory:

1. the finite-lattice overlap index density of a charged fermion;
2. the representation-level perturbative U(1) anomaly coefficients of a set of
   Weyl species.

Implementation:

`src/u1_chiral_anomaly_ledger.py`

Tests:

`tests/test_u1_chiral_anomaly_ledger.py`

## 1. Charge-q overlap operator

For a fermion of Abelian charge (q), the compact link phase seen by the
Wilson/overlap kernel is

[
A_mu(x)
longrightarrow
q A_mu(x).
]

The module therefore constructs

[
D_q[A]
=
D_{m ov}[qA].
]

This uses the same overlap machinery already verified for unit charge.

## 2. Local overlap index density

The local density is defined by the diagonal spin trace

[
oxed{
q_{m index}(x)
=
operatorname{tr}_{m spin}
left[
gamma_5
left(
I-rac{D_q}{2ho}
ight)
ight]_{x,x}.
}
]

Its lattice sum is

[
oxed{
sum_x q_{m index}(x)
=
operatorname{Tr}
left[
Gamma_5
left(
I-rac{D_q}{2ho}
ight)
ight].
}
]

The implementation computes the local and global forms independently and tests
their equality.

For the trivial free background used in the reference tests, the index is zero.

## 3. Gauge invariance

The underlying unit-charge compact gauge field transforms as

[
A_mu(x)
ightarrow
A_mu(x)
+
alpha(x)
-
alpha(x+hatmu).
]

The charge factor is applied when constructing (D_q[A]).

The local overlap index density is tested for invariance under this
transformation on weak admissible compact-U(1) fields.

## 4. Weyl-species anomaly bookkeeping

Each species is represented by

[
(q_i,chi_i),
]

where

[
chi_i
=
egin{cases}
+1 & 	ext{one handedness},\
-1 & 	ext{the opposite handedness}.
end{cases}
]

The four-dimensional Abelian cubic coefficient is

[
oxed{
C_{U(1)^3}
=
sum_i
chi_i q_i^3.
}
]

The mixed gravitational-Abelian coefficient is

[
oxed{
C_{m grav-U(1)}
=
sum_i
chi_i q_i.
}
]

The ledger reports both coefficients independently.

A vectorlike pair with equal charge and opposite handedness cancels both.

The tests also include a charge set for which the linear sum vanishes while the
cubic sum does not, verifying that the two constraints are logically
independent.

## 5. Covariant local anomaly candidate

For one Weyl species, the module also exposes

[
oxed{
mathcal A_{m cov}^{m candidate}(x)
=
chi q,
q_{m index}(x).
}
]

This is explicitly classified as a **covariant-anomaly diagnostic candidate**.

It is useful because in the continuum limit the charged overlap index density
is the lattice object expected to encode the corresponding topological
response.

However, it is not yet the consistent gauge anomaly derived from the variation
of a globally defined Weyl measure.

## 6. What is now testable

The repository can now test, separately:

- charged overlap-index locality;
- local gauge invariance of the index density;
- integrated index consistency;
- (U(1)^3) representation cancellation;
- mixed gravitational-U(1) representation cancellation;
- cancellation of the local covariant candidate for vectorlike species.

## 7. What remains unresolved

The following steps are still required for a complete anomaly analysis:

1. derive the consistent anomaly from the Weyl measure phase;
2. relate measure holonomy to infinitesimal gauge transformations;
3. determine the lattice counterpart of the Bardeen-Zumino relation between
   covariant and consistent anomalies;
4. extend the charged overlap construction to SU(2) and SU(3);
5. test complete non-Abelian and mixed anomaly coefficients;
6. treat global anomalies and topologically nontrivial gauge sectors;
7. supply a physically motivated chiral representation spectrum.

## 8. Scientific status

The representation sums

[
sum_ichi_i q_i^3,
qquad
sum_ichi_i q_i
]

are standard algebraic anomaly coefficients.

The local overlap index density is a finite-lattice topological diagnostic.

The repository does **not** yet claim that these pieces alone constitute a
complete anomaly-free lattice chiral gauge theory.

## Status

The chiral program now connects

[
oxed{
D_q[A]
ightarrow
q_{m index}(x)
ightarrow
	ext{representation anomaly ledger}.
}
]

This is the first direct bridge in the project between charged overlap topology
and explicit chiral-representation cancellation conditions.
