# Three-Dimensional Gauge Adapter v0.1

## Purpose

This extension uses the canonical six boundary orientations

[
{+X,-X,+Y,-Y,+Z,-Z}
]

as the orientation scaffold for a periodic three-dimensional U(1) lattice gauge field.

Implementation:

`src/gauge_3d.py`

Tests:

`tests/test_gauge_3d.py`

This is an experimental physical adapter. The six canonical gates provide a mathematically natural signed three-axis set, but the adapter does not yet prove that those axes are physical space.

## 1. Spatial scaffold

The boundary orientation set is identified at the adapter level with the three coordinate axes:

[
pm X,qquad pm Y,qquad pm Z.
]

A cubic periodic lattice is introduced with link fields

[
A_x,qquad A_y,qquad A_z.
]

Time is supplied separately by Hamiltonian evolution.

This creates a (3+1)-style computational structure, but the physical interpretation of the lattice spacing remains an additional hypothesis.

## 2. Gauge transformation

For local phase (alpha(x)), each oriented link transforms as

[
A_i(x)
ightarrow
A_i(x)+alpha(x)-alpha(x+hat i).
]

Elementary plaquette angles are

[
F_{ij}(x)
=
A_i(x)
+
A_j(x+hat i)
-
A_i(x+hat j)
-
A_j(x).
]

They are exactly invariant under the local U(1) transformation modulo (2pi).

## 3. Magnetic-like components

The three independent spatial plaquettes are identified algebraically as

[
B_x = F_{yz},
]

[
B_y = F_{zx},
]

[
B_z = F_{xy}.
]

These are gauge-invariant curvature components.

The discrete lattice identity

[

abla_{m lat}cdot B=0
]

holds identically because the plaquette field is a lattice curl. This is the discrete Bianchi identity and is the direct analogue of the homogeneous Maxwell equation

[

ablacdotmathbf B=0.
]

The implementation tests this identity directly for arbitrary small link configurations.

## 4. Electric-like field and Gauss constraint

The conjugate momenta to the three link fields are

[
E_x,qquad E_y,qquad E_z.
]

Their discrete divergence is

[
G(x)
=
sum_{i=x,y,z}
left[
E_i(x)-E_i(x-hat i)
ight].
]

In the source-free sector,

[
oxed{G(x)=0}.
]

With a physical source map, the natural extension would be

[
G(x)=ho(x).
]

The present implementation tests preservation of the source-free Gauss constraint during weak-field Hamiltonian evolution.

## 5. Weak-field Hamiltonian

For small plaquette angle,

[
H_{m weak}
=
rac12sum_xsum_i E_i(x)^2
+
rac{eta}{2}sum_xsum_{i<j}F_{ij}(x)^2.
]

This is the standard quadratic lattice Abelian gauge-field form.

The compact magnetic energy remains available as

[
H_B
=
eta
sum_{x,i<j}
left[
1-cos F_{ij}(x)
ight].
]

## 6. Transverse plane waves

Consider a weak transverse configuration in which only (A_y) is nonzero and it varies along the (x) direction:

[
A_y(x,t)
=
A_0e^{i(qx-omega t)}.
]

The lattice field equation gives

[
ddot A_y(x)
=
eta
left[
A_y(x+1)-2A_y(x)+A_y(x-1)
ight].
]

Therefore

[
oxed{
omega^2
=
4etasin^2(q/2)
}.
]

This is the same lattice dispersion relation independently derived for the routing-scale cylinder.

For long wavelength,

[
omegaapproxsqrt{eta}|q|,
]

so

[
oxed{
c_{m lat}=sqrt{eta}
}.
]

The 3D test suite directly checks the transverse-mode acceleration against this analytic eigenvalue.

## 7. Maxwell-structure comparison

The present 3D gauge adapter now contains structural counterparts of:

### Gauss magnetic law

[

ablacdotmathbf B=0
]

through the exact lattice Bianchi identity.

### Gauss electric law

[

ablacdotmathbf E=ho
]

through the Hamiltonian Gauss constraint once a source map is supplied.

### Faraday/Ampere wave sector

Hamiltonian evolution couples link coordinates and their conjugate fields. In the weak-field source-free sector, transverse modes obey the discrete wave equation and the lattice dispersion relation above.

This is enough to call the dynamics **Maxwell-like as a lattice U(1) gauge system**.

It is not yet enough to identify the variables with measured physical electric and magnetic fields.

## 8. What the six gates contribute

The important architectural fact is

[
B_6={pm X,pm Y,pm Z}.
]

That set supplies exactly three signed orientation pairs.

Consequently a three-axis gauge adapter is not an arbitrary addition unrelated to the kernel. The spatial orientation count comes directly from the canonical boundary architecture.

What does **not** follow automatically is:

- Euclidean metric distance;
- a physical lattice spacing (a);
- physical isotropy;
- SI dimensions;
- the numerical value of the propagation speed.

Those still require independent physical identification.

## 9. Remaining steps

The immediate unresolved tasks are now:

1. define matter/source variables and a conserved current;
2. couple that current gauge-covariantly to the 3D field;
3. derive the lattice continuity equation;
4. verify the source-coupled Gauss constraint remains preserved;
5. determine whether the polarity/injection dynamics can provide the source/current sector;
6. derive or independently measure the physical lattice spacing and time conversion;
7. run the complete repository test suite.

## Status

The engine now has a mathematically explicit three-dimensional U(1) gauge adapter whose axes are motivated by the canonical six boundary orientations.

It contains:

[
oxed{	ext{three electric-like link components}}
]

[
oxed{	ext{three magnetic-like curvature components}}
]

[
oxed{	ext{Gauss constraint}}
]

[
oxed{	ext{discrete Bianchi identity}}
]

[
oxed{	ext{transverse propagating modes}}
]

[
oxed{omega^2=4etasin^2(q/2)}
]

The remaining challenge is the physical source sector and the conversion from lattice units to measured electromagnetic quantities.
