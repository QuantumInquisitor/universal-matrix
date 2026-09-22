# Q-Ball Peak Period Classification v0.1

## Result from the t=2.5 trace

The perturbed peak events contain a very small reversal between `t=1.600` and
`t=1.650`. Its swing is `5.0471e-6`, about `0.25%` of the largest adjacent
swing. The classifier therefore records that pair as modulation rather than a
dominant breathing extremum.

After that removal, the retained same-kind intervals are:

- minimum to minimum: `1.375`;
- maximum to maximum: `0.675`.

Their relative spread is about `0.683`. They do not support one consistent
period at the present observation length. Averaging them would produce `1.025`,
but that number is not reported as a physical period because the inputs are
inconsistent.

The trace therefore supports three narrower statements:

1. the closely spaced `t=1.600–1.650` reversal is small modulation;
2. the perturbed state remains bounded through `t=2.5`;
3. a longer trace is required before assigning a dominant breathing period.

Only one perturbed radius maximum is present, at `t=1.975`, so a repeated
peak-radius phase relation is also not yet identified.

## Method

`src/qball_peak_period_classification.py` removes an adjacent opposite-kind
pair only when its swing is below one percent of the largest observed adjacent
swing. It then compares all retained minimum-to-minimum and
maximum-to-maximum intervals. A consistent period requires at least two
candidate intervals whose relative spread is no more than fifteen percent.

The thresholds are explicit parameters and are tested independently. This is
a diagnostic classification rule, not an assumed physical law.
