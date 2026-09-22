# Canonical Polarity Clock v0.1

## Purpose

This note derives a dimensionless polarity clock directly from the canonical
routing operator rather than assigning an arbitrary oscillator period.

Implementation:

`src/canonical_polarity_clock.py`

Tests:

`tests/test_canonical_polarity_clock.py`

## 1. Routing period

The canonical routing operator is

\[
T=T_{21}
\]

on (mathbb Z_{108}).

Its order is

\[
oxed{T^{36}=I}.
\]

The canonical polarity involution is

\[
P=T_{54}.
\]

Because

\[
18cdot21
=
378
equiv54
pmod{108},
\]

we have

\[
oxed{T^{18}=P}.
\]

Therefore one complete polarity cycle can be aligned exactly with the 36-state
routing cycle.

## 2. Polarity phase per routing tick

Define the dimensionless physical polarity phase

\[
oxed{
phi_P(k)
=
rac{2pi k}{36}
=
rac{\pi k}{18}.
}
\]

Therefore one routing tick advances the polarity clock by

\[
oxed{
Deltaphi_P
=
rac{\pi}{18}.
}
\]

This fixes the dimensionless clock increment from canonical routing.

It does **not** fix the physical duration of a routing tick.

## 3. Quarter-cycle operator

After nine routing ticks,

\[
T^9
=
T_{189}
=
T_{81}
\]

modulo 108.

Define

\[
oxed{
C=T^9=T_{81}.
}
\]

Then

\[
C^2
=
T^{18}
=
P
\]

and

\[
C^4
=
T^{36}
=
I.
\]

Thus

\[
oxed{
C^2=P,\qquad C^4=I.
}
\]

This produces a canonical four-stage cycle.

## 4. Four cardinal states

Using

\[
p(k)
=
cosphi_P(k)
\]

and

\[
s(k)
=
sinphi_P(k),
\]

the special routing ticks are:

\[
k=0:
\quad
phi_P=0,
\quad
p=+1,
\quad
s=0
\]

outward extremum;

\[
k=9:
\quad
phi_P=rac{\pi}{2},
\quad
p=0,
\quad
s=+1
\]

first neutral crossing;

\[
k=18:
\quad
phi_P=\pi,
\quad
p=-1,
\quad
s=0
\]

inward extremum and canonical polarity flip;

\[
k=27:
\quad
phi_P=rac{3pi}{2},
\quad
p=0,
\quad
s=-1
\]

second neutral crossing;

\[
k=36:
\quad
phi_P=2pi,
\quad
p=+1,
\quad
s=0
\]

full return.

Therefore the canonical routing cycle naturally supports

\[
oxed{
	ext{outward}
	o
	ext{neutral-up}
	o
	ext{inward}
	o
	ext{neutral-down}
	o
	ext{outward}.
}
\]

## 5. Connection to scale transfer

The previously defined neutral-crossing transfer law uses

\[
s(phi_P)=sinphi_P.
\]

The canonical clock now fixes its activation sequence without an arbitrary
continuous phase origin.

Maximum micro-to-macro transfer occurs at

\[
k=9
\]

and maximum macro-to-micro transfer occurs at

\[
k=27
\]

under the current orientation convention.

No transfer occurs at

\[
k=0,18,36.
\]

## 6. Important distinction from the 70-degree routing winding

The canonical routing operator also has the geometric winding increment

\[
	heta_T
=
2pirac{21}{108}
=
70^circ.
\]

That angle is a **routing winding angle**.

The polarity clock increment

\[
rac{\pi}{18}
=
10^circ
\]

is a different derived phase coordinate defined over the 36-step routing
period.

These two angles must not be conflated.

One tracks position on the seven-turn routing orbit.

The other tracks the normalized polarity cycle associated with

\[
T^{18}=P,
\qquad
T^{36}=I.
\]

## 7. What this fixes

The dimensionless polarity angular rate no longer needs to be chosen freely if
time is counted in routing ticks:

\[
oxed{
omega_P
=
rac{\pi}{18}
\quad
	ext{radians per routing tick}.
}
\]

If one routing tick later acquires a physical duration (	au), then

\[
omega_{P,m physical}
=
rac{\pi}{18	au}.
\]

Thus the remaining dimensional unknown is the physical tick duration (	au),
not the dimensionless polarity cycle itself.

## Status

The 36-state canonical routing cycle now supplies an exact four-stage polarity
clock:

\[
oxed{
T^9=C,
\quad
T^{18}=P,
\quad
T^{27}=C^3,
\quad
T^{36}=I.
}
\]

This is a mathematical consequence of the canonical routing algebra. The
interpretation of that clock as a physical oscillation remains experimental.
