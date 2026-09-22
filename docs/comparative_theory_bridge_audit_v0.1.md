# Comparative Theory Bridge Audit v0.1

## Purpose

This audit compares Canonical Kernel v0.4 and Physical Extension v0.1 with selected established or actively researched mathematical frameworks. A match means that a reusable mathematical structure exists. It does **not** mean that the Universal Matrix has derived or reproduced the external theory.

The implementation surface is `src/theory_bridge.py`.

## Executive classification

| Framework | Compatibility | What maps now | What does not map yet |
|---|---|---|---|
| Compact dimensions / Kaluza-Klein / string mode structure | Strong mathematical analogy | finite cyclic modes, Fourier basis, winding number | worldsheet, string tension, critical dimensions, supersymmetry |
| M-theory | Weak structural analogy | only generic nested/higher-dimensional bookkeeping | 11D Lorentzian dynamics, supersymmetry, M2/M5 branes, 3-form field, 11D supergravity limit |
| Loop quantum gravity | Partial graph analogy | finite graph substrate | SU(2) spin labels, intertwiners, area/volume spectra, Hamiltonian constraint |
| Causal-set approach | Strong history analogy | discrete time-unwrapped event order | Lorentz-invariant sprinkling/continuum recovery, causal-set action/dynamics |
| Holography / tensor networks | Partial scale analogy | nested layer index as scale coordinate | Hilbert-space factorization, entanglement entropy, isometries, AdS/CFT duality |
| Lattice gauge theory | Strong mathematical bridge | group-valued link phases, Wilson-loop holonomy | action, matter fields, non-Abelian gauge groups, continuum limit, physical coupling |
| Regge/CDT discrete geometry | Weak | finite discreteness only | simplices, lengths, deficit angles, Lorentzian triangulations |

## 1. String theory and compact dimensions

String theory uses periodic worldsheet fields and compact dimensions that support quantized momentum and winding sectors. Witten's 1995 analysis is central to the relation between Type IIA string theory and an eleven-dimensional strong-coupling description whose low-energy limit is eleven-dimensional supergravity.

The Universal Matrix already contains exact finite cyclic structures:

```
E = T9      order 12
T = T21     order 36
```

Every finite cyclic orbit `Z_N` has an exact discrete Fourier basis

\\[
psi_k(n)=N^{-1/2}exp(2pi i kn/N).
\\]

This is a legitimate finite analogue of mode decomposition on a compact circle.

For the routing orbit the selected step has winding

\\[
36(21)/108=7.
\\]

The inverse routing has winding (-7) when represented by the signed displacement (-21).

### What can be imported safely

- discrete momentum/mode labels from the Fourier dual of `Z_12` and `Z_36`;
- winding labels of closed routing cycles;
- a later compactification adapter if an actual higher-dimensional geometry is specified.

### What cannot be claimed

A finite cyclic orbit is not a string. The Matrix currently has no worldsheet action, string tension, Virasoro constraints, supersymmetry, or critical-dimension consistency conditions.

## 2. M-theory

M-theory is connected to eleven-dimensional supergravity and to strong-coupling limits of Type IIA string theory. It contains extended objects such as membranes/branes and substantially more structure than an arbitrary 11-component vector.

The repository's historical `m_theory_router.py` therefore should **not** be treated as an implementation of M-theory merely because it uses eleven coordinates.

### Current mapping status

There is no strong mathematical equivalence.

A future M-theory adapter would require at minimum:

- an 11-dimensional Lorentzian state geometry;
- supersymmetric degrees of freedom;
- M2 and M5 brane state objects;
- an analogue of the eleven-dimensional 3-form gauge field;
- a demonstrated low-energy reduction corresponding to 11D supergravity.

Until then, "M-theory" should be treated as an exploratory comparison label, not a property of the engine.

## 3. Loop quantum gravity and spin networks

Loop quantum gravity uses spin-network states labeled by SU(2) representations. Rovelli and Smolin showed that spin-network-related states support discrete area and volume spectra.

The Matrix has a finite graph once routing edges and optional register-coupling edges are introduced. This gives a graph substrate, but not a spin network.

### Possible adapter

A future experimental adapter could assign

\\[
j_ein{0,	frac12,1,	frac32,ldots}
\\]

to Matrix edges and intertwiners to vertices, then compute standard spin-network-inspired combinatorial observables.

### Missing

Without SU(2) representation labels and intertwiners there is no LQG area or volume operator. Node count alone is not quantum geometry.

## 4. Causal-set mapping

A cyclic state space cannot itself be a causal set because a causal order must not contain causal cycles.

However, the **time-unwrapped history** can be:

\\[
e_t=(t,n_t).
\\]

Define

\\[
e_tprec e_s quad	ext{iff}quad t<s.
\\]

Core states may repeat after a 36-step closure while the events remain distinct because their time labels differ.

This gives a finite locally ordered event history and is implemented by `causal_history()`.

### Important limitation

This is only a causal-history adapter. It does not establish Lorentz invariance, continuum recovery, or the stochastic structures used in causal-set quantum gravity.

## 5. Holography and tensor networks

Maldacena's AdS/CFT proposal relates certain conformal field theories to string/supergravity descriptions in Anti-de Sitter backgrounds. Tensor-network work, particularly MERA-inspired constructions, has shown how an extra network direction may encode scale.

The nested Matrix hierarchy

\\[
mathcal T_0leftrightarrowmathcal T_1leftrightarrowcdots
\\]

therefore has a legitimate **scale-network analogy**.

The engine now exposes nearest-neighbor scale edges

\\[
(0,1),(1,2),ldots.
\\]

### What is missing for holography

- a quantum Hilbert space on each layer;
- tensor-factor structure;
- entanglement entropy;
- isometric tensors;
- a boundary quantum theory;
- an emergent bulk metric;
- an AdS/CFT dictionary.

Thus "micro-to-macro layers" can map to a scale-network graph, but cannot currently be called holographic duality.

## 6. Lattice gauge theory: strongest immediate bridge

This is presently the most useful imported mathematical structure.

In lattice gauge theory, group-valued variables live on oriented links and Wilson loops measure holonomy around closed paths.

The Matrix already has oriented routing links. We can attach a U(1) variable

\\[
U_{ij}=e^{i	heta_{ij}}.
\\]

Under a local gauge transformation

\\[
	heta_{ij}ightarrow
	heta_{ij}+alpha_i-alpha_j,
\\]

the closed-loop product

\\[
W(C)=prod_{(ij)in C}U_{ij}
\\]

is invariant.

This is now implemented and regression-tested in `theory_bridge.py`.

### Why this matters

The phase variable already introduced in Nested Polarity Dynamics can now be separated into:

1. **site phase**, associated with a layer/state;
2. **link phase**, associated with interaction/transport;
3. **loop holonomy**, a gauge-invariant observable.

That is a much cleaner foundation for the proposed electromagnetic interpretation than treating raw node numbers as electromagnetic fields.

### Next extension

Upgrade the U(1) adapter into a dynamical lattice phase field with a specified action. Only after that should it be compared with Maxwell electromagnetism.

## 7. Regge calculus / causal dynamical triangulations

These frameworks discretize geometry using simplicial building blocks and, in Regge calculus, encode curvature using deficit angles.

The Matrix presently has no simplicial complex and no intrinsic edge-length assignment. Therefore its discreteness alone is insufficient for a meaningful Regge/CDT mapping.

This bridge is deferred.

## 8. Integration hierarchy

The engine should integrate external theory structures in this order.

### Stage A: implemented now

1. Fourier compact modes on `Z_12` and `Z_36`.
2. Exact routing winding (+7/-7).
3. U(1) link variables.
4. Gauge transformation of links.
5. Gauge-invariant Wilson-loop holonomy.
6. Time-unwrapped causal histories.
7. Multi-scale network adjacency.
8. Explicit compatibility registry listing missing requirements.

### Stage B: next mathematically defensible extensions

1. Couple Nested Polarity Dynamics phase variables to U(1) link phases.
2. Define a local gauge-invariant phase-difference variable.
3. Replace phenomenological phase coupling where possible with link-holonomy terms.
4. Construct an explicit discrete action.
5. Derive its equations of motion.
6. Test conservation and gauge invariance exhaustively.
7. Determine its linear/small-amplitude limit.
8. Compare that limit with discrete Maxwell equations.

### Stage C: optional quantum adapters

1. Hilbert-space representation for finite Matrix states.
2. Unitary transition operator.
3. Spin-network labeling experiment.
4. Tensor-network coarse graining across nested scales.
5. Entanglement entropy calculations.

These steps would make LQG and holographic comparisons mathematically substantive.

### Stage D: M/string theory only after prerequisites

Do not add branes or "11D M-theory" by name until the engine supports the mathematical structures those names require.

A legitimate future sequence would be:

1. define a higher-dimensional compact product space;
2. construct Fourier/Kaluza-Klein mode towers;
3. define extended one- and two-dimensional state objects;
4. formulate an action;
5. establish required symmetries;
6. only then test whether the resulting theory resembles a string/M-theory sector.

## 9. Research conclusion

The comparative audit does not show that existing quantum-gravity theories prove the Universal Matrix.

It does show that several independently developed mathematical tools can be used productively:

\\[
oxed{	ext{cyclic modes + winding}}
\\]

from compact-space mathematics,

\\[
oxed{	ext{link variables + holonomy}}
\\]

from lattice gauge theory,

\\[
oxed{	ext{time-unwrapped partial order}}
\\]

from causal-set thinking, and

\\[
oxed{	ext{scale-network structure}}
\\]

from tensor-network approaches.

The lattice-gauge bridge is the strongest immediate path because it interfaces directly with the existing phase/polarity dynamics and provides gauge-invariant quantities that can be tested without importing gravity.
