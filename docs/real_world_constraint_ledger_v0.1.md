# Real-World Constraint Ledger v0.1

## Purpose

This document records external experimental constraints that any physical
interpretation of the Universal Matrix extensions must satisfy.

Internal mathematical consistency is not enough.

A proposed physical sector should be rejected or revised when it conflicts with
established measurement.

---

## 1. Gravitational-wave / light propagation speed

The multimessenger event GW170817 / GRB 170817A was observed in both
gravitational waves and gamma rays.

LIGO/Virgo report a 1.7 second arrival-time separation after propagation over
more than one hundred million light years.

Their public science summary gives a fractional gravity/light speed difference
bounded approximately by

[
-3	imes10^{-15}
lesssim
rac{c_g-c}{c}
lesssim
7	imes10^{-16}.
]

Source:

LIGO Scientific Collaboration, "Gravitational waves and gamma-rays from a
binary neutron star merger: GW170817 and GRB 170817A"

https://ligo.org/science-summaries/GW170817GRB/

### Design consequence

If the experimental content scalar participates directly in the sector
responsible for observed gravitational-wave propagation, its causal speed
should not be treated as an unconstrained independent parameter.

The simplest compatible architecture is

[
oxed{
c_chi
=
c_{m gauge}
}
]

to within the relevant observational tolerance.

Implementation:

`src/causal_cone_bridge.py`

This is a real-world constraint, not a canonical theorem.

---

## 2. Weak equivalence principle

The final MICROSCOPE mission result compared free-fall accelerations of titanium
and platinum test masses.

The reported Eötvös parameter was

[
eta(mathrm{Ti},mathrm{Pt})
=
[-1.5
pm2.3(mathrm{stat})
pm1.5(mathrm{syst})]
	imes10^{-15}.
]

Source:

P. Touboul et al., "MICROSCOPE Mission: Final Results of the Test of the
Equivalence Principle," Physical Review Letters 129, 121102 (2022).

DOI:

https://doi.org/10.1103/PhysRevLett.129.121102

### Design consequence

Any gravity-like Matrix sector must produce composition-independent free-fall
acceleration to approximately this precision in the tested regime.

The current massive-motion candidate family has

[
mathbf F=mmathbf a,
]

so test-particle acceleration is independent of inertial mass.

However, that is not yet enough.

Future couplings must also avoid significant dependence on:

- chemical composition;
- nuclear binding fraction;
- electromagnetic self-energy;
- material species;
- internal Matrix state labels

unless the predicted violation lies below experimental bounds.

---

## 3. Constraint labels

Future physical modules should classify external constraints as:

### REQUIRED

Failure rules out the proposed physical interpretation in the tested regime.

### TARGET

The model should reproduce the observation once the relevant sector exists, but
the current implementation is not yet complete enough for a direct test.

### OPEN

No current measurement uniquely fixes the parameter.

---

## 4. Current ledger

| Constraint | Status | Matrix implication |
|---|---|---|
| Gauge/content causal speed equality | REQUIRED if content field represents observed gravity-wave sector | Prefer one causal cone |
| Composition-independent free fall | REQUIRED for gravity-like interpretation | Coupling to test bodies must be universal |
| Canonical routing identities | INTERNAL REQUIRED | Exact finite algebra |
| Open Gauss compatibility | INTERNAL REQUIRED | Six-face source/flux conservation |
| Physical seconds per routing tick | OPEN | Must be independently identified |
| Content field coupling (kappa_{mathcal C}) | OPEN | Must be measured or derived |
| Clock coupling (g_chi) | OPEN | Must be measured or derived |
| Massive-motion branch sign | OPEN | Needs action principle |
| Scalar/tensor gravitational-wave content | TARGET | Scalar field alone is insufficient |

---

## 5. Repository rule

No future document should claim agreement with gravity experiments merely
because the model contains:

- a (1/r) scalar potential;
- a (1/r^2) gradient;
- slower clocks near positive content;
- ray bending toward a source.

Those are structural ingredients only.

A gravity claim requires simultaneous quantitative agreement with independent
clock, free-fall, trajectory, lensing, and wave-propagation measurements using
the same parameter set.

---

## Status

This ledger turns external experiment into a design constraint for the ongoing
model reconstruction.


---

## 6. Solar-system spatial-response constraint

Weak-field light deflection and Shapiro delay depend on the PPN parameter

[
gamma.
]

A Living Reviews analysis explains that the clock/time contribution alone gives
only part of the full deflection, while the spatial-curvature contribution
provides the remaining (gamma)-dependent part.

The Cassini measurement is commonly quoted as

[
gamma-1
=
(2.1pm2.3)	imes10^{-5}.
]

References:

- C. M. Will, "The Confrontation between General Relativity and Experiment,"
  Living Reviews in Relativity.
- NASA Technical Reports Server summary of Cassini PPN gamma measurements.

### Matrix consequence

The current content-clock-only optical index corresponds to an effective

[
gamma_M=0,
]

which predicts only half the required leading weak-field light deflection.

Therefore this incomplete scalar clock model is ruled out as a complete
description of observed solar-system gravity.

A viable gravity-like extension must derive a spatial response satisfying

[
oxed{
gamma_Mapprox1
}
]

within the relevant experimental precision.

Implementation:

`src/weak_field_ppn_bridge.py`

This is now a REQUIRED constraint for any claim that the content sector
reproduces solar-system gravity.


---

## 7. Strong-field shadow/ring constraint

The simplest point-source reciprocity exponential metric predicts

[
b_c
=
2e,mu,
]

while Schwarzschild gives

[
b_{c,m Schw}
=
3sqrt3,mu.
]

The fractional difference is approximately

[
rac{2e}{3sqrt3}-1
approx
4.6%.
]

The Event Horizon Telescope Collaboration reports that the observed Sgr A*
image size is within approximately 10 percent of Kerr predictions after
calibrating the relation between the observed emission ring and the geometric
shadow.

Reference:

Event Horizon Telescope Collaboration, "First Sagittarius A* Event Horizon
Telescope Results. VI. Testing the Black Hole Metric," ApJL 930, L17 (2022).

https://eventhorizontelescope.org/publications/first-sagittarius-event-horizon-telescope-results-vi-testing-black-hole-metric

### Current implication

The 4.6 percent critical-impact-parameter difference is not obviously excluded
by image-size agreement alone at that quoted level.

This is **not** evidence that the exponential metric is correct.

A proper comparison requires:

- ray tracing through the exact candidate geometry;
- accretion-flow/plasma emission models;
- mass-to-distance uncertainty propagation;
- spin dependence;
- comparison to M87* and Sgr A* simultaneously;
- horizonless/throat boundary conditions.

The EHT analysis also constrains alternatives to an event horizon; thermal
surfaces are ruled out in their Sgr A* analysis and fully reflective surfaces
are disfavored.

A throat geometry therefore needs its own physically specified absorption,
transmission, or reflection law before it can be compared fairly with EHT data.

Status: TARGET / STRONG-FIELD TEST.
