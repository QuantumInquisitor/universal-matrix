# Terryology and Terryen geometry audit v0.1

## Decision

The engine admits this material in two sharply separated forms:

1. **Terryology arithmetic claims** are recorded and tested against their stated
   rules. They do not replace ordinary arithmetic because the proposed
   `1 times 1 = 2` definitions fail required algebraic laws.
2. **Terryen Wave Field counts** are retained as a source-defined configuration
   sequence. The counts `4, 8, 6, 12, 24` admit a useful candidate mapping to
   exact regular geometry already present in the engine.

The geometric match is mathematically real. It is not evidence that the
source's electromagnetic, particle, chemical, biological, or cosmological
interpretations are physically correct.

## Names and sources

The name **Terryology** comes from Erik Hedegaard's 2015 interview with
Terrence Howard. The interview describes it as a language of logic devised by
Howard and reports his claim that one times one equals two.

Howard's 2019 book does not use `Terryology` as its internal technical name.
It uses **Terryen Wave Fields** and **Terryen Wave Conjugations** for the named
geometries. These terms should not be silently treated as synonyms:

| Term | Role in this audit |
|---|---|
| Terryology | public label for Howard's proposed logic and arithmetic system |
| Terryen Wave Fields | the five named 4, 8, 6, 12, and 24 bubble configurations |
| Terryen Wave Conjugations | Howard's broader geometric and physical interpretation |
| Lynchpin / AllShape | related mechanical and curvilinear geometry audited separately |

Primary and direct sources:

- Terrence Howard, *One Times One Equals Two*, 2019, stable PDF mirror:
  https://monexpansion.com/wp-content/uploads/2024/05/Terrence-Howard.pdf
- Erik Hedegaard, “Terrence Howard's Dangerous Mind,” *Rolling Stone*, 2015:
  https://au.rollingstone.com/culture/culture-news/terrence-howards-dangerous-mind-841/
- Terrence Howard, full address and questions at the Oxford Union:
  https://www.youtube.com/watch?v=ca1vIYmGyYA
- Oleg Musin, “The Kissing Number in Four Dimensions,” 2003:
  https://arxiv.org/abs/math/0309430

The original book PDF was published on a Howard-associated domain, but that
domain no longer hosts a trustworthy project landing page. The stable mirror
above is used for reader safety. Page references below refer to the printed
page numbers in the book.

## Source claim ledger

| Claim | Pages | Audit status | Finding |
|---|---:|---|---|
| ordinary `1 times 1` should equal `2` | 15 to 24 | inconsistent with stated axioms | a multiplicative identity necessarily gives `1 times 1 = 1` |
| a nonterminating decimal prevents an exact square root of two | 26, 51 to 57, 61, 74 to 77 | category error | an algebraic number can be exact without having a terminating decimal expansion |
| physical “nothing” invalidates mathematical zero | 94 to 97 | category error | an additive identity is not a claim about the physical contents of a vacuum |
| five fields contain `4, 8, 6, 12, 24` meeting bubbles | 135, 137, 139, 140, 141 | source reported | the names and counts are explicit, but unique coordinates are absent |
| the forms determine particles, hydrogen, light, gravity, electricity, and magnetism | 135 to 145 | untested physical | no quantitative equations, data, uncertainty, or falsification criterion are supplied |
| `1 times 1` first equals two, then all things, and ultimately one | 149 | underspecified | one ordered input pair cannot have multiple outputs without another state or rule |

## Why ordinary one times one equals one

In any algebra with multiplicative identity `1`, the definition of identity is

`1 times a = a times 1 = a`.

Set `a = 1`. It follows immediately that

`1 times 1 = 1`.

This conclusion does not depend on flat space, curved space, physical units,
the shape of a drawn region, or a convention about decimal notation. It follows
from the role assigned to the symbol `1` and the operation called
multiplication.

If ordinary equality is also retained, asserting both `1 times 1 = 1` and
`1 times 1 = 2` makes `1 = 2`. In a ring-like number system that identification
collapses all values into the trivial system. A nontrivial alternative must
therefore change the operator, the identity, the objects, or the meaning of
equality and state those changes explicitly.

## Literal repeated-addition audit

Pages 15 and 16 instruct the reader to start with `a` and “add `a` to itself”
as many times as there are units in `b`. Read literally on nonnegative integer
counts, this gives

`H(a, b) = a(b + 1)`.

It is an off-by-one variant of repeated addition. It does produce
`H(1, 1) = 2`, but its exact behavior is:

| Property | Result | Counterexample or reason |
|---|---|---|
| commutative | no | `H(1, 2) = 3`, while `H(2, 1) = 4` |
| associative | no | `H(H(1,1),1) = 4`, while `H(1,H(1,1)) = 3` |
| left distributive over ordinary addition | no | `H(a,b+c) = a(b+c+1)`, not `a(b+c+2)` |
| right distributive over ordinary addition | yes | linearity in the first input preserves this one law |
| two sided identity | none | `0` is a right identity, but not a left identity |

The book invokes the associative and commutative laws while defining an
operation that fails both. That is a decisive internal inconsistency, not an
appeal to authority or preference for familiar notation.

## Single-entry patch audit

A more charitable possibility is to keep the ordinary multiplication table
and change only the `1,1` entry:

`P(a,b) = 2` when `a = b = 1`, and `P(a,b) = ab` otherwise.

This patch is commutative, but it is not associative:

`P(P(1,1),2) = P(2,2) = 4`,

while

`P(1,P(1,2)) = P(1,2) = 2`.

It is also not distributive:

`P(1,1+1) = 2`,

while

`P(1,1) + P(1,1) = 4`.

It has no two sided identity. Therefore `1 times 1 = 2` cannot be inserted as
an isolated correction while retaining the rest of ordinary arithmetic.

## The part that can be preserved

Howard repeatedly expresses the intuition that an interaction should retain
or count both participants. There is a completely consistent operation for
that idea:

`a union-count b = a + b`.

Then `1 union-count 1 = 2`. This operation is associative and commutative and
has identity `0`. It is addition or disjoint composition, not multiplication.
Giving it a distinct name prevents a semantic idea from contradicting the
algebra already attached to `times`.

The engine therefore preserves this as a **renamed operation**, not as a
replacement multiplication table.

## Exact square root of two

A finite decimal expansion is not the definition of exactness. The number
`sqrt(2)` is the positive root of the exact polynomial

`x squared - 2 = 0`.

The implementation represents every number in `Q(sqrt(2))` as an exact pair
of rational coefficients:

`a + b sqrt(2)`.

Multiplication uses

`(a + b sqrt(2))(c + d sqrt(2)) = (ac + 2bd) + (ad + bc)sqrt(2)`.

It verifies exactly that

`sqrt(2) squared = 2`

and

`sqrt(2) cubed = 2 sqrt(2)`.

The second relation, emphasized in the book as a puzzling return, is a valid
algebraic identity. Equivalently, `sqrt(2)` is a fixed point of the nonlinear
map `F(x) = x cubed / 2`. The complete real fixed-point set is
`{-sqrt(2), 0, sqrt(2)}`. This can be useful as a recurrence or dynamics idea,
but it does not invalidate conventional multiplication.

For the book's finite decimal `1.414213562373095`, the engine computes the
square residual exactly as a rational number. It is small but nonzero, exactly
as expected for a truncated approximation.

## Zero and division by zero

Zero plays several distinct roles that must not be conflated:

- a digit in positional notation;
- the additive identity;
- the cardinality of an empty set;
- a zero value of a field or observable;
- a philosophical or physical claim about “nothingness.”

Ordinary multiplication by zero follows from distributivity:

`a times 0 = a times (0 + 0) = a times 0 + a times 0`.

Subtract `a times 0` from both sides to obtain `a times 0 = 0`.

Division by zero is different. Solving `0 times x = a` gives:

- no solution when `a` is nonzero;
- every `x` as a solution when `a = 0`, so no unique quotient.

Thus multiplication by zero is well-defined while division by zero is not.
The fact that multiplication and division are related does not require every
element to possess a multiplicative inverse. Zero is precisely the exception.

## Dimensions and physical units

The arithmetic coefficient and the physical dimension are separate data:

`(1 metre)(1 metre) = 1 square metre`.

The coefficient remains `1`; the length exponent changes from `1 + 1` to `2`.
No alternative scalar multiplication is needed. The implementation tests this
with an exact rational coefficient and an integer unit exponent.

## Terryen source sequence

The five primary wave-field pages report:

| Source name | Page | Reported bubbles | Candidate regular vertex model | Ambient dimension |
|---|---:|---:|---|---:|
| Tetra-Terryen | 135 | 4 | tetrahedron | 3 |
| Huntyen | 137 | 8 | cube | 3 |
| Mira | 139 | 6 | octahedron | 3 |
| Aubreyen | 140 | 12 | icosahedron | 3 |
| Heavenly | 141 | 24 | regular 24-cell | 4 |

This candidate correspondence is not based only on matching counts. Every
candidate uses an equal-radius, centered vertex orbit, and the engine computes
its minimum angular separation:

| Candidate | Maximum pairwise cosine | Minimum angle | Equal central-sphere shell |
|---|---:|---:|---|
| tetrahedron | `-1/3` | `109.4712206345` degrees | nonoverlapping |
| cube | `1/3` | `70.5287793655` degrees | nonoverlapping |
| octahedron | `0` | `90` degrees | nonoverlapping |
| icosahedron | `1/sqrt(5)` | `63.4349488229` degrees | nonoverlapping |
| 24-cell | `1/2` | `60` degrees | exact touching configuration in 4D |

Here “equal central-sphere shell” means a specific test interpretation: equal
outer spheres touch one equal central sphere and must not overlap each other.
It does not claim this is the unique interpretation of Howard's drawings. His
text often discusses the negative void between meeting bubbles rather than a
central material sphere.

## Exact mirror, dual, and dimensional relations

Three relations make the candidate map structurally useful for the engine.

### Four plus mirror gives eight

The exact tetrahedron vertex set is not centrally symmetric. Adjoining its
central mirror produces eight points, and the engine proves that their union is
exactly the cube vertex set:

`tetrahedron union mirrored tetrahedron = cube`.

This connects Tetra-Terryen `4` to Huntyen `8` using the mirror principle
already required by the Universal Playing Field model. It is an exact geometry
result inside the candidate mapping. Howard's source does not explicitly prove
this coordinate identity.

### Eight and six are dual

The cube and octahedron are exact Platonic duals:

- cube signature: `8 vertices, 12 edges, 6 faces`;
- octahedron signature: `6 vertices, 12 edges, 8 faces`.

Their vertex and face counts exchange. This gives a rigorous inside-out relation
between the Huntyen `8` and Mira `6` candidates.

The same inside-out structure spans the full candidate sequence:

- the tetrahedron has signature `4, 6, 4` and is self-dual;
- the cube `8, 12, 6` and octahedron `6, 12, 8` are mutual duals;
- the icosahedron `12, 30, 20` is dual to the dodecahedron `20, 30, 12`, so
  the 12 Aubreyen directions are also the 12 dodecahedral face-normal rays;
- the 24-cell has signature `24, 96, 96, 24` and is self-dual.

This is the exact form of the engine's “inside is also outside” principle for
these candidates. Duality exchanges vertices with faces or cells while
preserving the common symmetry structure.

### Four lifts to twenty-four

The existing engine derives the full regular 24-cell from directed edge roots
of either tetrahedron in the mirrored pair. The result has:

- 24 equal-radius vertices;
- 96 edges;
- 96 triangular faces;
- 24 octahedral cells;
- full symmetry order 1,152.

This gives a bottom-up exact path from the tetrahedral seed to the proposed
Heavenly `24` candidate. It is a mathematical dimensional lift, not a claim
that a photographed 3D sculpture literally occupies four spatial dimensions.

## Kissing-number dimensional test

The kissing number is the maximum number of equal nonoverlapping spheres that
can touch one equal central sphere. The exact values through dimension four are:

| Dimension | Kissing number |
|---:|---:|
| 1 | 2 |
| 2 | 6 |
| 3 | 12 |
| 4 | 24 |

Therefore:

- the `4`, `6`, `8`, and `12` candidates are feasible directional shells in 3D;
- `24` is impossible in 3D under this equal-sphere interpretation;
- `24` is exact in 4D, where the regular 24-cell supplies the configuration.

Musin's proof establishes the four-dimensional maximum `k(4) = 24` and notes
the established three-dimensional result `k(3) = 12`.

This is the strongest new geometric result from the audit. The Heavenly count
is not merely another 3D Platonic count. Under a precise equal-sphere model it
is a genuine signal to move from three to four dimensions.

## What has and has not been established

Established exactly:

- the source uses the public name Terryology and the book names Terryen fields;
- the book's five primary counts are `4, 8, 6, 12, 24`;
- both tested versions of `1 times 1 = 2` fail ordinary algebraic requirements;
- `sqrt(2)` has an exact algebraic representation;
- zero and physical emptiness are different categories;
- the five counts match exact equal-radius regular vertex sets;
- tetrahedron plus central mirror equals cube;
- cube and octahedron are dual;
- the tetrahedron and 24-cell are self-dual, while the Aubreyen directions
  coincide with the face-normal orbit of the dodecahedron;
- the tetrahedral edge-root construction generates the 24-cell;
- a 24-sphere equal-kissing configuration requires at least four dimensions.

Not established:

- that Howard intended these exact coordinates or this polytope sequence;
- that the rendered void surfaces are uniquely determined by the counts;
- that a 3D rendering of the Heavenly form is a physical 4D object;
- that any form represents hydrogen, a photon, the Higgs field, gravity,
  electricity, magnetism, dark matter, or a vacuum state;
- that the forms produce propulsion, energy gain, healing, or material effects;
- that Terryology replaces ordinary arithmetic.

## Implemented tests

The executable audit verifies:

- complete source claim and wave-field registries;
- ordinary multiplication laws and identity on the audit domain;
- exact counterexamples for the literal and single-entry altered products;
- the consistent renamed participant-count operation;
- exact arithmetic in `Q(sqrt(2))`;
- exact residual of a finite decimal approximation;
- the zero-product solution cases;
- coefficient and unit-exponent separation;
- all five candidate point counts and ambient dimensions;
- common radius for every candidate orbit;
- pairwise cosine and angular-separation certificates;
- 3D and 4D kissing-number gates;
- tetrahedral mirror completion to the cube;
- cube and octahedron dual signatures;
- the full candidate sequence's dual and self-dual incidence signatures;
- generation of the 24-cell from either tetrahedral parity.

## Next experimental gate

The next useful geometry test is to reconstruct each pictured negative-space
surface from a declared sphere model. Each case needs:

1. sphere centers and radii;
2. whether spheres intersect, touch pairwise, or only share a central shell;
3. an implicit equation for the retained void boundary;
4. topology and connected-component checks;
5. symmetry comparison with the candidate regular vertex orbit;
6. projection rules for the 24-point 4D case;
7. a quantitative physical observable if any field interpretation is proposed.

Only after those inputs are specified should simulation be used to test
pressure, electromagnetic, acoustic, material, or propulsion claims.
