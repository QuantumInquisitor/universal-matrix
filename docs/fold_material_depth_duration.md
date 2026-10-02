# Experimental depth-three duration extension to 0.1 seconds

The depth-three passive material tree was initially restricted to 0.05 seconds. The older
depth-0 through depth-2 recursion experiment, however, used a 0.1 second interval. A weak
depth-2-to-depth-3 root response over 0.05 seconds therefore cannot by itself distinguish
strong attenuation from delayed propagation.

This checkpoint extends only the experimental depth-three audit to 0.1 seconds. It does not
change the production duration scope or any physical law.

## Unchanged model

The binary scale ratio, constitutive scaling, mapped connector formula and edge weights,
damping law, module masses, initial root perturbation and the 1e-12 root-response threshold
all remain unchanged. The original report_fold_material_depth3.py duration guard also remains
0.05 seconds.

## Controls

The extension compares depth 2 and depth 3 continuously to 0.1 seconds and samples their root
difference at 0.05, 0.075 and 0.1 seconds. It records whether the response crosses the existing
1e-12 resolution threshold rather than requiring either outcome.

A depth-three trajectory is also executed as two consecutive 0.05 second segments and compared
with the continuous 0.1 second run. This tests complete-state persistence across the extension.

Every segment retains node, edge and subtree energy accounts. Coordinate extrema are recorded
and must stay inside the already declared scale and fold-angle domain. A half-timestep depth-three
run checks numerical refinement.

## Interpretation

If depth 2 to depth 3 becomes resolved only after 0.05 seconds, the prior negative result is
best interpreted as a bounded observation-window result and evidence of delayed transmission
under the current model.

If the difference remains unresolved through 0.1 seconds, that strengthens the evidence for
strong depth attenuation over the tested interval but still does not establish a zero or
infinite-depth limit.

Neither result justifies changing connector strength or material scaling solely to make deeper
levels influence the root.
