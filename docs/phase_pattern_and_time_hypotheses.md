# Phase patterns, circulation and time hypotheses

## Purpose and provenance

The user's pasted thoughts about Kozyrev, time, folding, spirals and environmental
energy are research prompts, not instructions or established engine laws. We
retain alternative hypotheses by stating their equations, observables and failure
conditions. Neither popularity nor a striking diagram substitutes for this test.

This first experiment is a reciprocal phase-control baseline for P05/P06/P08.
It does not implement Kozyrev's proposed mechanism or establish a time crystal.
It also does not yet attach phase forces to the breathing assembly.

## Executable baseline

`scripts/report_phase_pattern_controls.py` uses a ring with N=8,16,24 nodes,
three fixed seeds, common or one-turn phase-offset targets, uniform drift
omega=-1,0,+1, and coupling K=0,1: 108 cases. Independent runs use step 0.025
and duration 40 in dimensionless model time. Perturbations are uniform in
[-0.45,0.45] radians. They are initial disturbances, not continuous noise.

For each ring edge i,j, delta=theta_j-theta_i+alpha_i-alpha_j and
V=sum K(1-cos(delta)). The phase forces are F=-grad(V). The declared dynamics
are theta_dot=omega+F. Reciprocal edges give sum(F)=0. Consequently,
dV/dt=-sum(F_i^2), including for reversed uniform drift. RK4 integrates the
rotating-frame phases and the dissipation integral at the same stage states.
V is a dimensionless Lyapunov function, **not calibrated material energy**.
Uniform drift has zero work against this particular relative-phase potential;
this does not say that a physical rotating device requires no power.

Common order is |mean exp(i theta)|; target alignment is
|mean exp(i(theta-alpha))|. Exact one-turn target phases have common order zero
and target alignment one. Local phase organization therefore requires a
pattern-aware observable in future viewer mapping.

The two targets are exactly equivalent after subtracting alpha. They are
encoded in the links, not selected spontaneously. Sixteen nodes have no special
status here. `mirror=True` negates phases and targets: it is phase conjugation,
not a spatial reflection of the actual assembly. Reversing omega alone leaves
relaxation unchanged and is not physical time reversal. Phase velocity on an
abstract ring is not a measured propagation speed in space.

The benchmark includes coupling-off controls, phase conjugation and step
halving. The compact result is `experiments/phase-pattern-controls-summary.json`.
The full output includes initial/final phase arrays and sampled diagnostics:

```text
python scripts/report_phase_pattern_controls.py --output artifacts/phase-pattern-controls/results.json
python -m pytest tests/test_phase_pattern_controls.py -q -p no:cacheprovider
```

Ten tests check the negative gradient against finite differences, reciprocal
mean-phase preservation, target-aware order, phase conjugation, opposite-drift
equivalence, coupling-off behavior, mode equivalence, trajectory and balance
convergence, and invalid inputs. No universal stability claim is made for all
positive step sizes and coupling strengths accepted by the exploratory runner.

## Source assessment of the time ideas

- [Kozyrev's author-attributed translated paper](https://www.spirit-science.fr/ArchivesScientifiques/1967KOZYREVzj.pdf)
  proposes an active time property distinct from duration, with gyroscope and
  torsion-pendulum experiments. It also discusses inconsistent results and
  vibration sensitivity. The reported c_2=700 +/- 50 km/s is a named parameter,
  not c squared; later instantaneous-transfer hypotheses are separate. This is
  a historical proposal and reported experiment, not independent replication.
  The supplied 'time isn't money' wording has not been verified as a quotation.
- The pasted claim that solar fusion was disproved is not supported by that
  source. Direct [Borexino proton-proton neutrino measurements](https://borex.lngs.infn.it/papers/articles/solar_nu/neutrinos-from-the-primary-proton-proton-fusion-process-in-the-sun/)
  and [CNO neutrino measurements](https://www.nature.com/articles/s41586-020-2934-0)
  are quantitative constraints any alternative solar model must reproduce.
- Mechanical twist, fluid vorticity, quantum spin and spacetime torsion need
  distinct variables. [Trautman's Einstein-Cartan treatment](https://www.fuw.edu.pl/~amt/ect.pdf)
  supplies an explicit spin/torsion framework; it does not establish the pasted
  faster-than-light energy claims.
- [Tesla's 1900 article, transcribed reproduction](https://borderlandsciences.org/tesla/article/1900_06_-_Increasing_Human_Energy.html)
  discusses environmental energy and power transmission. It does not supply
  evidence for the pasted composite of sub-Planck vortices, Higgs physics and
  an unpublished gravity mechanism. Those attributions remain unresolved.
- Statements about perceived stillness or measurement can guide interpretation
  but do not currently define additional evolution equations or observables.

## Next discriminating experiments and unfinished scope

1. Add a named chiral or nonreciprocal coupling term; test zero and both signs
   with predicted sign changes. An asymmetry must enter through a declared
   mechanism rather than the clockwise label. Compare against this null model.
2. Add detuning, ongoing seeded noise and finite delays. Inject an unpredictable
   perturbation and measure arrival/recovery, distinguishing correlation from
   signaling. Current instantaneous ring coupling has no spatial speed claim.
3. Specify masses, material laws, damping, reservoirs and force-to-geometry
   mapping before assigning joules, power or entropy. Account for prescribed
   drive work and environmental exchange. Extra reservoirs must be explicit.
4. Compare timing subsystems against an ordinary oscillator/divider at matched
   cost and disturbances. Merely showing periodicity is insufficient.
5. Connect declared phase/internal state to the recurrence recorder, actual
   folding geometry and viewer. The present standalone baseline has neither
   recursive mechanical coupling nor an autonomous breathing mechanism.

No source claim is promoted to an engine constant by this report. Physical
calibration, experimental replication and the proposed alternative models
remain open.
