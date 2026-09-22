# Local Matrix Transition Kernel v0.1

## Purpose

This module answers the next creator-style design question:

> What is the smallest local transition rule that can support conservative exchange, polarity-sensitive direction, gauge transport, and reversible dynamics?

Implementation:

- src/local_transition_kernel.py

Tests:

- tests/test_local_transition_kernel.py

## 1. Design constraints

The local rule is required to satisfy:

1. **Locality**  
   Only the two endpoint cells of one oriented edge participate.

2. **Reversibility**  
   Reversing the signed evolution step inverts the local map.

3. **Conservation**  
   The pair quadratic content is invariant.

4. **Gauge covariance**  
   Interaction depends on the gauge-invariant phase difference.

5. **Orientation consistency**  
   Reversing an oriented edge reverses the signed generator.

6. **Polarity sensitivity**  
   Opposite polarity can reverse or enhance directed exchange without creating content.

These requirements do not prove a unique law. They define a minimal constrained ansatz.

## 2. Gauge-covariant phase difference

For endpoint phases

\[
\phi_i,\qquad \phi_j
\]

and oriented U(1) link phase

\[
\theta_{ij},
\]

define

\[
\boxed{
\Delta_{ij}
=
\phi_j-\phi_i+\theta_{ij}.
}
\]

Under

\[
\phi_i\to\phi_i+\alpha_i,
\]

\[
\phi_j\to\phi_j+\alpha_j,
\]

\[
\theta_{ij}
\to
\theta_{ij}
+\alpha_i-\alpha_j,
\]

the quantity \(\Delta_{ij}\) is invariant.

## 3. Phase exchange channel

The first channel is

\[
\boxed{
J_{\rm phase}
=
g_\phi\sin\Delta_{ij}.
}
\]

It is odd under edge reversal because

\[
\Delta_{ji}=-\Delta_{ij}.
\]

This is the lowest harmonic gauge-invariant directed phase carrier already used in related parts of the engine.

## 4. Polarity exchange channel

Let the signed endpoint polarities be

\[
\sigma_i,\sigma_j\in\{-1,+1\}.
\]

Define

\[
\boxed{
J_{\rm pol}
=
g_p
\frac{\sigma_i-\sigma_j}{2}
\cos\Delta_{ij}.
}
\]

Properties:

- like polarity gives zero explicit polarity-gradient channel;
- opposite polarity gives a signed channel;
- exchanging source and target reverses the sign;
- phase-aligned opposite polarities maximize this channel;
- a global polarity reversal reverses this channel.

This is an experimental polarity-coupling ansatz.

It should not be described as established electromagnetism.

## 5. Alternating scale orientation

The ontology layer supplies an exact canonical branch sign.

The nested-scale hypothesis then adds

\[
\epsilon_\ell=(-1)^\ell.
\]

The effective oriented polarity is

\[
\boxed{
\sigma_{\rm eff}
=
\sigma_{\rm branch}
(-1)^\ell.
}
\]

Thus neighboring scale levels can carry opposite effective orientation even when their canonical branch bits agree.

This implements the micro-to-macro alternating-polarity idea explicitly.

The alternation rule remains a physical hypothesis.

## 6. Combined local generator

The current minimal two-channel generator is

\[
\boxed{
G_{ij}
=
g_\phi\sin\Delta_{ij}
+
g_p
\frac{\sigma_i-\sigma_j}{2}
\cos\Delta_{ij}.
}
\]

The couplings

\[
g_\phi,\qquad g_p
\]

remain dimensionless model inputs.

They are not derived from the canonical kernel in v0.1.

## 7. Conservative exchange map

For endpoint content amplitudes

\[
a_i,\qquad a_j,
\]

define the local angle

\[
\delta_{ij}
=
G_{ij}\,\Delta t.
\]

The update is

\[
\boxed{
\begin{pmatrix}
a_i'\\
a_j'
\end{pmatrix}
=
\begin{pmatrix}
\cos\delta_{ij} & -\sin\delta_{ij}\\
\sin\delta_{ij} & \cos\delta_{ij}
\end{pmatrix}
\begin{pmatrix}
a_i\\
a_j
\end{pmatrix}.
}
\]

Therefore

\[
\boxed{
(a_i')^2+(a_j')^2
=
a_i^2+a_j^2.
}
\]

Conservation is built into the local map.

## 8. Reversibility

Because the update is a rotation,

\[
R(\delta)^{-1}=R(-\delta).
\]

Therefore a signed reverse step exactly inverts the local map up to floating arithmetic.

This is an important design principle.

Irreversible macroscopic behavior should not be inserted into the microscopic edge rule unless required by evidence. It should preferably emerge from coarse graining, open boundaries, or statistical behavior.

## 9. Edge reversal

Reversing the physical edge gives

\[
(i,j,\theta_{ij})
\longrightarrow
(j,i,-\theta_{ij}).
\]

Then

\[
\Delta_{ji}=-\Delta_{ij}
\]

and

\[
\frac{\sigma_j-\sigma_i}{2}
=
-
\frac{\sigma_i-\sigma_j}{2}.
\]

Therefore

\[
\boxed{
G_{ji}=-G_{ij}.
}
\]

The interaction has no preferred edge orientation.

## 10. What this answers

This is the first common local law in the project that explicitly combines:

- phase transport;
- gauge connection;
- polarity difference;
- alternating nested-scale orientation;
- conservative transfer;
- exact local reversibility.

It unifies mathematical motifs that previously existed in separate modules.

## 11. What it does not answer

The kernel does not yet determine:

- why \(g_\phi\) has one particular value;
- why \(g_p\) has one particular value;
- whether the polarity channel corresponds to electromagnetism, another interaction, or only an internal transfer law;
- the physical time represented by one update step;
- the physical length of one neighboring-cell edge;
- how a many-edge update should be ordered in the continuum limit;
- whether this law yields Lorentz symmetry;
- whether stable particle-like excitations result.

## 12. Creator-style interpretation

If designing a universe from minimal rules, this is preferable to assigning separate forces at the start.

A cell does not need to know "gravity", "electromagnetism", or a particle name.

It needs:

- its state;
- its neighbors;
- an oriented connection to each neighbor;
- a reversible rule for exchanging conserved content.

Different effective forces would then need to emerge from collective states, representations, and long-distance limits.

That is the standard this transition kernel is designed to test.

## 13. Next question

The next question is no longer simply "what force law do we add?"

It is:

> When this local edge rule is applied across the entire repeated Matrix complex, what collective modes are stable, what dispersion relation emerges, and which symmetries appear at long wavelength?

That is the next dynamics-to-particle and dynamics-to-spacetime bridge.
