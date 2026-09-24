# Charged Matter 3D Persistence v0.1

## Status

This layer performs the first direct three-dimensional survival test of the controlled below-threshold charged radial branch after correcting the lattice-spacing mismatch.

A finite simulation window is evidence about the numerical classical field model. It is not proof of an elementary particle, quantum stability, or experimental reality.

## Candidate

The seeded continuation branch reaches a controlled point near

$$
A_0=1,
\qquad
\omega\approx0.80015,
$$

with

$$
E/Q<1.
$$

That radial solution is mapped onto a cubic lattice with

$$
h=0.5.
$$

The real-time dynamics uses the same $h$ in the Laplacian, energy, charge, and radius diagnostics.

## Mapping consistency

Before evolution, the Cartesian lattice $E/Q$ is compared with the radial continuum value.

This is a discretization check.

A mapping that changes the ratio substantially is rejected as a poor representation of the radial candidate.

## Survival diagnostics

The persistence report tracks

* relative energy drift,
* relative charge drift,
* peak-amplitude ratio,
* RMS-radius ratio.

The default finite-window criteria are deliberately explicit:

$$
|\Delta E/E|\le10^{-5},
$$

$$
|\Delta Q/Q|\le10^{-10},
$$

with peak and radius remaining within ten percent of their initial values.

These are numerical survival criteria, not universal physical constants.

## Perturbation test

A smooth localized radial perturbation is applied through

$$
\Phi\rightarrow
\Phi
\left[
1+
\epsilon
e^{-r^2/(2w^2)}
\right],
$$

and the same real factor is applied to the initial momentum.

The default test uses

$$
\epsilon=0.005,
\qquad
w=1.
$$

The perturbed configuration is then judged from its own conserved energy and charge and from whether its size and peak remain bounded.

## Interpretation

If both the exact mapped profile and a nearby perturbed profile survive the same finite window, the result is stronger than

* existence of a variational ansatz,
* convergence of a radial BVP,
* or an energy-per-charge inequality alone.

It demonstrates finite-time nonlinear persistence in the current classical lattice model.

It still does not establish asymptotic stability or identify the excitation with a known particle.

## Next creator question

If this finite-window persistence test passes, the next questions are:

1. how survival changes as the run time is increased,
2. how large a perturbation can be tolerated,
3. whether the branch has a turning-point stability boundary,
4. how dynamical compact U(1) gauge fields change the result,
5. whether the localized mode survives coupling to the content/reciprocity sector,
6. whether any dimensionless observables can be fixed without calibration.
