# Physical Extension v0.1: Nested Polarity and Scale Dynamics

This document specifies the first non-gravitational dynamical extension built on top of Canonical Kernel v0.4. It is deliberately separated from the kernel because the additional equations are physical-model postulates rather than consequences of the finite core.

## 1. Layer state

Each nested micro-to-macro layer is represented by

[
X_ell=(n_ell,sigma_ell,phi_ell,A_ell),
]

where

- (n_ellinmathbb{Z}_{108}) is the canonical core state,
- (sigma_ellin{-1,+1}) is polarity,
- (phi_ell) is phase,
- (A_ellge0) is dimensionless modeled amplitude.

The polarity flip is

[
Q(n,sigma)=(n+54,-sigma)
]

and obeys

[
Q^2=I.
]

Routing is polarity-directed:

[
sigma=+1Rightarrow T_{21},
qquad
sigma=-1Rightarrow T_{-21}=T_{87}.
]

## 2. Self-similar scale hierarchy

If each neighboring layer is related by one common scale ratio (lambda>0), self-similarity implies

[
R_ell=R_0lambda^ell.
]

This geometric law follows directly from the constant-ratio postulate. The v0.4 kernel does not determine the numerical value of (lambda).

To allow dynamics across scales, define a dynamic exponent (z) by

[
omega_ell=omega_0lambda^{-zell}.
]

The special case (z=1) corresponds to characteristic time proportional to characteristic length, as would occur under an assumed scale-independent propagation speed. That interpretation is an additional physical postulate, not a theorem of the kernel.

The ratio between neighboring intrinsic rates is therefore

[
rac{omega_{ell+1}}{omega_ell}=lambda^{-z}.
]

This gives a dimensionless observable before any conversion to SI units.

## 3. Directed inter-layer injection

A physically useful exchange law must at minimum distinguish direction. The earlier symmetric ansatz was therefore replaced.

The current minimal antisymmetric form is

[
J_{ell,ell+1}
=
kappasqrt{A_ell A_{ell+1}}
rac{sigma_ell-sigma_{ell+1}}{2}
cos(phi_ell-phi_{ell+1}).
]

It has the following exact structural properties:

[
J(a,b)=-J(b,a),
]

so reversing source and target reverses the flow;

[
sigma_a=sigma_bRightarrow J(a,b)=0,
]

so the present minimal model exchanges amplitude only across a polarity difference; and a global polarity reversal reverses the flow direction.

The exchange update is conservative:

[
A_ell' = A_ell-J_{ell,ell+1},
qquad
A_{ell+1}' = A_{ell+1}+J_{ell,ell+1},
]

subject to bounds preventing negative amplitude. Therefore nearest-neighbor exchange conserves total modeled amplitude.

This is a Russell-inspired compression/expansion interchange model. The symmetry constraints reduce arbitrariness, but the equation remains a physical-extension ansatz. It is not claimed to be Maxwell's law or an established electromagnetic law.

## 4. Phase velocity as the candidate clock variable

A clock is fundamentally a periodic phase process. Therefore the extension no longer defines its candidate clock quantity from an arbitrary amplitude telemetry function. It uses phase velocity.

For layer (ell), the intrinsic signed phase rate is

[
dotphi_ell^{(0)}
=
sigma_ellomega_ell.
]

A neighboring layer contributes the dimensionless correction

[
deltadotphi_{ell j}
=
sigma_ellkappa
(-sigma_ellsigma_j)
sqrt{rac{A_j}{A_ell}}
cos(phi_ell-phi_j).
]

The modeled phase velocity is then

[
dotphi_ell
=
sigma_ellomega_ell
+
sum_{jsimell}deltadotphi_{ell j}.
]

This makes differential rate behavior a consequence of explicit phase dynamics.

For any two positive reference rates (r_a,r_b), define the dimensionless differential rate

[
mathcal R(a,b)
=
rac{r_b-r_a}{r_a}.
]

If a later physical postulate identifies the magnitude of the Matrix phase rate with a physical oscillator frequency up to one universal conversion factor, then that factor cancels in the ratio and

[
rac{Delta f}{f}
=
rac{|dotphi_b|-|dotphi_a|}{|dotphi_a|}.
]

This cancellation is important: a fractional frequency-shift prediction can in principle be dimensionless and need not require an arbitrary seconds-per-tick calibration. However, the identification between Matrix phase velocity and physical clock frequency is still a physical hypothesis requiring independent justification.

## 5. What is now derived and what remains free

Derived once the extension postulates are accepted:

- geometric scale law (R_ell=R_0lambda^ell);
- neighboring intrinsic-rate ratio (lambda^{-z});
- polarity-directed routing;
- involutive polarity reversal;
- antisymmetry of inter-layer flux;
- conservation of total modeled exchange amplitude;
- dimensionless phase-rate ratios;
- possibility of nonzero differential rates without inserting a gravitational potential.

Still free or unestablished:

- the numerical scale ratio (lambda);
- the dynamic exponent (z);
- coupling strength (kappa);
- the physical meaning of amplitude (A);
- the physical origin and boundary conditions for phase and polarity;
- whether (|dotphi|) corresponds to an atomic clock frequency;
- how matter and electromagnetic field measurements map into the layer state;
- whether this dynamics reproduces any established gravitational observation.

## 6. Immediate falsification program

The next defensible step is not to fit (lambda,z,kappa) to a known clock-shift measurement.

Instead, one independent physical identification must fix or constrain these quantities. Only then should the predicted dimensionless rate ratio be compared with a clock experiment.

A useful candidate is to derive (lambda) or (z) from an independently measurable electromagnetic or resonant scaling relation. If the parameters remain adjustable specifically to reproduce gravitational-redshift data, the model has not made an independent prediction.

## Status

The Universal Matrix now has a mathematically explicit mechanism for:

[
	ext{polarity reversal}
+
	ext{micro/macro scaling}
+
	ext{directed conservative exchange}
+
	ext{differential phase rate}.
]

It still does not yet have a parameter-free physical prediction.


## 7. Independent electromagnetic parameter identification

The extension should not determine its free parameters from the gravitational or clock observable it is meant to explain. Two parameters can instead be constrained from independent resonator physics.

### 7.1 Dynamic exponent from electromagnetic scale similarity

For geometrically similar, nondispersive electromagnetic structures with unchanged dimensionless material parameters, Maxwell scale invariance gives

[
omega propto R^{-1}.
]

Comparing this with

[
omega_ell=omega_0lambda^{-zell}
]

selects

[
oxed{z=1}
]

for that specific electromagnetic similarity class.

This does not prove that every Universal Matrix layer is an electromagnetic resonator. It states a falsifiable bridge assumption: if the nested layers are physically realized as geometrically similar electromagnetic resonant structures, then (z) is no longer a free fit parameter.

### 7.2 Scale ratio from geometry

If two adjacent physical realizations of the nested structure have independently measured characteristic scales (R_ell) and (R_{ell+1}), then

[
oxed{lambda=rac{R_{ell+1}}{R_ell}}.
]

Thus (lambda) should be measured from geometry, not chosen to fit a clock experiment.

### 7.3 Coupling from normal-mode splitting

For two nominally identical weakly coupled resonators with measured split mode frequencies (omega_-) and (omega_+), the standard matched two-mode relation gives a physical coupling rate

[
kappa_{m phys}=rac{omega_+-omega_-}{2}
]

and uncoupled center frequency

[
omega_0=rac{omega_++omega_-}{2}.
]

Therefore the normalized dimensionless coupling used by the Matrix extension can be fixed as

[
oxed{
kappa
=
rac{kappa_{m phys}}{omega_0}
=
rac{omega_+-omega_-}{omega_++omega_-}
}.
]

This provides an independent laboratory route for determining (kappa).

### 7.4 Consequence for the gravity benchmark

Under the electromagnetic-resonator bridge hypothesis:

- (z=1) is fixed by scale similarity;
- (lambda) is measured geometrically;
- (kappa) is measured from resonator mode splitting.

The nested dynamics can then be run with those values held fixed. Only after that should its predicted fractional phase-rate shift be compared with a clock/redshift experiment.

That creates the required separation between parameter identification and target validation.

## 8. Remaining physical unknowns

Even after (z), (lambda), and (kappa) are independently constrained, the model still needs:

- an experimentally defined physical object corresponding to one Matrix layer;
- a measured quantity corresponding to the modeled amplitude (A_ell);
- a rule for initializing phase and polarity from laboratory conditions;
- evidence that Matrix phase rate maps to the frequency of a physical clock or resonator;
- a prediction for a new experimental configuration made before measurement.

Those are now the principal unresolved physical steps.
