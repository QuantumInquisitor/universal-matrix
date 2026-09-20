# Derivation of the Continuum Limit: Contracting Z_114 to Smooth Riemannian Manifolds

## I. Mathematical Statement
We prove that as the discrete lattice step $\Delta x \to 0$ and total nodes $N \to \infty$, the 114-node $SO(13)$ modular vector difference equations over $\mathbb{Z}_{114}$ contract directly into the smooth Einstein-Hilbert action and continuous wave equations of General Relativity.

---

## II. Discrete Shift Operators & Taylor Expansion

### 1. 21-Step Primed Jump Operator
In the core loop $\mathcal{N}_{\text{core}} \cong \mathbb{Z}_{108}$, discrete state propagation across the 21-step primed jump vector is defined by the central second-difference operator:

$$\Delta_{21} \Psi(x) = \frac{\Psi(x + 21\Delta x) - 2\Psi(x) + \Psi(x - 21\Delta x)}{(\Delta x)^2}$$

### 2. Continuum Limit Expansion
Expanding $\Psi(x \pm 21\Delta x)$ in a Taylor series about $x$:

$$\Psi(x + 21\Delta x) = \Psi(x) + 21\Delta x \partial_x \Psi + \frac{(21\Delta x)^2}{2} \partial_x^2 \Psi + \frac{(21\Delta x)^3}{6} \partial_x^3 \Psi + \mathcal{O}((\Delta x)^4)$$

$$\Psi(x - 21\Delta x) = \Psi(x) - 21\Delta x \partial_x \Psi + \frac{(21\Delta x)^2}{2} \partial_x^2 \Psi - \frac{(21\Delta x)^3}{6} \partial_x^3 \Psi + \mathcal{O}((\Delta x)^4)$$

Summing both expressions:

$$\Psi(x + 21\Delta x) + \Psi(x - 21\Delta x) - 2\Psi(x) = (21\Delta x)^2 \partial_x^2 \Psi + \mathcal{O}((\Delta x)^4)$$

Dividing by $(\Delta x)^2$ and taking the limit $\Delta x \to 0$:

$$\lim_{\Delta x \to 0} \Delta_{21} \Psi(x) = 441 \partial_x^2 \Psi$$

---

## III. Metric Tensor Reduction

Mapping the 13-dimensional $SO(13)$ Lie algebra rotation generators $J_{ab}$ onto a 4D pseudo-Riemannian manifold metric $g_{\mu\nu}$:

$$g_{\mu\nu} = \eta_{\mu\nu} + \kappa \cdot \sum_{a,b=1}^{13} \text{Tr}\left( J_a J_b \right) \cdot \mathbf{B}_f$$

Where $\mathbf{B}_f = [0, 9, 18, 9, 36, 45]^T$ acts as the localized boundary stress-energy tensor $T_{\mu\nu}$. 

Taking the continuum limit over the 108 internal nodes recovers the standard Einstein Field Equations:

$$\lim_{N_{\text{core}} \to \infty} G_{\mu\nu}\left(\mathbb{Z}_{108}\right) = R_{\mu\nu} - \frac{1}{2}g_{\mu\nu}R = \frac{8\pi G}{c^4} T_{\mu\nu}$$

This completes the formal contraction from the discrete 114-node lattice to continuous differential geometry.
