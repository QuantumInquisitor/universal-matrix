# Recursive upstream-parent drive audit

The causal replay experiment showed that deep work suppression is dominated by the actual
trajectory delivered by the upstream parent. Restoring downstream descendants changed the work
fraction by less than one percent over the tested interval.

This checkpoint measures what is different about the upstream drive itself.

## Corresponding comparison

For each representative full-tree edge:

- level 1: node 0 to node 1, parent scale 1;
- level 2: node 1 to node 3, parent scale 1/2;
- level 3: node 3 to node 7, parent scale 1/4;

the embedded state at physical time t is compared with the corresponding isolated-pair state at
reference time t/s, where s is the parent scale.

That time mapping follows the already verified dynamic similarity law.

## Drive observables

The report compares:

- parent generalized displacement magnitude from the material reference;
- parent rate magnitude multiplied by parent scale;
- child displacement and scale-normalized rate;
- mapped parent-child port separation in metres;
- connector potential;
- parent and child generalized force magnitudes;
- instantaneous parent and child connector power.

Each magnitude is reported as embedded / isolated at the corresponding scaled time.

The report also records a generalized-coordinate power factor,

P / (norm(F) norm(qdot)),

for parent and child endpoints. This is an energy-flow diagnostic showing force-velocity
alignment. It is not promoted to a universal geometric phase because the generalized coordinates
mix scale and angular components.

## Interpretation

A strong reduction in parent displacement/rate or relative port separation would show that the
recursive signal is attenuated before the next interface is driven.

A similar drive amplitude but strongly different power factor would instead identify phase
misalignment as the dominant effect.

The audit does not change any coefficient, infer a new coupling, validate a spatial recursive
assembly or establish arbitrary depth.
