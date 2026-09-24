# Frequency sources and physical-model requirements v0.1

Status: source audit and optional historical instrument dataset. These values
are experimental inputs, not established biological resonances, a frequency
treatment protocol, or a piezoelectric material model. No hardware output is
enabled and no canonical clock or toroidal current is changed.

## What “most accurate” can mean here

The best directly readable firsthand measurement account found in this audit
is Aubrey Scoon's examination of a Beam Ray instrument. It is useful for
tracing reported settings to an author, instrument configuration and frequency
role. It is not an independently calibrated standard. The instrument's exact
date and attribution are qualified by its examiner. The source also describes
dial backlash and nonlinear tuning; a printed integer does not establish
one-hertz accuracy. See the [analysis](https://www.rife.de/scoon_1939_beam_ray_analysis.html)
and [companion examination](https://www.rife.de/scoon_1939_beam_ray_machine.html).

Other sources were compared before choosing the initial dataset:

| Source | Useful evidence | Limitation |
| --- | --- | --- |
| [Rife laboratory archive](https://rife.org/lab-clinical-reports) | Reproductions of dated laboratory and instrument documents | Private archive provenance; original scans still require authentication and careful visual transcription |
| [MOR comparison table](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/RifeMORs.htm) | Keeps several attributed eras and sources visible | Later compilation; indirect entries and wavelength-derived values must remain separate |
| [CAFL maintainer](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/CAFL.htm) | Large directly available catalog, headed v2023_05_25 when inspected | Mixed anecdotal, converted and speculative entries; size is not calibration evidence |
| [NCFL maintainer](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/Non-ConsolidatedFrequencyList.htm) | Retains source lists and conversion context | Heterogeneous frequencies, wavelengths, ranges, notes and device codes |

The [maintainer's index](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/)
warns that some redistributed catalogs round entries when converting units.
The [catalog introduction](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/IntrotoFrequenciesandAnecdotes.htm)
describes mixed sources and limited testing. No reviewed catalog establishes
a universally accurate map of disease-specific resonances. Cancer Research UK
reports [no reliable evidence that Rife machines cure cancer](https://www.cancerresearchuk.org/about-cancer/treatment/complementary-alternative-therapies/individual-therapies/rife-machine-and-cancer).

## What is included

`src/reference_data/rife_scoon_catalog.json` preserves all 15 resolved settings
in Scoon's table, the separately reported carrier observations, reported
spectral components, mains modulation, a waveform example and the later
booster bandwidth. Its 24 frequency records retain
their source locations, original units, configurations and approximation
status. Four oscillator-band ranges and the separately reported booster input
range remain ranges. Incomplete dial settings
remain unresolved; no frequency is guessed from a dial number.

Historical labels are retained as source metadata, without translating them
into modern diagnoses or assigning an effect. Unknown measurement uncertainty
is represented by null, never zero. Approximate carrier observations from
different reports/configurations remain separate records. Spectral observations
are not silently promoted to exact integer harmonics.

The `approximate` flag records whether the source explicitly qualified a
value; false does not mean an exact or calibrated measurement. The waveform
example retains the report's uncalibrated-scope context. The later booster
bandwidth is a separate role, not a drive setting or a resonance.

This is complete for the selected resolved table and the explicit carrier,
spectral, mains, waveform-example and bandwidth observations in its two source
reports. It is not a claim
to include every frequency from all historical or modern catalogs. Earlier
scanned settings and unsourced modern lists are not silently substituted.

## How the data can be used

`src/frequency_source_catalog.py` loads and validates the source records.
Frequency selection requires an explicit role. Its exact decimal unit
conversion distinguishes mHz from MHz, retains duplicate source memberships,
and rejects missing or invalid units. Carrier values and modulation values
are never merged by default.

The optional cycles-per-model-tick conversion requires an explicit
seconds-per-tick value. It performs only dimensional conversion:

$$
\text{cycles per tick}=f_{\mathrm{Hz}}\,\Delta t_{\mathrm{seconds/tick}}.
$$

It does not infer that clock scale or a resonance. Any later drive must also
state amplitude, phase, waveform and duration. A modulated waveform requires
its carrier and modulation law; a scalar list of numbers does not specify
that waveform. Run `python -m src.frequency_source_catalog` for the audit.

## Established inputs still needed for a physical ring model

1. **A measured time and length scale.** The existing toroidal geometry and
   content current are dimensionless. Supplying Hz does not identify a
   Matrix tick with a second or content with electric charge.
2. **Material and orientation.** Piezoelectricity needs elasticity, dielectric
   properties, a coupling tensor and mass density. Crystal/poling directions
   must be mapped into the ring's local frames. These are material inputs,
   not consequences of ring shape. See [material inputs](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.013.html)
   and [coupled equations](https://doc.comsol.com/6.4/doc/com.comsol.help.sme/sme_ug_theory.06.043.html).
3. **Mechanical and electrical boundaries.** Supports, electrodes, loads and
   surrounding media affect the solution. The drive and measured output
   must be defined. The [piezoacoustic transducer example](https://doc.comsol.com/6.3/doc/com.comsol.help.models.sme.piezoacoustic_transducer/models.sme.piezoacoustic_transducer.pdf)
   illustrates solving the coupled fields and sweeping the excitation.
4. **Losses and bandwidth.** Mechanical, dielectric and coupling losses are
   distinct inputs. Passive material dissipation must be nonnegative.
   See [piezoelectric losses](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_modeling.05.109.html).
5. **Derived and measured resonances.** Compute modes from geometry, mass and
   stiffness, then compare frequency response and damping with measurements.
   A named frequency is not automatically a mode. See [frequency-response
   equations](https://www.comsol.com/blogs/how-to-model-different-types-of-damping-in-comsol-multiphysics).
6. **Numerical controls.** Test zero drive/coupling, signed response, coordinate
   rotation, energy accounting, and mesh/time-step convergence. Resolve the
   highest represented waveform frequencies and compare against analytic
   or measured reference cases. These are proposed validation gates for
   this repository, not completed physical experiments.

A minimal next physical experiment would use a specified linear material and
small deformations, with an explicit drive and measured response. Large
inside-out motion and general toroidal fan-out remain separate geometry and
dynamics questions. The frequency catalog alone closes none of those gates.
