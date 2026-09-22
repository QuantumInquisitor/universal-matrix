# Canonical-Locked Alternating Scale Transfer v0.1

## Purpose

This extension sharpens the earlier neutral-crossing scale-transfer model by tying two previously free choices more tightly to the existing canonical structure.

Implementation:

`src/canonical_scale_transfer.py`

Tests:

`tests/test_canonical_scale_transfer.py`

## 1. Alternating scale orientation

The working hypothesis is that neighboring nested toroidal scales carry opposite orientation:

\\[
epsilon_ell = (-1)^ell.
\\]

This gives the polarity carrier

\\[
p_ell(phi)
=
epsilon_ell cosphi
\\]

and the inter-scale transfer carrier

\\[
s_ell(phi)
=
epsilon_ell sinphi.
\\]

Therefore two neighboring layers at the same phase have opposite signed orientation.

This implements the micro-to-macro polarity alternation hypothesis directly instead of leaving every scale with the same orientation convention.

## 2. Canonical clock normalization

The canonical routing cycle contains 36 ticks:

\\[
T^{36}=I,
\\]

with polarity reversal after 18 ticks:

\\[
T^{18}=P=T_{54}.
\\]

The associated polarity-clock increment per routing tick is

\\[
Deltaphi_P
=
rac{2pi}{36}
=
rac{pi}{18}.
\\]

The new transfer candidate identifies the maximum one-tick inter-scale rotation with this exact increment:

\\[
oxed{
delta_ell(phi)
=
epsilon_ell
rac{pi}{18}
sinphi.
}
\\]

This removes the separate free transfer coefficient from this specific candidate law.

That identification is an experimental normalization hypothesis, not a theorem of the canonical kernel.

## 3. Why the pair dynamics are rotations

Let the two adjacent scale amplitudes be

\\[
mathbf a
=
egin{bmatrix}
a_ell\
a_{ell+1}
end{bmatrix}.
\\]

Assume a linear continuous exchange law

\\[
dot{mathbf a}
=
Amathbf a
\\]

that conserves

\\[
mathcal C
=
a_ell^2+a_{ell+1}^2.
\\]

Then

\\[
rac{dmathcal C}{dt}
=
mathbf a^T
(A+A^T)
mathbf a.
\\]

For this to vanish for every state,

\\[
A+A^T=0.
\\]

Therefore the two-state generator must be skew-symmetric:

\\[
A
=
egin{bmatrix}
0 & -g\
g & 0
end{bmatrix}.
\\]

Its exponential is an orthogonal rotation.

So the rotation form is not arbitrary once linearity and exact quadratic conservation are imposed. What remains model dependent is the scalar generator (g).

The present canonical-locking hypothesis chooses

\\[
g
propto
epsilon_ellsinphi
\\]

with the proportionality normalized by (pi/18) per routing tick.

## 4. Transfer extrema and neutral crossings

At polarity extrema,

\\[
phi=0,pi,
\\]

so

\\[
sinphi=0
\\]

and therefore

\\[
delta_ell=0.
\\]

There is no inter-scale transfer.

At neutral crossings,

\\[
phi=rac{pi}{2},
rac{3pi}{2},
\\]

the magnitude is maximal:

\\[
|sinphi|=1.
\\]

Thus the transfer magnitude is exactly

\\[
|delta_ell|
=
rac{pi}{18}
\\]

for one routing tick.

## 5. Alternating direction across scales

Because

\\[
epsilon_{ell+1}
=
-epsilon_ell,
\\]

adjacent scale edges alternate their signed orientation.

This implements the hypothesis that nested toroidal fields flip orientation as the hierarchy moves from micro to macro and back again.

The same clock phase therefore need not mean the same directional flow on every scale.

## 6. Exact conservation

Every adjacent transfer uses

\\[
R(delta)
=
egin{bmatrix}
cosdelta & -sindelta\
sindelta & cosdelta
end{bmatrix}.
\\]

Hence

\\[
R^TR=I.
\\]

Therefore

\\[
a_ell'^2+a_{ell+1}'^2
=
a_ell^2+a_{ell+1}^2.
\\]

A chain of such rotations also preserves

\\[
oxed{
mathcal C_{m total}
=
sum_ell a_ell^2.
}
\\]

The implementation uses a symmetric forward and reverse half sweep to reduce ordering bias between noncommuting neighboring edge rotations.

## 7. Reversal symmetry

Since

\\[
sin(phi+pi)
=
-sinphi,
\\]

the transfer angle changes sign after a polarity half-cycle:

\\[
delta_ell(phi+pi)
=
-delta_ell(phi).
\\]

Thus the isolated two-layer map obeys

\\[
R[-delta(phi)]
=
R[delta(phi)]^{-1}.
\\]

The tests verify exact numerical recovery for reversed neutral-crossing phases and closure over a complete 36-tick canonical clock cycle for a single scale edge.

## 8. What is now constrained

This candidate now derives or fixes:

1. the alternating sign between adjacent nested layers from the explicit parity rule,
2. the transfer activation profile from the quadrature (sinphi),
3. zero transfer at polarity extrema,
4. maximum transfer at neutral crossings,
5. exact quadratic conservation from orthogonal dynamics,
6. the one-tick normalization from the canonical (pi/18) clock increment.

## 9. What remains unresolved

The model still does not establish that

\\[
a_ell^2
\\]

is physical energy.

It also does not yet derive the alternating orientation rule from a deeper topological theorem of the 108-state kernel.

The strongest next questions are:

1. Can the alternating scale sign be derived from the six-gate boundary orientation or a canonical representation rather than postulated?
2. Does a measurable system exist whose adjacent scale transfer follows the (pi/18) normalization?
3. Can gauge curvature, matter content, or six-gate flux modulate this canonical transfer without breaking the global conservation law?
4. Does the nested alternating law generate a measurable dispersion or resonance spectrum that differs from the earlier free-coupling model?

## Status

The model now contains a more constrained nested transfer candidate:

\\[
oxed{
delta_ell
=
(-1)^ell
rac{pi}{18}
sinphi_ell
}
\\]

with exact quadratic conservation.

It should currently be treated as an experimentally testable bridge hypothesis, not as an established physical law.
