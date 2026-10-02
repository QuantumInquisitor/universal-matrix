# Isolated versus embedded recursive pair dynamics

The recursive tangent audit showed that every 1:2 parent-child interface is locally self-similar
under the current model, yet the full depth-three tree delivers only a few percent of parent-side
work to deeper children over 0.1 seconds. Static tangent mismatch therefore does not explain the
finite-time attenuation.

This checkpoint separates local pair dynamics from cascade loading and phase history.

## Isolated corresponding pairs

Three isolated pairs are integrated with the same existing material and mapped-connector laws:

- parent 1, child 1/2;
- parent 1/2, child 1/4;
- parent 1/4, child 1/8.

The parent begins with the same generalized displacement used by the recursive tree. Initial
generalized rates are divided by parent scale so the three cases are dynamically corresponding.
Physical timestep and duration scale with parent length, while a common reference-time coordinate
is retained.

At matching reference times the audit compares:

- generalized coordinates;
- parent-scale-normalized rates;
- mechanical and connector energies divided by parent scale cubed;
- endpoint work divided by parent scale cubed;
- child work as a fraction of parent-work magnitude.

Exact collapse is expected if the implemented half-scale pair law is dynamically self-similar.

## Embedded comparison

The same interface levels are then read from the full 15-module depth-three tree at physical
times 0.02, 0.05, 0.075 and 0.1 seconds.

For child level d with parent scale s, the matching isolated reference time is t/s. This is
essential because the existing scale law makes intrinsic time proportional to length.

The embedded parent at levels 2 and 3 is not initialized with the isolated-pair perturbation. It
is driven by its own upstream connector and simultaneously loaded by downstream children.
Therefore disagreement between isolated and embedded work fractions is evidence of cascade
loading, phase history and multi-interface storage, not a failure of the local pair similarity
law by itself.

## Scope

The scale-1/4 to scale-1/8 isolated pair uses the already audited experimental scale-extension
validator. The repository-wide production scale floor remains unchanged.

No connector coefficient, material coefficient, scale exponent or new recursive interaction is
introduced. The experiment does not validate a spatial recursive embedding, arbitrary depth,
measured material properties or correspondence with the 69-component toroidal flow assembly.
