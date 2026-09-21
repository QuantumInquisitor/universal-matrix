# Falsification and Validation Program

## Status

The earlier version of this file contained numerical photon-delay and interferometer predictions that were not independently derived from the current canonical kernel. Those values are withdrawn as predictions.

A valid physical prediction must be generated from parameters fixed independently of the target measurement.

## 1. Parameter-separation rule

For every benchmark, divide inputs into:

- **structural parameters**, fixed by the mathematical architecture;
- **independently measured parameters**, determined from a different experiment;
- **target observable**, never used to tune the previous two categories.

If a parameter is adjusted to reproduce the target result, the result is calibration rather than prediction.

## 2. Gauge-wave benchmark

The weak open U(1) adapter predicts a lattice dispersion relation of the form

[
omega^2
=
4eta
sum_i
sin^2left(rac{q_i}{2}ight)
]

for appropriate transverse lattice modes.

A first laboratory benchmark should therefore test:

1. whether a physical implementation corresponding to the modeled link network can be identified;
2. whether (eta) is independently determined;
3. whether measured normal-mode frequencies follow the predicted lattice dispersion;
4. whether deviations agree with the predicted higher-order lattice terms.

### Falsification condition

Once (eta), geometry, and boundary conditions are fixed independently, statistically significant disagreement between measured and predicted mode frequencies beyond stated uncertainty falsifies that physical mapping.

## 3. Polarity/source benchmark

The polarity adapter maps

[
P=Asigmahat u
]

to

[
ho_{m pol}
=
-
ablacdot P.
]

A physical realization would need independent measurements for (A), (sigma), and orientation.

### Falsification condition

If the mapped physical source distribution does not reproduce the sign, conservation behavior, or measured field response predicted by the gauge solve under independently fixed parameters, the polarity-to-source interpretation is falsified.

## 4. Boundary-flux benchmark

The open solver requires the discrete divergence theorem

[
sum_xho
=
sum_{gin B_6}
Phi_g^{E,mathrm{outward}}.
]

### Falsification condition

For any claimed physical six-gate realization, measured enclosed source and measured total outward field flux must satisfy the mapped Gauss balance within uncertainty. Persistent incompatible results falsify that boundary realization.

## 5. Clock-shift benchmark

The current model can generate dimensionless phase-rate differences in the nested polarity extension, but it does not yet independently identify those rates with atomic clock frequency.

### Falsification condition

A clock-shift prediction should not be published until the phase-rate-to-clock mapping and all required parameters are fixed independently. Once they are, a disagreement with measured fractional frequency shift outside uncertainty falsifies that mapping.

## 6. Gravity comparison

The model does not include gravity or General Relativity as primitive equations.

That absence is not itself a falsification of General Relativity.

A valid discriminating test requires:

[
O_{m Matrix}

eq
O_{m GR}
]

for a predeclared observable, followed by an experiment precise enough to distinguish the two predictions.

## 7. Repository rule for new predictions

A new prediction document or test should include:

1. observable definition,
2. units,
3. source and boundary conditions,
4. parameter provenance,
5. numerical algorithm,
6. convergence/error analysis,
7. uncertainty,
8. prediction generated before target comparison,
9. explicit falsification threshold,
10. code path and test reference.

Predictions lacking these fields should be labeled exploratory rather than physical.
