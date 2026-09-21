# SU(2) Hamiltonian Gauge Dynamics Reference v0.1

## Purpose

The SU(2) Wilson sector previously contained exact static gauge geometry but no
electric Hamiltonian dynamics.

This extension adds a source-free Kogut-Susskind-style Hamiltonian reference.

Implementation:

`src/su2_hamiltonian_reference.py`

Tests:

`tests/test_su2_hamiltonian_reference.py`

## 1. Canonical variables

Each oriented link carries

[
U_i(x)in SU(2)
]

and a left-electric Lie-algebra momentum

[
E_i(x)
=
E_i^a(x)T_a,
]

with

[
T_a=rac{sigma_a}{2}.
]

## 2. Hamiltonian

[
oxed{
H
=
rac12
sum_{m links,a}
(E_i^a)^2
+
eta
sum_p
left[
1-rac12operatorname{ReTr}U_p
ight].
}
]

## 3. Exact group drift

The link equation is represented as

[
dot U_i
=
iE_iU_i.
]

A finite drift step is therefore

[
oxed{
U_i
	o
exp(iDelta t,E_i)
U_i.
}
]

For SU(2), the exponential is evaluated in closed form.

Therefore each drift remains on the SU(2) group manifold to numerical
precision.

## 4. Wilson force reference

For a link component (a), define a left group perturbation

[
U_i
	o
e^{iepsilon T_a}U_i.
]

The canonical force is

[
oxed{
dot E_i^a
=
-rac{partial V}{partial q_i^a}.
}
]

The reference implementation evaluates this derivative symmetrically:

[
rac{partial V}{partial q_i^a}
approx
rac{
V(e^{+iepsilon T_a}U_i)
-
V(e^{-iepsilon T_a}U_i)
}{
2epsilon
}.
]

This is intentionally slower than an analytic staple implementation.

Its role is to provide a high-confidence numerical oracle against which the
optimized force can be tested.

## 5. Non-Abelian Gauss generator

At site (x),

[
oxed{
G(x)
=
sum_i
left[
E_i(x)
-
U_i^dagger(x-hat i)
E_i(x-hat i)
U_i(x-hat i)
ight].
}
]

The incoming electric field is parallel transported into the algebra frame at
the destination site before subtraction.

Source-free physical states satisfy

[
G(x)=0.
]

## 6. Integration

The engine uses kick-drift-kick:

1. half electric-force kick;
2. exact SU(2) group drift;
3. second half kick.

Tests verify:

- SU(2) preservation;
- force sign against direct group derivative;
- exact identity vacuum stationarity;
- Gauss cancellation for a uniform compatible field;
- small energy drift for a nontrivial source-free smoke evolution.

## 7. Next step

The finite-difference force scales poorly with lattice size.

The next implementation should derive the analytic staple force and verify it
pointwise against this reference.

## Status

SU(2) now has a genuine Hamiltonian electric sector and non-Abelian Gauss
constraint reference.
