# Annular junction edge ports v0.1

## Purpose

The connector-topology audit showed that the existing rectangular junction
ports cannot be swept nonsingularly into the annular poloidal cut of a toroidal
edge channel.

This checkpoint redesigns the external edge ports of the conservative junction
as annuli while preserving the same node balance and deterministic
inlet-to-outlet transfer logic.

## One annular band per incident edge

The junction is an annular cylindrical control volume. Its lower and upper
faces share a common radial interval.

Negative signed outward flux is assigned to the lower face as an inlet.
Positive signed outward flux is assigned to the upper face as an outlet.
A zero-current edge still receives one annular band, placed by its graph
source/target role.

Ports on each face partition the available radial interval into disjoint
concentric annular bands.

## Common cumulative-flux coordinate

Each face orders its ports by edge index and assigns each port an interval in a
cumulative flux coordinate.

The interval length equals the magnitude of that edge's boundary flux.

An inlet-to-outlet transfer amount is therefore the overlap length of one inlet
flux interval with one outlet flux interval. This reproduces the deterministic
transport decomposition without requiring a rectangular lane for each pair.

## Connector-compatible boundary profile

For local annular coordinate q in [0,1], define

H(q) = (2q-q^2)^3.

Its derivative is

H'(q) = 6(1-q)(2q-q^2)^2.

For an edge with magnitude F and annular width w, the face streamfunction
increments by

F H(q)/(2 pi).

The resulting axial current density is

J_z = F H'(q)/(2 pi r w).

This is exactly the source normal-density profile used by the annular Piola
connector derived from the toroidal cut flux measure.

Thus every external edge port now has both the topology and the pointwise flux
profile required by the connector.

## Divergence-free internal transfer

Let Psi_lower(r) and Psi_upper(r) be the cumulative streamfunctions on the two
faces. Interpolate them through the junction with

Psi(s,r) = (1-h(s)) Psi_lower(r) + h(s) Psi_upper(r),

where h(s)=3s^2-2s^3.

In cylindrical coordinates around the junction axis,

J_z = (1/r) partial_r Psi,

J_r = -(1/r) partial_z Psi.

This streamfunction form is divergence-free.

Because the lower and upper cumulative flux totals agree at both radial side
walls, radial side-wall flux also vanishes.

## What is established

The implementation verifies:

- one annular band per incident graph edge;
- exact signed surface flux for every port;
- annular topology for zero and nonzero edge ports;
- deterministic inlet/outlet transfer amounts from cumulative-flux intervals;
- pointwise boundary-profile agreement with the Piola connector source profile;
- numerical divergence convergence to zero;
- zero radial side-wall current;
- complete Vesica and Flower/Tree annular junction networks;
- graph edge-flux and node-balance preservation;
- disjoint node control volumes;
- rejection of unbalanced nodes and invalid geometry.

## Evidence boundary

This checkpoint establishes local connector compatibility, not a complete
global embedding.

The annular junctions are placed as disjoint local control volumes, while the
cut-open toroidal channels retain their own local charts. Rigid frame
orientation, source/target connector direction, physical separation of the two
cut copies, and collision-free global routing of all connectors remain open.

## Next gate

Build a framed edge assembly that contains:

1. one source annular junction port;
2. one Piola connector into the inlet copy of the cut-open toroidal channel;
3. the cut-open toroidal current domain;
4. one exit connector from the outlet copy;
5. one target annular junction port.

The assembly must preserve vector orientation and signed flux for positive,
negative, and zero graph currents and must expose collision checks for a full
network embedding.
