# Spherical projection and virtual-work reference v0.1

This module checks an algebraic connection between symmetric stress/strain
tensors and their projections onto a sphere of orientations. It provides a
small numerical control for future tensor material work. It does not implement
concrete M4 damage, fit a material, predict piezoelectric coupling, or derive a
physical ring from the Matrix kernel.

## Relation to engineering microplane M4

[Bažant, Caner, Carol, Adley and Akers (2000), Part I](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%282000%29126%3A9%28944%29)
describe microplane strains as projections of the continuum strain and obtain
continuum stresses through virtual work. Their particular improvement includes
a work-conjugate volumetric/deviatoric split and modified stress-strain
boundaries, friction and unloading behavior. The volumetric/deviatoric idea
itself should not be attributed exclusively to M4. The source is a constitutive
model for concrete, not a general theory of matter.

[Caner and Bažant (2000), Part II](https://doi.org/10.1061/(ASCE)0733-9399(2000)126:9(954))
provides algorithm and calibration against concrete test data. Such calibration
has a material and loading domain; it does not establish piezoelectric constants.
The [OOFEM material manual, section 1.6.8](https://www.oofem.org/resources/doc/matlibmanual/matlibmanual.pdf)
allows 21, 28 or 61 microplanes and notes that its M4 implementation needs
element-size adjustment for softening and uses elastic stiffness when a tangent
is unavailable. Thus 21 is an integration choice, not a universal count of
physical planes. [OOFEM's projection interface](https://www.oofem.org/resources/doc/oofemrefman/html/classoofem_1_1MicroplaneMaterial.html)
also distinguishes normal, volumetric, deviatoric and tangential components.

The equations below are an elementary, independently stated projection control.
Here stress is prescribed and its tractions are projected. In a constitutive
microplane model, the plane stresses instead follow material laws and history;
they need not equal projections of the final macroscopic stress. Passing this
control therefore does not validate those constitutive laws.

## Conventions and identities

Let sigma and epsilon be real, symmetric 3 by 3 tensors. Sigma is stress in Pa;
epsilon is infinitesimal tensorial strain, dimensionless. In particular,
epsilon_xy = gamma_xy/2 when gamma is engineering shear strain. Let n be a unit
normal and define the normalized full-sphere average

\[
\langle f\rangle = \frac{1}{4\pi}\int_{S^2} f(n)\,d\Omega.
\]

The projection and its normal/tangent decomposition are

\[
t=\sigma n,\quad e=\epsilon n,\quad
t_N=n\cdot t,\quad e_N=n\cdot e,
\]

\[
t_T=t-t_Nn,\qquad e_T=e-e_Nn.
\]

Tangential components are vectors in the plane, so an arbitrary choice of two
tangent axes is unnecessary. Pointwise orthogonality gives

\[
t\cdot e=t_Ne_N+t_T\cdot e_T.
\]

The spherical moments used by this control are

\[
\langle n_i\rangle=0,\qquad
\langle n_i n_j\rangle=\frac{\delta_{ij}}{3},
\]

\[
\langle n_i n_j n_k n_l\rangle
=\frac{\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}
+\delta_{il}\delta_{jk}}{15}.
\]

For symmetric tensors, the second moment directly proves

\[
3\langle t\cdot e\rangle=\sigma:\epsilon,
\qquad
3\langle\operatorname{sym}(t\otimes n)\rangle=\sigma.
\]

Thus the factor **three** belongs to a normalized sphere average. An
unnormalized hemisphere integral of these even work/reconstruction integrands
would instead have coefficient 3/(2 pi). Mixing normalized weights and that
integral coefficient changes the result.

Replacing epsilon by a virtual strain variation gives virtual work density;
replacing it by a strain rate gives power density. The present API accepts strain,
so sigma:epsilon has units Pa = J/m³. It is not automatically stored elastic
energy: for a separate linear elastic proportional-loading model the stored
energy has the additional factor one-half. No such constitutive law is supplied.

The fourth moment provides an independent check on the partition:

\[
3\langle t_N e_N\rangle
=\frac{(\operatorname{tr}\sigma)(\operatorname{tr}\epsilon)
+2\sigma:\epsilon}{5},
\]

\[
3\langle t_T\cdot e_T\rangle
=\frac{3\sigma:\epsilon
-(\operatorname{tr}\sigma)(\operatorname{tr}\epsilon)}{5}.
\]

For sigma = p I and epsilon = a I, all work is normal and equals 3 p a.
For an aligned uniaxial pair, the normal/tangent fractions are 3/5 and 2/5.
For a tensorial pure-shear pair they are 2/5 and 3/5. Individual contributions
can be negative for arbitrary prescribed stress/strain pairs; they are work
pairings, not independent nonnegative stored energies.

## Quadrature and numerical evidence

`spherical_quadrature` uses Gauss-Legendre points for z = cos(theta) and a
uniform periodic azimuth grid, with a fixed fractional azimuth offset. If the
one-dimensional Gauss weights are w_a and there are N_phi azimuths, each product
weight is w_a/(2 N_phi); the total is one. This is **not** OOFEM's 21-plane rule.

The default orders (4,12) give 48 sphere directions. The report compares (2,4),
(3,8) and (4,12). The coarse rule already integrates the second moment and can
pass total work and stress reconstruction while failing the fourth moment and
the normal/tangent partition. Higher orders resolve these polynomial identities
to floating-point precision. That result does not certify angular integration
of nonlinear damage laws or arbitrary anisotropic material functions.

Moment errors are maximum absolute component errors. Work error is normalized
by the product of the stress and strain Frobenius norms, which remains useful
when the work pairing is zero. Reconstruction error uses the stress norm. Zero
stress or strain has an explicit zero-error convention. Inputs are checked for
finite real values and symmetry to relative tensor scale 1e-12; accepted
roundoff asymmetry is removed. The implementation rejects detected unresolved
arithmetic instead of presenting a nonfinite or underflowed nonzero work density
as a result. These checks are numerical range guards, not measurement accuracy.

## APIs, checks and next material step

Implementation: `src/microplane_projection_reference.py`.
Tests: `tests/test_microplane_projection_reference.py`.
Run `python -m src.microplane_projection_reference` for the bounded report.

The public APIs are `OrientationQuadrature`, `spherical_quadrature`,
`project_tensors` and `audit_projection`. The audit returns moments, work
contributions, normalized residuals and reconstructed stress. Tests compare
analytic hydrostatic, uniaxial and shear results, tensor rotation covariance,
quadrature orders, an intentionally nonisotropic rule, orthogonal/zero work
pairs, input rejection and work scaling. The test suite checks implementation
identities; it is not experimental material validation.

The useful next material step is to supply a measured material tensor with its
symmetries, coordinate axes and units, and check its rotated response and work
conjugacy. A piezoelectric ring would additionally require elastic, dielectric
and piezoelectric constitutive data, electrical and mechanical boundary
conditions, geometry, losses and a justified spatial-to-mode reduction. The
existing single-mode piezoelectric reference remains a separate approximation.
