# Clock-Space Reciprocity v0.1

## Purpose

The six-gate symmetry constrains the spatial response to

\\[
S(psi)
=
e^{gamma_Mpsi},
\\]

but does not by itself fix (gamma_M).

The content-clock sector gives the tick-duration lapse

\\[
L_t(psi)
=
e^psi.
\\]

This note introduces one additional physical postulate:

> A local canonical propagation event remains one responded spatial link per one
> responded routing tick, so the locally measured causal speed is independent of
> the content potential.

Implementation:

`src/clock_space_reciprocity.py`

Tests:

`tests/test_clock_space_reciprocity.py`

## 1. Local causal-speed ratio

Under the responded link/tick interpretation,

\\[
rac{v_{m local}}{v_{m ref}}
=
rac{S}{L_t}.
\\]

Therefore

\\[
rac{v_{m local}}{v_{m ref}}
=
e^{(gamma_M-1)psi}.
\\]

If local causal speed is invariant for arbitrary (psi),

\\[
e^{(gamma_M-1)psi}=1.
\\]

Hence

\\[
oxed{
gamma_M=1.
}
\\]

This result is conditional on the reciprocity postulate.

It is not a theorem of the canonical finite kernel alone.

## 2. Resulting clock and spatial response

With

\\[
gamma_M=1,
\\]

the local clock-rate ratio is

\\[
N(psi)=e^{-psi},
\\]

and the spatial scale response is

\\[
S(psi)=e^psi.
\\]

The static isotropic effective line element becomes

\\[
oxed{
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}
(dx^2+dy^2+dz^2).
}
\\]

## 3. Weak-field expansion

For small (psi),

\\[
-e^{-2psi}
=
-1+2psi-2psi^2+O(psi^3),
\\]

and

\\[
e^{2psi}
=
1+2psi+2psi^2+O(psi^3).
\\]

Comparing with the standard first post-Newtonian isotropic form gives

\\[
oxed{
eta_{m PPN}=1,
qquad
gamma_{m PPN}=1
}
\\]

at the displayed weak-field orders.

This is a correspondence result for the effective metric candidate.

It is not a proof that the full theory equals General Relativity.

## 4. Light propagation

The null travel-time index is

\\[
n
=
rac{S}{N}
=
e^{2psi}.
\\]

For

\\[
psi(r)=rac{mu}{r},
\\]

the leading deflection is

\\[
oxed{
alpha
=
rac{4mu}{b}.
}
\\]

Thus the reciprocity postulate supplies the second half of the weak-field light
deflection that the clock-only scalar sector was missing.

## 5. Massive weak-field motion

The temporal metric factor gives the Newtonian-order correspondence

\\[
oxed{
mathbf a
=
c_*^2
ablapsi.
}
\\]

For a positive point source,

\\[
psi=rac{mu}{r},
\\]

so

\\[

ablapsi
=
-rac{mu}{r^3}mathbf r,
\\]

which points toward the source.

Therefore the reciprocity metric selects the previously ambiguous
"toward-higher-potential" massive-motion branch at weak field.

## 6. Relation to known exponential metrics

The line element

\\[
ds^2
=
-e^{-2psi}dt^2
+
e^{2psi}dmathbf x^2
\\]

is not historically novel.

Exponential metric forms have appeared in earlier alternative-gravity and
phenomenological work, including metrics often associated with
Papapetrou/Yilmaz-type constructions.

The present project must therefore distinguish:

- the known metric form;
- the specific Matrix route used to motivate it.

No novelty claim should be made for the metric form itself.

## 7. Strong-field warning

Published analyses of exponential metrics note that their strong-field behavior
can differ substantially from Schwarzschild/GR black-hole geometry.

Therefore agreement with weak-field coefficients

\\[
eta=gamma=1
\\]

does not establish correct compact-object physics.

The model still needs direct tests against:

- perihelion/precession observables;
- Shapiro delay beyond leading order;
- binary pulsars;
- compact-object structure;
- gravitational-wave generation;
- strong-field lensing;
- black-hole shadow/ringdown observations.

## 8. What this accomplishes

The sequence is now

\\[
oxed{
B_6	ext{ symmetry}
Rightarrow
S=e^{gamma_Mpsi}
}
\\]

plus

\\[
oxed{
	ext{local clock-space reciprocity}
Rightarrow
gamma_M=1.
}
\\]

So the previously free spatial response can be fixed by a clearly stated
physical principle rather than by fitting the Cassini result.

## Status

The reciprocity metric is an experimental effective-geometry candidate.

Its weak-field behavior is promising, but its strong-field and dynamical
behavior remain unvalidated.
