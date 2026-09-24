# Proposed storage and acoustic controls v0.1

These two optional references turn pressure-transfer and pipe analogies into explicit modern models. Their SI parameters are supplied by the caller; the demonstrations use synthetic values. They do not reconstruct a Russell apparatus, infer a historical spectrum, calibrate a material, or change the canonical integer/geometry modules.

## Passive pressure storage

`src/proposed_pressure_storage.py` provides `PressureStorageNetwork(C, G, B)` with:

| Input | Meaning | Unit/condition |
|---|---|---|
| `compliance_m3_per_pa` | Incremental volume stored per pressure increment | m³/Pa; finite and strictly positive |
| `conductance_m3_per_pa_s` | Oriented link flow per pressure difference | m³/(Pa s); finite and nonnegative |
| `incidence` | +1 at a link's tail, −1 at its head | Dimensionless; exactly two signed entries per column |
| Pressure vector | Signed pressure increment from a fixed common reference state | Pa; one finite value per node |
| Time | Elapsed time in a closed, unforced network | s; finite and nonnegative |

Fluid capacitance and pressure/volume-flow variables are standard lumped system elements; the [MIT one-port notes](https://web.mit.edu/2.151/www/Handouts/OnePorts.pdf), pp.4–7, give their reference-pressure and storage relationships. The tank-transfer motivation comes from the institutional transcription of [The Russell Genero-Radiative Concept](https://www.philosophy.org/archives/the-russ). The graph, constitutive assumptions, solver and tests here are our declaration.

With diagonal `C` and `G`, define `L=B G Bᵀ`. The implemented equations are

\[
Q=GB^Tp,\qquad C\dot p=-L p,\qquad
E=\tfrac12p^TCp,\qquad
\dot E=-\sum_eG_e(B^Tp)_e^2.
\]

Pressure times volume is energy in joules, and pressure times volume flow is power in watts. Total incremental stored volume `Σ C_i p_i` is conserved separately in every component joined by **positive** conductance. A zero-conductance bridge does not join two equilibria. For each component `A`,

\[
\bar p_A=\frac{\sum_{i\in A}C_i p_i(0)}{\sum_{i\in A}C_i},\qquad
E(0)-E_\infty=\tfrac12\sum_A\sum_{i\in A}C_i[p_i(0)-\bar p_A]^2.
\]

Each component's known constant-pressure nullspace is removed explicitly in energy coordinates `sqrt(C)p`. The remaining symmetric eigensystem supplies positive exponential decay rates. The solver never declares an arbitrary first computed eigenvalue zero. Unresolved positive decay spectra raise an error rather than being relabeled as isolated or stationary modes.

`pressure_at` evaluates that finite-dimensional solution; `flow_m3_per_s`, `pressure_rate_pa_per_s` and `energy_j` expose the physical quantities. `audit` compares endpoint energies with an independently evaluated modal loss integral, using `expm1` for small elapsed times, and reports per-component volume residuals and an instantaneous power-balance residual. The result is an unforced equalization process, without sustained oscillation. Uniform residual compression cannot drive equal-pressure links; using it requires an external reference reservoir and a different boundary model.

The implementation allows 1–128 nodes and at most 4096 edges, including an `(n,0)` incidence array. Parameters are copied into immutable array storage. Inputs with invalid shapes, boolean-only/non-real arrays, nonfinite values, nonpositive compliance, negative conductance or malformed incidence are rejected. Derived overflows and unresolved scales also reject. This bounded float64 solver is not an arbitrary-condition-number guarantee.

The synthetic three-node example uses `C=(2,3,5)×10⁻¹⁰`, `G=(0.5,0.8,0.3)×10⁻¹²`, and pressures `(100000,20000,0)` Pa. It reaches an equilibrium of **26000 Pa**. Initial stored energy is **1.060 J**; equilibrium energy is **0.338 J**; equalization can dissipate **0.722 J**. At 1000 s the modal loss is approximately **0.721831571224 J**, with an energy-balance residual about `1.1×10⁻¹⁶ J` in the recorded demonstration. These are computed synthetic quantities, not measurement precision.

Omitted effects include nonlinear gas thermodynamics, heat transfer, fluid inertance, external sources, load extraction and material limits. A toroidal geometry connection would require an explicit assignment of compliance and conductance from geometry and material data.

## Ideal cylindrical-pipe acoustics

`src/proposed_pipe_acoustics.py` provides `PipeAcoustics(length_m, sound_speed_m_s, left_end, right_end)`. Each endpoint is explicitly `open` or `closed`; default is open/open. For small one-dimensional pressure perturbations in a uniform ideal cylinder,

\[
p_{tt}=c^2p_{xx},\qquad -u_{xx}=k^2u,\qquad f=ck/(2\pi).
\]

An ideal open end has `u=0`. An ideally closed end has `u_x=0`. These pressure boundaries and the distinction between cylindrical and conical bores are explained by the [UNSW acoustics group](https://www.phys.unsw.edu.au/jw/pipes.html). The present implementation is cylindrical only.

| Ends | Analytic frequencies | Mode ordering |
|---|---|---|
| Open/open | `n c/(2L)` | `n=1,2,...` |
| One closed, one open | `(2n+1)c/(4L)` | `n=0,1,...` |
| Closed/closed | `n c/(2L)` | `n=0,1,...`; first entry is the static uniform-pressure mode |

`analytic_frequencies_hz(count)` returns the ideal continuum result. `finite_element_modes(intervals, count)` independently solves the linear consistent-mass finite-element problem on `x/L∈[0,1]`. It returns frequencies, physical node positions, nodal pressure modes and dimensionless eigenvalues `(kL)²`. Mode amplitudes have no absolute pressure calibration; they are normalized by the dimensionless integral `∫u² d(x/L)`. Open-end values are exactly constrained to zero. The closed/closed constant mode is inserted from its explicit boundary nullspace, with the remaining positive modes solved in its orthogonal complement.

Mode counts must be integers in 1–256 and cannot exceed the unconstrained mesh degrees of freedom. Dense meshes are limited to 2–256 intervals. Boolean/fractional counts, nonfinite/nonpositive SI parameters, unrecognized boundaries, overflowing frequencies and numerically collapsed physical mesh spacing reject. Resolution near the mesh cutoff is not certified merely because the eigenproblem returns a number; low-mode refinement remains necessary.

At `L=1 m` and declared `c=343 m/s`, open/open frequencies start `(171.5,343,514.5)` Hz; closed/open frequencies start `(85.75,257.25,428.75)` Hz. Capping one end of this same ideal pipe **halves** its fundamental and selects odd harmonics. This is a bounded boundary-condition control for the pipe analogy previously located in the [*A New Concept of the Universe* reproduction](https://www.giurfa.com/the_new_concept.pdf#page=86), mirror label Page 85. It does not test an unspecified historical instrument or the entire theory. A conical bore, different effective length, selected overtone or different excitation would be another declared experiment.

For 128 intervals, the computed open/open fundamental is approximately `171.504305 Hz`; closed/open is `85.750538 Hz`. The ratio is about `0.499990588`. Across three refinements the low-mode frequency error decreases quadratically. The static zero mode of a closed/closed pipe is not a sound resonance and should not be compared with the open/open fundamental.

No end corrections, radiation impedance, viscosity, thermal losses, mean flow, transverse modes, wall compliance, nonlinear excitation or measured sound-speed uncertainty are included. Cross-sectional area cancels from this uniform one-dimensional eigenproblem; this does not make pipe radius irrelevant to the omitted effects.

## Reproduction and verification

From the repository root:

```text
python -m src.proposed_pressure_storage
python -m src.proposed_pipe_acoustics
python -m pytest tests/test_proposed_pressure_storage.py tests/test_proposed_pipe_acoustics.py -q
```

The focused tests cover analytic two-reservoir decay and integrated loss; independently integrated three-node dynamics and work; component-wise conservation; isolated nodes and zero links; orientation reversal; common-pressure shifts; passive energy and pressure bounds; all endpoint choices; exact sine/cosine nodal shapes; second-order acoustic convergence; the half-fundamental control; geometry/speed scaling; invalid inputs and bounded allocations. They validate the declared mathematical models and their ordinary-scale numerical implementation, without supplying a physical fit to Russell's apparatus or the Universal Matrix geometry.

Recorded verification on 2026-09-24: **75 focused tests passed**. Both demonstration entry points also executed successfully.
