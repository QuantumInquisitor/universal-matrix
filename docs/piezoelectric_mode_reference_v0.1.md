# Single-mode piezoelectric reference v0.1

`src/piezoelectric_mode_reference.py` supplies an optional linear electromechanical control with analytic limits and explicit energy accounting. Its demonstration is a **synthetic numerical example, not a material fit**. The model has one mechanical coordinate and one electrode charge; it does not derive a physical ring from toroidal geometry.

## Parameters and polarity

`PiezoelectricMode` requires finite effective modal parameters and a nonempty `parameter_source` identifying their origin:

| Symbol | Constructor field | SI unit | Constraint |
| --- | --- | --- | --- |
| m | `mass_kg` | kg | positive |
| k | `stiffness_n_per_m` | N/m | positive; short-circuit stiffness |
| c | `damping_n_s_per_m` | N s/m | nonnegative |
| C | `capacitance_f` | F | positive |
| theta | `coupling_c_per_m` | C/m, equivalently N/V | signed |

`ModeState` stores displacement x in metres, velocity v in m/s, and electrode charge q in coulombs. Applied force F is in newtons; current I in amperes enters the positive electrode. The passive shunt conductance G is in siemens. Time and frequency are supplied in seconds and Hz.

The adopted reciprocal coupling convention is

$$
m\ddot{x}+c\dot{x}+kx-\theta V=F,
\qquad q=CV+\theta x,
\qquad \dot q=I-GV.
$$

Thus `voltage_v(state)` returns $(q-\theta x)/C$. Reversing electrode polarity reverses q, V, I and theta consistently. The coupling coefficient is an effective modal quantity, not a bulk piezoelectric tensor entry. A physical parameter set needs a specified mode normalization, geometry, electrodes, supports and material reduction or independent measurements. Spatial material models additionally require elasticity/compliance, coupling, permittivity, density and orientation data; see [COMSOL's material documentation](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.013.html).

## Stored energy and time steps

`energy_j(state)` evaluates

$$
H=\frac12mv^2+\frac12kx^2+\frac{(q-\theta x)^2}{2C}.
$$

Direct differentiation using the stated equations gives

$$
\dot H=Fv+VI-cv^2-GV^2.
$$

With zero external inputs, nonnegative c and G therefore dissipate energy; with both losses zero the energy is conserved.

`step_current_driven` uses implicit midpoint integration with constant inputs over each positive time step. Bars denote arithmetic endpoint averages. Since H is quadratic, the step obeys, in exact arithmetic,

$$
H_{n+1}-H_n
=\underbrace{\Delta t(F\bar v+I\bar V)}_{W}
-\underbrace{\Delta t(c\bar v^2+G\bar V^2)}_{D}.
$$

`StepResult` reports the new state, both energies, external work W, dissipated energy D, and `balance_error_j = H_after - H_before - W + D`. Floating-point calculations can leave a residual. Energy balance alone does not establish trajectory or phase accuracy; those require time-step refinement. The internal solve uses energy-scaled coordinates to reduce sensitivity to mixed SI scales.

## Electrical boundaries and harmonic response

- **Short circuit:** V=0, hence q=theta x. `step_short_circuit` requires an initial state satisfying that constraint and maintains it. It rejects an inconsistent charged state because closing an ideal short would require separate switching and energy accounting.
- **Open circuit:** I=0 and G=0 imply constant q, including nonzero q. Its stiffness is $k_o=k+\theta^2/C$. Constant charge $q_0$ contributes the bias force $\theta q_0/C$; it does not change that incremental stiffness. The open-circuit harmonic API describes zero incremental charge about an equilibrium, not a requirement that every transient start with q=0.

`natural_frequency_hz(boundary)` returns the undamped values

$$
f_s=\frac{1}{2\pi}\sqrt{k/m},\qquad
f_o=\frac{1}{2\pi}\sqrt{(k+\theta^2/C)/m}.
$$

Short/open eigenfrequency comparisons are also used by [Daraki et al. (2024)](https://www.mdpi.com/1996-1073/17/10/2420). The need for modal capacitance and residual-mode corrections in larger systems is treated by [Toftekær and Høgsberg (2020)](https://orbit.dtu.dk/en/publications/multi-mode-piezoelectric-shunt-damping-with-residual-mode-correct/). The scalar identities here follow directly from this module's declared equations.

Phasors use $\exp(i\omega t)$, with $\omega=2\pi f$. For the selected short/open boundary, `harmonic_response` and `harmonic_sweep` use

$$
\hat x=\frac{\hat F}{k_b-m\omega^2+i c\omega}.
$$

Short circuit gives $\hat V=0$ and $\hat q=\theta\hat x$; open circuit gives $\hat q=0$ and $\hat V=-\theta\hat x/C$. For an imposed voltage, `voltage_driven_response` uses $k_b=k$ and replaces the numerator by $\hat F+\theta\hat V$. It returns the required electrode current $\hat I=i\omega\hat q$, with $\hat q=C\hat V+\theta\hat x$.

These APIs require positive frequencies and reject singular or numerically unresolved undamped poles. A damped displacement-response peak is distinct from the undamped natural frequency; for constant force amplitude its interior maximum, when present, satisfies $\omega_{peak}^2=k_b/m-c^2/(2m^2)$. A finite sweep only locates a sampled maximum.

## Report and validation scope

Run `python -m src.piezoelectric_mode_reference` from the repository root for the synthetic parameter label, short/open natural frequencies, sampled response peaks and midpoint energy-balance residual. The regression entry point is `tests/test_piezoelectric_mode_reference.py`; a report run is not experimental validation.

This reference supplies one linear mode and a passive conductance load. Spatial tensor reduction, multiple interacting modes, finite deformation, physical ring validation and measured losses remain separate work. It establishes no therapeutic effect and assigns no physical time scale or material constant to the Matrix clock or historical frequency labels.
