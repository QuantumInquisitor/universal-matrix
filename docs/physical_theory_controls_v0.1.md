# Established physical theory controls, version 0.1

These two optional controls test explicit predictions before connecting any
theory to the Matrix geometry. They do not fit the geometry, validate M4, infer
a material, or identify a physical ring mode. The existing toroidal and
piezoelectric constructions are unchanged.

## Hydrogen: infinite-nucleus and reduced-mass Rydberg approximations

For field-free, nonrelativistic hydrogen-1, use

\[
R_H=\frac{R_\infty}{1+m_e/m_p},\qquad
\lambda_{\rm vacuum}^{-1}=R_H(n_l^{-2}-n_u^{-2}).
\]

The infinite-nucleus control replaces `R_H` with `R_infinity`. The supplied
[CODATA 2022 constants](https://physics.nist.gov/cuu/pdf/wall_2022.pdf) are
`R_infinity = 10973731.568157 m^-1` and `m_e/m_p = 5.446170214889e-4`.
Their standard uncertainties are respectively `0.000012 m^-1` and `9.4e-15`.
The resulting reduced-mass constant is approximately `10967758.340277308 m^-1`.
No constant is fitted to the reference rows. The leading reduced-mass term and
the additional relativistic/radiative contributions are described in
[Jentschura et al., 2009, equations 3–4](https://www.nist.gov/document/canjphys2009pdf).

The numerical comparison uses the eight vacuum entries in the
[NIST hydrogen strong-line table](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable2.htm),
with explicit upper quantum numbers `8,7,6,5,4,3,2,2` and lower number one.
These are declared Lyman-series assignments, not values chosen by a nearest
match. The `n=2..5` configurations appear in the
[persistent table](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3.htm).
The two `n=2` rows remain separate references despite sharing one prediction.

For these eight entries, the unweighted wavelength RMS discrepancy is about
`533.242702 ppm` for the infinite nucleus and `11.1409782 ppm` with reduced
mass. The latter discrepancies remain approximately `8.90–13.34 ppm`.
This improvement demonstrates the importance of nuclear motion at this
approximation level. The remaining discrepancy is not statistical evidence
against the complete theory: fine structure, Lamb shift, hyperfine structure,
and other corrections are absent. No linewidth or intensity is predicted.

The NIST values are evaluated references: its
[hydrogen notes](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable1.htm)
identify Ritz fine components and weighted-average multiplets. Comparing with
them is not an independent new observation. Unknown row uncertainties are
not treated as zero; this RMS is descriptive, not a chi-square fit. All air
entries are counted and excluded because converting air wavelength requires
an explicit refractive-index convention. `c/lambda_air` is not silently used
as a vacuum frequency.

## ABC: a periodic curl eigenfield

[Dombre et al., 1986, equations 1.1 and 2.1](https://doi.org/10.1017/S0022112086002859)
give the Arnold–Beltrami–Childress field. In a cube of side `L` with opposite
faces identified, set `k=2*pi*n/L`, with positive integer `n`, and

\[
\mathbf B=(a\sin kz+c\cos ky,\quad b\sin kx+a\cos kz,\quad
c\sin ky+b\cos kx).
\]

Direct differentiation gives `div B = 0`, `curl B = k B`, and
`Laplacian B = -k^2 B`. This is a periodic three-torus, not the surface or
solid interior of an embedded doughnut. Truncating the field onto an annular
device does not establish its wall or port boundary conditions. The field
can be treated as a kinematic mathematical control. If amplitudes are tesla,
coordinates/meters and permeability/H per meter are supplied, the explicit
magnetostatic interpretation gives `J=k B/mu` and `J cross B=0`. It supplies
no stability, material response, or dynamo-growth claim.

The implementation samples a shifted periodic grid and takes independent
centered differences. For this single wave number the derivative symbol is
`sin(k*h)/h`, so the expected relative curl discrepancy is
`1-sin(k*h)/(k*h)`. With `L=2*pi`, `n=1`, and grids `16,32,64`, its values are
approximately `0.0255046416`, `0.00641314886`, and `0.00160560696`. Refinement
therefore approaches second order. The same calculation independently tests
divergence and the normalized force-free residual.

Periodic quadrature checks `mean(|B|^2)=a^2+b^2+c^2`. For a curl eigenfield,
`A=B/k` is a periodic vector potential, giving magnetic helicity
`integral A dot B = L^3*(a^2+b^2+c^2)/k`. The audit reports this candidate
helicity conditionally on its curl check; arbitrary input fields do not gain
a valid vector potential merely by dividing by a declared eigenvalue.

Two negative controls are necessary: a constant field offset remains
divergence-free but generally destroys the force-free property, while an
added gradient creates detectable divergence. Thus solenoidality alone is
not mistaken for a force law.

An additional derived parity control reflects `x` using `S=diag(-1,1,1)`.
Transporting an axial magnetic field gives `B'(y)=det(S) S B(S^-1 y)`.
The curl eigenvalue and magnetic helicity reverse sign; squared-field integral
and force-free property remain. Tests verify the sign with numerical curl.
This is an isometric reflection, not a spherical inversion or continuous
inside-out deformation. General geometric transformations do not preserve
the Euclidean curl-eigenfield equation automatically.

## Reproduction and scope

Run `python -m src.physical_theory_controls` for the reference report and
`python -m pytest tests/test_physical_theory_controls.py -q` for the controls.
The report reads `src/reference_data/nist_hydrogen_lines.json`; the tests
also use independent authoritative wavelength fixtures. Inputs require
finite values, explicit quantum-number/model choices and wavelength media,
and a declared curl wave number below the grid Nyquist frequency.

These controls add spectral approximation and curl/helicity checks beyond
the existing route-collision, Piola-flux, and single-mode piezoelectric tests.
Any proposed link among their dimensional scales still needs its own
equations, boundary conditions, and measurements.
