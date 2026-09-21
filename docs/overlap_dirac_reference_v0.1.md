# Overlap-Dirac / Ginsparg-Wilson Chiral Reference v0.1

## Purpose

Wilson fermions remove lattice doublers but explicitly complicate chiral
symmetry.

This extension adds a standard free overlap-Dirac reference that satisfies the
Ginsparg-Wilson relation exactly.

Implementation:

`src/overlap_dirac_reference.py`

Tests:

`tests/test_overlap_dirac_reference.py`

## 1. Euclidean Wilson kernel

For four lattice directions,

[
D_W(p)
=
isum_mu
gamma_musin p_mu
+
rsum_mu
(1-cos p_mu).
]

Define

[
A=D_W-ho,
]

with

[
0<ho<2r.
]

## 2. Overlap operator

The overlap operator is

[
oxed{
D_{m ov}
=
ho
left[
1+
rac{A}{sqrt{A^dagger A}}
ight].
}
]

For the free momentum-space kernel,

[
A^dagger A
=
left[
sum_musin^2p_mu
+
(W-ho)^2
ight]I.
]

## 3. Ginsparg-Wilson relation

The implemented operator satisfies

[
oxed{
gamma_5D
+
Dgamma_5
=
rac1ho
Dgamma_5D.
}
]

The tests evaluate the full matrix residual at generic momentum and require it
to vanish to numerical precision.

## 4. Gamma5 Hermiticity

The overlap operator also satisfies

[
oxed{
D^dagger
=
gamma_5Dgamma_5.
}
]

This is verified independently.

## 5. Doubler removal

In four Euclidean dimensions the naive Brillouin zone has

[
2^4=16
]

corners.

For

[
0<ho<2r,
]

only

[
p=(0,0,0,0)
]

remains a zero of the overlap operator.

Every nonzero corner is lifted to

[
oxed{
D_{m ov}=2ho I.
}
]

Thus the reference has one physical massless pole rather than sixteen naive
species.

## 6. Modified lattice chirality

Define

[
oxed{
widehat{gamma}_5
=
gamma_5
left(
1-rac{D}{ho}
ight).
}
]

For the free overlap operator,

[
widehat{gamma}_5^2=1.
]

This is the lattice-modified chiral structure associated with
Ginsparg-Wilson fermions.

## 7. What this accomplishes

The repository now distinguishes three fermion levels:

1. naive lattice fermions, which double;
2. Wilson fermions, which lift doublers but modify chiral symmetry;
3. overlap/Ginsparg-Wilson fermions, which realize exact lattice-modified
   chirality.

## 8. What remains open

This reference is free and momentum-space.

A physical chiral gauge theory still requires:

- gauge-covariant overlap operator;
- admissible gauge backgrounds / locality analysis;
- chiral projectors built from (widehat{gamma}_5);
- anomaly accounting;
- anomaly cancellation for the complete matter representation;
- coupling to the reciprocity geometry;
- second quantization.

## Status

The repository now has an exact chiral lattice-fermion correctness target
without reintroducing species doubling.
