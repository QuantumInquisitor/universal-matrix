# Polarity-Aware Rotor Transition v0.2

## Status

This document describes an experimental ontology-to-dynamics bridge. It does not alter the exact canonical Z_108 kernel and does not claim a derived law of nature.

## Purpose

The repository already contains two pieces that should be composed rather than duplicated:

1. a gauge-covariant nearest-neighbor rotor Hamiltonian,
2. an exact canonical polarity/phase identity in which the polarity branch can be represented by a pi phase offset.

The v0.2 transition joins those layers while adding a hard safeguard against double counting canonical polarity.

## Canonical branch representation

For an independent local phase phi_x and canonical polarity bit p_x in {0,1}, define

$$
\phi_x^{\mathrm{eff}} = \phi_x + \pi p_x.
$$

Then each nearest-neighbor rotor link uses

$$
\Delta_{xy}
=
\phi_y^{\mathrm{eff}}
-
\phi_x^{\mathrm{eff}}
+
\theta_{xy}.
$$

The interaction is

$$
H_{\mathrm{int}}
=
\kappa
\sum_{\langle xy\rangle}
\left[
1-\cos(\Delta_{xy})
\right].
$$

The kinetic term remains

$$
H_{\mathrm{kin}}
=
\sum_x
\frac{\pi_x^2}{2I}.
$$

## Exact polarity consequences

When two sites have equal independent base phase and equal link phase:

* equal canonical branch gives Delta = 0 and minimum link energy,
* opposite canonical branch gives |Delta| = pi and maximum single-link rotor energy 2 kappa.

A global branch flip p_x -> 1-p_x adds the same pi shift to every site. All link differences are therefore unchanged modulo 2 pi. The Hamiltonian and forces are exactly invariant under a global polarity reversal.

A local branch flip changes only the links incident on the flipped site.

## Gauge covariance

The gauge convention remains

$$
\phi_x \rightarrow \phi_x + \alpha_x,
$$

$$
\theta_{xy}
\rightarrow
\theta_{xy}
+
\alpha_x
-
\alpha_y.
$$

The canonical branch bit is not a gauge variable. Therefore Delta_xy is gauge invariant.

## Double-counting safeguard

Two phase representations are explicitly separated.

### independent

Use this when the phase variable is independent of canonical polarity. The exact branch offset pi p_x is applied.

### canonical_clock

Use this when the supplied phase already represents the canonical polarity clock. No additional branch offset is applied.

This prevents the same half-cycle polarity reversal from being represented twice.

## Dynamics

The continuous-time candidate Hamiltonian uses the same nearest-neighbor rotor force as the existing local transition module. Numerical evolution uses a second-order symplectic leapfrog update.

The weak-field lattice speed remains

$$
c_{\mathrm{lat}}^2 = \frac{\kappa}{I}.
$$

No mapping from lattice units to SI length or time is asserted.

## What this improves

This layer removes the need for an extra phenomenological polarity-force term when canonical polarity is already representable as an exact phase offset.

It makes polarity enter the rotor Hamiltonian through one mathematically consistent channel rather than through two independently tunable channels.

## What remains open

The model does not yet determine:

* the physical lattice spacing,
* the physical time represented by one model-time unit,
* the values of kappa or I,
* whether long-wavelength modes reproduce a known relativistic field theory,
* whether stable localized excitations reproduce particle properties,
* whether alternating micro-to-macro orientation should modify canonical branch assignment, link orientation, or scale coupling.

## Next creator question

The next high-value step is to analyze the normal modes of this polarity-aware rotor lattice and determine whether the exact branch structure opens, closes, or shifts collective-mode bands while preserving the required continuum symmetries.
