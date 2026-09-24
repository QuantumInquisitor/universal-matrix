# Conservative three-dimensional toroidal current v0.1

`src/conservative_toroidal_field.py` supplies a prescribed, compact content
current on a solid ring torus. This closes the kinematic three-dimensional
field gate beyond the earlier conservative graph currents. The content and
coordinates remain dimensionless. A force law, evolution law, material model,
and physical identification are not supplied by this construction.

## Domain, stream function, and current

Let R>a>0 be the major and minor radii, rho=sqrt(x^2+y^2), u=rho-R,
and q=max(0,1-(u^2+z^2)/a^2). The support is u^2+z^2<a^2.
Since R>a, the support avoids the cylindrical axis. The current is exactly
zero outside, so its implementation never divides by rho on that axis.

With signed poloidal cut flux I and toroidal cut flux T, define

$
\psi=\frac{I}{2\pi}q^3,
\qquad
J_\rho=-\frac{1}{\rho}\partial_z\psi
=\frac{3Iz}{\pi a^2\rho}q^2,
$
$
J_z=\frac{1}{\rho}\partial_\rho\psi
=-\frac{3Iu}{\pi a^2\rho}q^2,
\qquad
J_\phi=\frac{3T}{\pi a^2}q^2.
$

The Cartesian vector is
`(J_rho*x/rho-J_phi*y/rho, J_rho*y/rho+J_phi*x/rho, J_z)`.
Both field and first derivatives vanish at the support boundary. Thus the
zero extension introduces no boundary source or singular surface flux.

## Local conservation and invariant surfaces

Axisymmetry makes the azimuthal divergence term zero. The remaining terms
cancel by equality of mixed derivatives:

$
\nabla\cdot J
=\rho^{-1}[-\partial_\rho\partial_z\psi
+\partial_z\partial_\rho\psi]=0.
$

For the stationary continuity equation, `dq_content/dt + div(J) = 0`, this
prescribed current causes no local content accumulation. The coordinate cutoff
q in the formulas is distinct from the conserved content variable.

Moreover `u*J_rho + z*J_z = 0`, so the field is tangent to every nested torus
u^2+z^2=constant. The construction describes closed-domain circulation; it
cannot silently represent transfer between recursive universe scales.

## Flux normalization

These are actual surface integrals with oriented normals:

| Cut | Normal | Integrated flux |
| --- | --- | ---: |
| Outer equatorial annulus, z=0 and R<=rho<=R+a | +z | -I |
| Inner equatorial annulus, z=0 and R-a<=rho<=R | +z | +I |
| Full meridional disk at phi=0 | +phi | T |

For example, the outer flux is
`-6*I/a^2 * integral_0^a u*(1-u^2/a^2)^2 du = -I`.
The meridional disk uses area element s ds dtheta, giving
`3*T/(pi*a^2) * integral_0^a 2*pi*s*(1-s^2/a^2)^2 ds = T`.
A graph route's signed current can therefore set I without an arbitrary
normalization factor. This is a flux matching interface, not yet a spatial
map from individual Yantra chambers or Tree edges to the torus.

## Mirror operations

A spatial mirror transforms a polar current vector by its pushforward.
It is distinct from reversal at fixed coordinates.

| Operation | Position map | Parameter map (I,T) |
| --- | --- | --- |
| Central inversion | (x,y,z)->(-x,-y,-z) | (-I,T) |
| Reflection in axial xz plane | (x,y,z)->(x,-y,z) | (I,-T) |
| Flow reversal | Position unchanged | (-I,-T) |

Tests check the Cartesian vector identities directly. All operations are
involutions and the two mirrors commute. No polarity-clock phase or physical
charge is inferred from these sign rules.

## Verification and use

```sh
python -m src.conservative_toroidal_field
python -m pytest -q tests/test_conservative_toroidal_field.py
```

Tests independently integrate all three cuts, verify Cartesian divergence
convergence under step refinement, differentiate the stream function, test
nested-surface tangency and mirror pushforwards, and check support boundaries,
the axis, reversed signs, zero current, and invalid parameters. The CLI states
the analytic flux values; the tests perform the numerical integration.

The legacy `toroidal_resonance_engine.py` and `toroidal_winding_engine.py`
remain compatibility/product interfaces with separate assumptions.

## Next scientific gates

An actual graph-to-volume coupling must specify where every graph channel maps,
which oriented surface measures its flux, and whether a local interpolation
preserves divergence. A dynamical field additionally requires a stated action
or transport law. Physical units and experimental comparisons must be fixed
independently before interpreting content as a measured quantity.
