# Canonical Mathematical Specification v0.4

This document freezes the finite discrete mathematical kernel currently implemented in `src/canonical_kernel.py`. It does not assert a physical theory.

## 1. Architecture

The internal core is the cyclic label space

```
C = Z_108
```

and the external boundary is a separate six-element set

```
B = {+X, -X, +Y, -Y, +Z, -Z}.
```

The implementation assigns the boundary labels to node IDs 108 through 113. Thus the complete architectural inventory has 114 positions, but the routing algebra is not `Z_114`.

The six oriented boundary vectors form the vertices of an octahedron. Their abstract signed-permutation symmetry has order

```
2^3 * 3! = 48.
```

This order-48 fact follows from the boundary geometry itself and does not depend on the legacy decimal-stream arithmetic.

## 2. Interface, polarity, and reflection

Define translations on `Z_108` by `T_d(n)=n+d mod 108`.

The interface operator is

```
E = T_9.
```

It has order 12:

```
E^12 = I.
```

The polarity operator is

```
P = T_54,
```

so

```
P^2 = I
E^6 = P.
```

The reflection is

```
F(n) = 107 - n mod 108.
```

It satisfies `F^2=I` and reverses translations.

## 3. Routing synchronization class

A routing step must preserve the three residue classes modulo 3, generate a 36-state cycle in each class, and satisfy

```
T^3 = E^7.
```

Within positive steps below 108, these constraints admit exactly

```
{21, 57, 93}.
```

Therefore synchronization alone does not uniquely derive 21.

The canonical implementation chooses

```
T = T_21
```

by the **minimal-positive-lift convention**. Dividing the candidates by the three routing channels gives reduced steps

```
7, 19, 31,
```

all congruent to 7 modulo 12. The representative 7 is the smallest positive lift, giving 21 in the core.

For the selected routing operator,

```
T^36 = I
T^18 = P
T^3 = E^7.
```

The three routing orbits are exactly the residue classes modulo 3, each of length 36.

## 4. Register projection

The 64-address register projection is

```
pi(n) = 7n mod 64.
```

This is a projection from canonical representatives of `Z_108`; it is not a group homomorphism from `Z_108` to `Z_64`.

For a canonical translation by `0 <= d < 108`, define the carry indicator

```
w_d(n) = 1 if n >= 108-d, otherwise 0.
```

Then

```
Delta pi = 7d + 12 w_d(n) mod 64.
```

The +12 correction is the register image of subtracting 108 during a core wrap because `-7*108 = -756 = 12 mod 64`.

For the three synchronized routing lifts, per 36-state orbit:

| step | reduced step | nonwraps | wraps | nonwrap delta | wrap delta |
|---:|---:|---:|---:|---:|---:|
| 21 | 7 | 29 | 7 | 19 | 31 |
| 57 | 19 | 17 | 19 | 15 | 27 |
| 93 | 31 | 5 | 31 | 11 | 23 |

Across all three routing orbits, multiply the wrap and nonwrap counts by three.

## 5. Register collisions

Because 7 is invertible modulo 64,

```
pi(n)=pi(m) iff n=m mod 64
```

for canonical representatives in 0 through 107.

Therefore the projection has exactly 44 double-hit addresses and 20 single-hit addresses:

```
44*2 + 20 = 108.
```

The double-hit pairs are

```
(n, n+64), 0 <= n <= 43.
```

These pairs define the current register-coupling relation used in graph analysis. Treating equal register addresses as actual dynamical coupling is a model choice, not a consequence of the projection alone.

## 6. Mixed-radix coordinates

Every core state has a unique representation

```
n = r + 3q + 9s + 27u
```

with

```
r,q,s in {0,1,2}
u in {0,1,2,3}.
```

This is a mixed-radix coordinate system of cardinality

```
3*3*3*4 = 108.
```

It is a set-coordinate decomposition, not a claim that `Z_108` is the direct product of those factors.

## 7. What is canonical and what is not

Canonical in v0.4:

- 108-state cyclic internal label space
- six external oriented boundary gates
- interface step 9
- polarity step 54
- register projection multiplier 7
- synchronized routing class {21,57,93}
- minimal-positive-lift convention selecting routing step 21
- reflection F(n)=107-n
- mixed-radix encoding
- projection carry law
- exact register-collision multiplicities

Not foundational in v0.4:

- decimal streams 123456789 and 987654321
- modulus-31 closure
- the historical Axiom-I arithmetic
- calibrated speed-of-light expressions
- 3/6/9 masks as transition operators
- toroidal physical geometry
- gravitational, quantum, biological, consciousness, black-hole, or white-hole interpretations

Those may be studied as secondary hypotheses or experimental mappings, but they are not mathematical consequences of this kernel.



## 7A. Derived mod-9 quotient audit

Reduction modulo nine is an exact quotient of the additive core because nine
divides 108. It labels the nine orbits of (E=T_9).

Every canonical representative has a unique set-coordinate decomposition

$$
n=r+9k,\qquad 0\le r<9,\quad 0\le k<12.
$$

Thus the core has nine interface fibers with twelve phases in each fiber.

This is a derived audit, not an additional canonical transition definition.
Multiplication by two in $\mathbb Z_9$ has orbit partition

$$
(0),\quad (3,6),\quad (1,2,4,8,7,5).
$$

but that automorphism is distinct from the additive canonical operators.
Executable details are in
`src/canonical_mod9_interface_audit.py` and
`docs/canonical_mod9_interface_audit_v0.1.md`.

## 8. Implementation authority

The executable reference is `src/canonical_kernel.py`. Regression identities are in `tests/test_canonical_kernel.py`.

Legacy modules may retain compatibility aliases while migration is in progress. Any conflict between a legacy module and the canonical kernel is a migration defect, not an alternate definition of the architecture.
