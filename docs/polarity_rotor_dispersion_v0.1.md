# Polarity Rotor Dispersion v0.1

## Status

This is a linear normal-mode analysis of the candidate polarity-aware rotor lattice. It is a mathematical consequence of the current Hamiltonian, not an experimental claim about nature.

## Question

Does the exact canonical polarity branch create an additional stable collective-mode band when polarity is represented by the exact phase offset

\[
\phi_x^{\mathrm{eff}} = \phi_x + \pi p_x?
\]

## Stable compensated background

For zero link phase, an energy-minimizing background satisfies

\[
\phi_x^{(0)}
=
\phi_{\mathrm{ref}}
-
\pi p_x.
\]

Therefore

\[
\phi_x^{\mathrm{eff},(0)}
=
\phi_{\mathrm{ref}}
\quad
(\mathrm{mod}\;2\pi).
\]

Write a small perturbation as

\[
\phi_x
=
\phi_x^{(0)}
+
\eta_x.
\]

The polarity offsets cancel from every link difference and the quadratic Hamiltonian becomes

\[
H^{(2)}
=
\sum_x
\frac{\Pi_x^2}{2I}
+
\frac{\kappa}{2}
\sum_{\langle xy\rangle}
(\eta_y-\eta_x)^2.
\]

Thus the exact linear dispersion on a unit-spacing cubic lattice is

\[
\boxed{
\omega^2(\mathbf{k})
=
\frac{4\kappa}{I}
\left[
\sin^2\frac{k_x}{2}
+
\sin^2\frac{k_y}{2}
+
\sin^2\frac{k_z}{2}
\right].
}
\]

For small wavevector,

\[
\omega^2
=
\frac{\kappa}{I}
|\mathbf{k}|^2
+
O(k^4).
\]

The long-wavelength characteristic speed is therefore still

\[
c_{\mathrm{lat}}
=
\sqrt{\kappa/I}.
\]

## Main result

For any static canonical polarity pattern whose independent base phase compensates the exact pi branch offset, the linear spectrum is identical to the ordinary rotor spectrum.

Canonical polarity is therefore isospectral at this level.

It does not create a second stable band merely by being written as an exact pi phase offset.

This is a constraint on future model building. A genuine additional branch of stable collective excitations requires additional independent dynamics, such as amplitude motion, a second field, dynamical scale coupling, nontrivial link structure, or another degree of freedom that is not algebraically reducible to the same phase.

## Uncompensated polarity backgrounds

Suppose instead that neighboring opposite branches are assigned equal independent base phase with zero link phase. Then those links sit at

\[
\Delta_{xy}=\pi.
\]

Their quadratic stiffness is

\[
\kappa\cos\Delta_{xy}
=
-\kappa.
\]

The configuration is stationary because \(\sin\pi=0\), but it is not an energy minimum.

For a periodic cubic checkerboard in which every nearest neighbor has opposite branch, the entire nonzero rotor spectrum changes sign:

\[
\omega^2(\mathbf{k})
=
-
\frac{4\kappa}{I}
\sum_a
\sin^2\frac{k_a}{2}.
\]

All nonzero modes are unstable.

The zone-corner mode reaches

\[
\omega^2(\pi,\pi,\pi)
=
-12\kappa/I.
\]

Compensating the base phase by \(-\pi p_x\) restores the ordinary positive spectrum.

## Physical interpretation boundary

This result does not show that canonical polarity is physically irrelevant.

It shows something narrower:

When polarity is exactly reducible to a phase offset inside the current one-field rotor Hamiltonian, a stable equilibrium absorbs that offset and the small-oscillation spectrum cannot distinguish the polarity pattern.

Therefore polarity cannot be counted again as an independent linear oscillator without adding new nonredundant structure.

## Falsifiable code checks

The implementation verifies:

* arbitrary compensated polarity patterns are isospectral,
* different random compensated polarity patterns have identical spectra,
* the numerical Hessian matches the exact finite-lattice analytic spectrum,
* a checkerboard uncompensated background has one zero mode and all other modes negative,
* compensating that checkerboard restores one Goldstone zero mode and a nonnegative rotor spectrum,
* canonical-clock mode does not apply the branch offset again.

## Next creator question

The next high-value question becomes sharper:

> What is the smallest additional nonredundant degree of freedom that can produce a second stable collective branch without duplicating canonical polarity or gauge phase?

The most conservative candidate is matter amplitude, because the repository already shows that the rotor sector is the fixed-amplitude limit of complex matter. Allowing the amplitude to move introduces a radial mode that is mathematically independent of the phase mode and can support defects, localized structures, and a possible mass gap.
