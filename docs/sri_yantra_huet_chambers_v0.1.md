# Huet Sri Yantra 43-Chamber Extraction v0.1

## Purpose

The Huet planar checkpoint reconstructs the nine maximal concurrent triangles.
This checkpoint derives the traditional forty-three subsidiary chambers from
that linework.

The chamber coordinates are not stored as a table.

## Sourced chamber contract

Chiodo's 2021 paper records the traditional description as:

- one central triangle;
- an enclosure of 8 triangles;
- an enclosure of 10 triangles;
- a second enclosure of 10 triangles;
- an enclosure of 14 triangles.

The same paper identifies the central triangle as the intersection of t1 and
t5 and shows the concentric rows in Figure 2.b.

The count

1 + 8 + 10 + 10 + 14 = 43

is therefore an input constraint from the documented Sri Yantra tradition.
Which actual triangles in the Huet coordinate arrangement satisfy that
constraint is computed.

## Arrangement reconstruction

The extractor begins with the 27 finite sides of the nine maximal Huet
triangles.

It then:

1. computes every pairwise segment intersection;
2. merges numerically coincident concurrency points;
3. obtains 69 arrangement nodes;
4. connects any two nodes that lie on the same original maximal-triangle side;
5. enumerates every nondegenerate three-node circuit whose three sides are
   supported by the original linework.

The Huet reference produces 122 possible triangular circuits before the
traditional concentric-ring conditions are applied.

This is why a generic planar-face polygonization is not the chamber
definition.

## Nine symmetry-axis anchors

After reflection across the common symmetry axis, the arrangement contains
nine atomic axis-symmetric triangular circuits.

They are found geometrically by requiring that:

- the candidate is its own mirror;
- no other arrangement node lies strictly inside it;
- no original maximal-triangle segment enters its interior.

One of those nine is uniquely supported by t1 and t5. It is the central
triangle.

The remaining eight occur as four nested left-right pairs along the rotated
symmetry axis. From the centre outward those pairs anchor the 8, 10, 10, and
14 chamber rings.

## Ring extraction

For a ring containing N chambers, two chambers are its axis anchors.

The upper half must therefore contain

(N - 2) / 2

intermediate chambers.

The engine enumerates candidate chains between the two anchors and requires
consecutive chambers to meet at exactly one arrangement vertex. It reflects
the upper chain to form the lower half.

A ring candidate is rejected if any two of its chambers:

- overlap in positive area; or
- share positive edge length.

Finally the four rings are combined with the central chamber. The same
non-overlap rule is enforced globally.

For the Huet reference geometry there is exactly one complete solution.

## Derived result

The unique solution contains:

| enclosure | chambers | unique circuit vertices |
| --- | ---: | ---: |
| central | 1 | 3 |
| eight | 8 | 16 |
| inner ten | 10 | 20 |
| outer ten | 10 | 20 |
| fourteen | 14 | 28 |

Total chamber count:

43

Total chamber sides:

129

All 129 chamber sides are distinct.

Each of the four noncentral enclosures is a vertex-touching cycle: every
chamber meets exactly two chambers of its own ring at one vertex.

Every ring is closed under the exact planar reflection.

## What has been derived

The repository no longer carries the number 43 only as an inventory statement.

For the Huet reference solution it now derives:

- the chamber vertex coordinates;
- the membership of every chamber in one of the five concentric circuits;
- the complete 43-member chamber set;
- mirror pairing;
- ring-cycle adjacency;
- the 129 distinct chamber sides;
- the 3, 16, 20, 20, and 28 circuit-vertex counts.

## Evidence boundary

The ring counts are sourced properties of the Sri Yantra and are used as the
target combinatorial contract.

The individual chamber coordinates and the fact that the Huet arrangement has
exactly one globally admissible chamber system are computational results of
this implementation.

This checkpoint does not establish that the current candidate spherical,
spiral-cone, or Meru realizations preserve the newly derived 43-chamber
incidence.

It also does not make the traditional chamber count identical to the
repository's canonical 108-state processor.

## Next gate

Lift this derived 43-chamber incidence complex into the nonplanar Sri Yantra
realizations and test the map explicitly.

The next comparison should answer:

- which chamber vertices remain distinct;
- which chamber adjacencies are preserved;
- whether any edges cross or chambers collapse;
- whether mirror pairing commutes with the lift;
- whether the 8, 10, 10, and 14 cycles remain cycles.

A topology-changing claim is allowed only if one of those tests actually
fails.

## Primary source

Alessandro Chiodo, "On the construction of the Sri Yantra",
Comptes Rendus Mathematique 359 (2021), 377-397.
DOI: 10.5802/crmath.163.
