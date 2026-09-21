# Homogeneous Time-Dependent Reciprocity Dirac Sector v0.1

## Purpose

The repository already contains:

- constant-(psi) Dirac propagation;
- static spatially varying (psi(mathbf x)) with the Hermitian spatial
  spin-connection term.

This extension adds the complementary case

[
psi=psi(t)
]

exactly.

Implementation:

`src/reciprocity_dirac_time_background.py`

Tests:

`tests/test_reciprocity_dirac_time_background.py`

## 1. Metric

[
ds^2
=
-N(t)^2dt^2
+
a(t)^2dmathbf x^2
]

with

[
N=e^{-psi},
qquad
a=e^{psi}.
]

## 2. Curved spinor normalization

For the unrescaled spinor (Psi), the spatial volume element is

[
a^3d^3x.
]

Therefore the conserved one-mode norm is

[
oxed{
a^3Psi^daggerPsi.
}
]

Define the rescaled spinor

[
oxed{
chi
=
a^{3/2}Psi
=
e^{3psi/2}Psi.
}
]

Then (chi^daggerchi) uses the ordinary flat norm.

## 3. Hermitian rescaled Hamiltonian

For a spatial Fourier mode (mathbf p),

[
oxed{
H_chi
=
e^{-2psi}
oldsymbolalphacdotmathbf p
+
e^{-psi}eta m.
}
]

This is Hermitian for every instantaneous value of (psi(t)).

The static limit agrees exactly with the previously implemented
constant-background reciprocity Dirac Hamiltonian.

## 4. Temporal spin connection

Because

[
chi=e^{3psi/2}Psi,
]

the unrescaled spinor equation is

[
oxed{
ipartial_tPsi
=
left[
H_chi
-
rac{3i}{2}dotpsi
ight]Psi.
}
]

The apparently anti-Hermitian term is the homogeneous temporal spin-connection
/ volume-dilution contribution.

It is required so that

[
a^3Psi^daggerPsi
]

remains constant.

## 5. Shared causal cone

For a massless spinor,

[
oxed{
v_{m coord}
=
e^{-2psi}.
}
]

The reciprocity metric null speed is also

[
oxed{
c_{m null,coord}
=
e^{-2psi}.
}
]

Thus the time-dependent Dirac principal propagation speed remains on the same
causal cone as the geometry scalar and gauge sectors.

## 6. Numerical evolution

The rescaled one-mode equation is integrated with RK4.

The tests verify:

- Hermiticity of the instantaneous rescaled Hamiltonian;
- exact static-limit agreement;
- equivalence of rescaled and unrescaled equations;
- equality of curved and rescaled norms;
- norm conservation under time-dependent (psi(t));
- massless speed equality with the metric null cone.

## 7. What remains open

The full case

[
psi=psi(t,mathbf x)
]

requires both:

- the static spatial anticommutator/spin-connection structure;
- the temporal volume/spin-connection structure;

in one operator, including noncommuting time-dependent spatial coefficients.

That is the next Dirac-sector derivation.

## Status

The temporal part of the reciprocity Dirac spin connection is now implemented
and tested for homogeneous time-dependent geometry.
