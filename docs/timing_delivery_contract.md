# Conditional timing acquisition and delivery contract

This additive experiment schedules existing timing signals through explicitly
declared acquisition and receiver services. It does not rerun or replace the
168-case Floquet study. The new contribution is deadline, contention and drop
accounting; endpoint resource counts were already documented in the original
timing study.

The fixture preserves the exact finite-shot arrays and parameters of all 16
base interacting cases at `g=.97`, `N=6/8`, seeds `0..7`. It records the original
full artifact raw SHA256 and source hashes. The reporter pins the extracted
fixture's normalized UTF-8/LF hash and exact case IDs. No new measurement
samples or spin evolutions are generated.

## Conditional source acquisition

All durations are synthetic drive-period units, not measured seconds. Endpoint
`n` is requested at time `n`. Each of its 256 independent fresh preparations
occupies one of 256 lanes for `.25 + n + .25` periods: preparation, endpoint
evolution and endpoint readout. Jobs are FIFO by endpoint then shot number;
the earliest-free lane is selected, breaking ties by lane number. An estimate
is available only after its last shot finishes. No speculative preparation,
continuous sensing or readout backaction is modeled.

The divider is assumed available at cycle `n`. **Only downstream service,
load and deadlines are matched.** Its acquisition cost is not measured or
matched to the cold-start endpoint backend. Thus failure of this backend is
a conditional scheduling result, not a general no-go result for spin clocks
or proof of a physical divider advantage.

The `ideal_replay` positive control makes both saved candidate samples and the
divider available at `n`, with zero receiver service and a zero-latency
deadline. It schedules no acquisition jobs; the cold-start operation counts
are counterfactual for this prerecorded-playback control.

## Shared receiver contract

One FIFO server receives source samples and explicit competing jobs. Capacity
counts all unfinished jobs, including the one in service. Completions precede
arrivals at equal timestamps; competing arrivals precede source arrivals at
equal times, then supplied order. Zero-duration jobs complete immediately only
when no earlier job is pending; immediately completed jobs do not count as
unfinished. No jobs are preempted. A full queue drops arrivals.

Deadlines are inclusive and measured from original source cycle `n`. Accepted
late jobs still consume service and retain their completion records, but their
samples are unavailable to the on-time receiver. The returned `delivered_ticks`
are **on-time accepted edges**, not all eventual events. The original threshold
`.2` and receiver rules remain unchanged. Dropped/late sample positions become
unresolved in the original indexed sequence; they are never compacted away or
repaired from expected parity. Canonical routing advances only from accepted
on-time edges.

## Four declared configurations

| Configuration | Source acquisition | Receiver service | Deadline | Capacity | Competing jobs |
| --- | --- | ---: | ---: | --- | --- |
| Ideal replay | Instantaneous prerecorded samples | 0 | 0 | Unlimited | None |
| Cold start, unloaded | Fresh endpoints | .1 | 1 | Unlimited | None |
| Cold start, contention | Fresh endpoints | .1 | 1 | Unlimited | .9 service at every integer 0..256 |
| Cold start, finite queue | Fresh endpoints | .1 | .25 | 1 unfinished job | 1.5 service every fourth cycle 0..256 |

Each configuration runs all 16 existing traces alongside the ideal divider.
This is not a new reliability sample or an optimization of queue policies.
The original 128-edge target remains unchanged; missing, late and extra edges
are distinguished from intrinsic signal correctness.

All 16 traces retain 128 on-time ticks in ideal replay, as does the divider.
The declared cold-start acquisition backend delivers no on-time edges under
the chosen deadlines; the ideal-availability divider retains 128 in unloaded
and contention cases. The finite-queue stress case delivers zero on-time edges
for either source. These outcomes follow the stated conditional service
contracts and do not establish a matched-hardware advantage.

Resource outputs retain preparations, accumulated Floquet periods and gate
counts for the cold-start acquisition only. `energy_joules` is explicitly null.
Simulation runtime and operation counts are not energies. Physical loading,
measurement backaction, electrical costs and absolute timing remain open.

## Reproduction

Run `python scripts/report_timing_delivery.py --output
artifacts/timing-delivery-summary.json`. It reads the committed small fixture,
so a fresh checkout needs neither the large historical artifact nor a rerun.
The committed summary contains compact per-case metrics and provenance.

Tests check hand-derived one/two-lane acquisition schedules, known resource
totals, analytic FIFO waiting, deadline boundaries, tied arrivals/completions,
sample-loss adjacency, late-job service and invalid inputs. Original timing
receiver tests remain part of focused validation.
