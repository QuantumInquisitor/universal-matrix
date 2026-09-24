# Frequency and spectrum evidence catalog, version 0.1

This optional reference layer keeps numerical provenance and physical meaning
separate. Sharing a number or a geometric pattern does not establish a shared
resonance, interaction, or therapeutic effect. No frequency here sets the
canonical Matrix clock, a material constant, or a hardware output.

## Holdings and evidence classes

| Collection | Actual coverage in this repository | Evidence and interpretation |
| --- | --- | --- |
| Existing Scoon/Rife instrument reports | 24 source records, five ranges, 12 unresolved settings | Historical instrument observations; modulation, carrier and reported spectral components remain distinct in `frequency_source_catalog.py`. |
| CAFL v2023_05_25 | 1,557 source entries: 1,403 with explicit numeric fields and 154 without; 11,668 frequency occurrences | Unverified anecdotal compilation. These are listed claims, not discovered or established biological resonances. Author/source labels are preserved for traceability. |
| NIST hydrogen strong lines | All 30 rows of this particular table, including 14 persistent lines; 8 vacuum and 22 air wavelengths | Evaluated atomic reference data. Ritz fine-structure components and unresolved multiplets are explicitly distinguished. This is not the complete spectrum of hydrogen or of all matter. |
| Walter Russell, *The Universal One* (1926) | Comprehensive relevant-concept audit and five selected numerical leads | Historical author proposals. Two hypothetical rates are explicitly qualified; three wavelengths have unverified units and medium. No measured element-Hz table is established. |

Source data are in `src/reference_data/cafl_explicit_catalog.json`,
`nist_hydrogen_lines.json`, and `universal_one_numeric_leads.json`. The existing
`rife_scoon_catalog.json` retains its original scope and source roles. Separate
loaders prevent accidental relabeling of the new collections as one evidence
class. Unknown uncertainty is represented by null, never zero.

## CAFL extraction and limitations

The source is the maintainer's publicly readable
[Consolidated Annotated Frequency List](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/CAFL.htm),
retrieved 2026-09-24. Its visible header specifies v2023_05_25 and Hz. The
[source introduction](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/IntrotoFrequenciesandAnecdotes.htm)
provides the maintainer's context. Attribution to this compilation does not
mean every value was measured by Royal Rife or appears in an original Rife record.

The full retrieved entry block, positions 41 through 2846 in the text reader,
was inspected by an independent extraction and reproduced by the committed
parser. Those positions are retrieval-text locations, not HTML line numbers.
The first label is `Abdominal_inflammation`; the last is `Zygomycosis`.
Repeated values and source ordering are preserved. The 11,668 occurrences
are not 11,668 distinct discoveries.

Only the numeric field following the entry separator outside parentheses is
imported. Balanced multiline annotations are joined before exclusion. Numbers
inside annotations, treatment schedules, anecdotes and reference instructions
are excluded. Missing explicit values remain missing; aliases are not resolved
by copying another entry's numbers. A future extractor must not turn numbers
in prose into calibrated frequencies. Unsupported explicit syntax fails closed.

Four annotations span multiple retrieved lines, including `Cancer` and
`Herpes_simplex_RTI`; splitting those lines into independent records would
misattribute prose and numeric values. The parser also rejects numbers split
by an annotation, so `12(annotation)34` cannot become the invented value 1234.
Tests cover these failure modes and selected source values.

The original retrieved-line JSON, retained as a local research intermediate,
has SHA-256 `5e11796d8c4f56874d59df8f948d2582488e5167a0fe087db1e2bfdbed1f6b4a`.
The committed dataset contains the factual labels and explicit numeric fields,
with indicators that annotations were omitted. Reproduction against a future
webpage needs the same version and entry bounds; the live page may change.

## Physical wavelength conventions

The complete [NIST strong-line table](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable2.htm)
and its [hydrogen notes](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable1.htm)
identify neutral hydrogen-1. Decimal strings preserve printed precision. The
1215, 4861 and 6562 angstrom components are Ritz wavelengths; the other rows
are unresolved multiplets derived from weighted-average energies. These are
evaluated references, not a fresh measurement campaign.

Per-row references remain attached, with their meanings from the
[NIST reference table](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable7.htm).
Relative intensities are source-dependent values and must not be interpreted
as calibrated transition probabilities or material coupling strengths.

This Handbook labels its infrared entries as air wavelengths too. Its convention
must not be replaced by an assumed cutoff borrowed from another database.
The conversion function uses `frequency = c / (n * wavelength)` with angstroms
converted to meters. Vacuum fixes n=1. Air requires an explicit, wavelength-specific
phase refractive index supplied by the caller; the routine does not invent its
temperature, pressure, humidity, composition, or dispersion model. An unknown
medium is rejected. See the [Handbook conventions](https://www.nist.gov/pml/handbook-basic-atomic-spectroscopic-data/basic-atomic-spectroscopic-data-handbook).

## Book, M4 and tests

The [Russell audit](universal_one_source_audit_v0.1.md) maps the applicable
concepts across octave classification, polarity, scaling, conservation,
geometry, waves, time, color/spectra, rotation, crystallization, valence,
ionization and tone. Original edition and later transcription pagination
are distinguished. Unverified diagrams remain a documented source gap.

The [M4 audit](m4_source_and_claim_audit_v0.1.md) separates visible image labels,
verified source identities and missing physical definitions. Its named
cosmological model is not attributed by processor papers that also use M4.

The [physical theory controls](physical_theory_controls_v0.1.md) compare two
declared hydrogen approximations against the eight vacuum references and
test a periodic force-free ABC field with independent differences and negative
controls. These are bounded scientific and mathematical references, not a
demonstration that M4 or Russell explains the data.

The [microplane projection reference](microplane_projection_reference_v0.1.md)
checks tensor projections and virtual work motivated by the separately
sourced engineering model. It does not import concrete damage laws or infer
piezoelectric coupling from a spherical diagram.

## Broader coverage still to add

There is no finite list of every possible frequency: continuous radiation,
condition-dependent resonances and different physical quantities coexist.
Separate, sourced catalogs can expand the useful coverage:

- [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
  for additional elements, ions, transitions, evaluated uncertainties and
  observed/Ritz distinctions. This batch imports one Handbook table only.
- [HITRAN](https://www.hitran.org/) for molecular absorption line parameters;
  isotopologues, line strengths, temperature and pressure broadening conventions
  must travel with those data. No HITRAN rows are imported in this batch.
- The [non-consolidated frequency list](https://www.electroherbalism.com/Bioelectronics/FrequenciesandAnecdotes/Non-ConsolidatedFrequencyList.htm)
  is a separate historical/anecdotal source and has not been imported here.
- Material resonance measurements require sample geometry, composition, boundary
  conditions, drive amplitude, temperature and uncertainty. A generic catalog
  cannot supply the missing modal parameters of a piezoelectric ring.

Run `python -m src.spectral_reference_catalog` for a coverage report. All
source expansion remains optional and leaves the canonical kernel unchanged.
