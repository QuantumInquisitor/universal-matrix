# The Universal Matrix: A Finite Discrete Architecture with a 108-State Core, Six Boundary Gates, and a 64-Address Projection

**Malakhiyah**  
*Working Mathematical Preprint — Version 0.4*

---

## Abstract

This paper defines a finite discrete architecture consisting of a 108-state cyclic internal core and six external oriented boundary gates. The core is labeled by the cyclic group (mathbb{Z}_{108}); the six boundary states are separate from that routing group and are associated with the orientations (+X,-X,+Y,-Y,+Z,-Z). The architecture includes an order-12 interface translation (E=T_9), an order-two polarity translation (P=T_{54}), a reflection (F(n)=107-n), and a 64-address projection (pi(n)=7nmod 64). A routing synchronization condition admits three positive routing lifts, (21,57,93); the present implementation selects (21) by a minimal-positive-lift convention, giving three disjoint routing cycles of length 36. We derive the carry-aware projection law, the exact register-collision multiplicities, a mixed-radix coordinate representation of the 108 core states, and the order-48 abstract symmetry of the six oriented boundary directions. The purpose of this paper is to state the finite mathematics precisely and to separate proved properties from conventions and physical hypotheses. No claim is made here that the discrete architecture replaces established gravitational, quantum, or other physical theories.

---

## 1. Scope and Mathematical Status

The Universal Matrix is treated here as a finite mathematical model. Its canonical architecture is

[
mathcal{A}=mathbb{Z}_{108}sqcup B_6,
]

where

[
B_6={+X,-X,+Y,-Y,+Z,-Z}.
]

The symbol (sqcup) is important: the six boundary states are not additional elements of the cyclic routing group. The complete implementation therefore contains 114 labeled positions, but its internal routing algebra is (mathbb{Z}_{108}), not (mathbb{Z}_{114}).

This distinction removes an ambiguity present in earlier versions of the framework. Internal translations are evaluated modulo 108. The six external states form a boundary interface with the core rather than extending its cyclic modulus.

Throughout this paper, statements are classified implicitly by their mathematical role:

- a **definition** introduces an object or coordinate convention;
- a **theorem/proposition** follows from stated definitions and assumptions;
- a **convention** selects one representative when the mathematics admits more than one;
- a **computational observation** records a finite property verified exhaustively;
- a **physical hypothesis** would require independent empirical validation and is not part of the canonical kernel.

---

## 2. Boundary Architecture

### 2.1 Six Oriented Gates

Let the boundary orientations be represented by the six unit vectors

[
B_6={pm e_x,pm e_y,pm e_z}.
]

In the reference implementation these are assigned the external labels 108 through 113:

[
108leftrightarrow +X,quad
109leftrightarrow -X,quad
110leftrightarrow +Y,quad
111leftrightarrow -Y,quad
112leftrightarrow +Z,quad
113leftrightarrow -Z.
]

The numerical labels are implementation coordinates. The mathematical boundary object is the six-element oriented set itself.

### 2.2 Boundary Symmetry

The six vectors ({pm e_x,pm e_y,pm e_z}) are the vertices of a regular octahedral configuration. A signed permutation of three coordinate axes consists of:

1. an arbitrary permutation of the three axes, giving (3!) possibilities; and
2. an independent sign reversal on each axis, giving (2^3) possibilities.

Therefore the full signed-permutation group acting on the boundary has order

[
|G_B|=2^3,3!=48.
]

This is the hyperoctahedral group in three dimensions,

[
G_Bcong C_2^3times S_3,
]

also identifiable with the Weyl group (W(B_3)cong W(C_3)).

The number 48 therefore follows directly from the six-direction boundary geometry. No decimal-stream remainder calculation is required to obtain it.

---

## 3. The 108-State Core

Let

[
C=mathbb{Z}_{108}.
]

For any integer (d), define the translation

[
T_d(n)=n+dpmod{108}.
]

Composition satisfies

[
T_aT_b=T_{a+b},
]

and

[
T_d^{-1}=T_{-d}.
]

### 3.1 Interface Translation

Define

[
E=T_9.
]

Because

[
rac{108}{gcd(108,9)}=12,
]

(E) has order 12:

[
E^{12}=I.
]

The sequence generated from any state by repeated application of (E) therefore closes after 12 steps.

### 3.2 Polarity Translation

Define

[
P=T_{54}.
]

Since

[
2(54)=108,
]

we have

[
P^2=I.
]

Moreover,

[
E^6=T_{6cdot9}=T_{54}=P.
]

Thus the interface cycle contains a distinguished half-cycle involution.

The map (P) has no fixed state in (mathbb{Z}_{108}). Consequently it partitions the core into exactly

[
108/2=54
]

unordered antipodal pairs

[
{n,n+54}.
]

This provides a mathematically exact 54-pair structure. Terms such as inward/outward may be assigned to the two orientations of each pair as an additional interpretation, but the pairing itself is purely algebraic.

---

## 4. Routing

### 4.1 Three Routing Channels

Any translation whose step is divisible by 3 preserves the residue

[
ho(n)=nmod3.
]

Thus the core decomposes into the three channel sets

[
O_r={ninmathbb{Z}_{108}:nequiv rpmod3},
qquad r=0,1,2.
]

Each contains 36 states.

### 4.2 Synchronization Constraint

We require a routing translation (T=T_t) to satisfy:

1. it preserves the three channels;
2. each channel is traversed as one 36-state cycle;
3. three routing steps equal seven interface steps:

[
T^3=E^7.
]

Since

[
E^7=T_{63},
]

condition 3 requires

[
3tequiv63pmod{108}.
]

Together with the 36-cycle requirement, the positive solutions below 108 are

[
oxed{tin{21,57,93}}.
]

Therefore the synchronization equation does not uniquely derive (t=21).

### 4.3 Minimal-Positive-Lift Convention

Divide the three candidates by the channel factor 3:

[
21/3=7,qquad57/3=19,qquad93/3=31.
]

These satisfy

[
7equiv19equiv31pmod{12}.
]

The reference architecture chooses the smallest positive representative,

[
oxed{t=21},
]

and therefore

[
T=T_{21}.
]

This is a convention selecting a canonical representative from the synchronization class, not a uniqueness theorem.

### 4.4 Exact Routing Identities

For (T=T_{21}),

[
gcd(21,108)=3.
]

Hence (T) has exactly three cycles, each of length

[
108/3=36.
]

The exact identities are

[
T^{36}=I,
]

[
T^3=E^7,
]

and

[
T^{18}=T_{378}=T_{54}=P.
]

Since (E^6=P),

[
oxed{T^{18}=E^6=P}.
]

The forward and reverse routing operators satisfy

[
T^{-1}=T_{87},
qquad
T^{-1}T=I.
]

This gives an exact operator triad consisting of forward translation, inverse translation, and identity.

---

## 5. Routing Winding

One routing step advances by the fraction

[
rac{21}{108}=rac{7}{36}
]

of a full cyclic turn. Its angular representation is therefore

[
	heta=rac{2pi(21)}{108}=rac{7pi}{18}=70^circ.
]

After 36 routing steps,

[
36(70^circ)=2520^circ=7(360^circ).
]

Thus each 36-state routing orbit performs seven complete angular windings before closure.

A convenient geometric visualization is

[
H(k)=
left(
Rcosrac{7pi k}{18},
Rsinrac{7pi k}{18},
kh
ight),
]

where (R) and (h) are visualization parameters. This is a helix. It is not, by itself, a derivation of a physical torus.

The number seven here denotes winding number. It should not be conflated automatically with any unrelated seven-element physical or symbolic system.

---

## 6. The 64-Address Projection

Define

[
pi:Cightarrowmathbb{Z}_{64}
]

on canonical representatives (0le n<108) by

[
oxed{pi(n)=7npmod{64}}.
]

Because

[
gcd(7,64)=1,
]

multiplication by 7 permutes the 64 register addresses.

However, (pi) is not a group homomorphism from (mathbb{Z}_{108}) to (mathbb{Z}_{64}), because changing a representative by 108 changes (7n) by

[
7(108)=756equiv52
otequiv0pmod{64}.
]

The projection is therefore defined using canonical core representatives.

### 6.1 Interface Projection

For a nonwrapping (+9) step,

[
7(9)=63equiv-1pmod{64}.
]

Thus the interface operator moves locally by one register address in the reverse direction.

This relation determines the multiplier 7 if one adopts the convention that a nonwrapping interface step should correspond to the minimal reverse register displacement:

[
9gequiv-1pmod{64}
]

has the unique solution

[
gequiv7pmod{64}.
]

The reverse-unit requirement itself is an architectural convention; once adopted, the value 7 follows uniquely.

---

## 7. Projection Carry Theorem

Let (0le d<108), and define

[
w_d(n)=
egin{cases}
1,&nge108-d,\
0,&n<108-d.
end{cases}
]

Then the canonical translation is

[
T_d(n)=n+d-108w_d(n).
]

Applying the register projection,

[
egin{aligned}
pi(T_d(n))-pi(n)
&equiv7[d-108w_d(n)]pmod{64}\
&equiv7d+12w_d(n)pmod{64},
end{aligned}
]

because

[
-7(108)equiv12pmod{64}.
]

Therefore

[
oxed{
Deltapiequiv7d+12w_d(n)pmod{64}
}.
]

This formula has been exhaustively checked in the reference implementation for every core state and every displacement (0le d<108).

### 7.1 Routing-Lift Carry Structure

For the three synchronized routing lifts:

| (t) | (t/3) | nonwraps/orbit | wraps/orbit | nonwrap (Deltapi) | wrap (Deltapi) |
|---:|---:|---:|---:|---:|---:|
| 21 | 7 | 29 | 7 | 19 | 31 |
| 57 | 19 | 17 | 19 | 15 | 27 |
| 93 | 31 | 5 | 31 | 11 | 23 |

For (t=21),

[
29(19)+7(31)=768=12(64),
]

so one 36-state routing orbit closes after twelve net register turns.

Across all three routing channels, the corresponding transition counts are 87 nonwrapping and 21 wrapping steps.

---

## 8. Register Collisions

For canonical states (n,min{0,ldots,107}),

[
pi(n)=pi(m)
]

if and only if

[
7(n-m)equiv0pmod{64}.
]

Since 7 is invertible modulo 64,

[
nequiv mpmod{64}.
]

Within the 108 canonical representatives, the repeated-address pairs are therefore exactly

[
(n,n+64),
qquad0le nle43.
]

There are 44 such pairs. The remaining states (44,ldots,63) have no second representative in the core.

Hence the register multiplicities are exactly

[
44	imes2+20	imes1=108.
]

There are:

[
oxed{44	ext{ double-hit addresses}}
]

and

[
oxed{20	ext{ single-hit addresses}}.
]

No register address has three core representatives.

Equal register address does not by itself prove physical or dynamical coupling. A model may add edges between equal-address states, but that is an additional graph construction.

---

## 9. Reflection Symmetry

Define

[
F(n)=107-npmod{108}.
]

Then

[
F^2=I.
]

For every translation (T_d),

[
FT_dF=T_{-d}.
]

In particular,

[
FTF=T^{-1}
]

and

[
FEF=E^{-1}.
]

Also,

[
FP=PF.
]

For the routing subsystem generated by (T=T_{21}) and (F), these relations give a dihedral action on each routing structure.

When equal-register states are additionally connected by the 44 collision edges, exhaustive graph analysis shows that the full graph retains only the two-element automorphism group generated by (F). This is a computational property of that particular added coupling graph, not of the bare cyclic core.

---

## 10. Mixed-Radix Coordinates

Every (nin{0,ldots,107}) can be written uniquely as

[
oxed{n=r+3q+9s+27u}
]

with

[
r,q,sin{0,1,2},
qquad
uin{0,1,2,3}.
]

Therefore the state count factors as

[
108=3cdot3cdot3cdot4.
]

This is a mixed-radix coordinate system. It is not an assertion that

[
mathbb{Z}_{108}cong
mathbb{Z}_3	imes
mathbb{Z}_3	imes
mathbb{Z}_3	imes
mathbb{Z}_4.
]

A coarser representation is

[
n=a+9b,
]

where

[
ain{0,ldots,8},
qquad
bin{0,ldots,11}.
]

In these coordinates,

[
pi(n)=7a-bpmod{64},
]

because

[
7(9b)=63bequiv-bpmod{64}.
]

This compactly exposes the reverse-unit interface behavior.

---

## 11. Six Boundary Gates and Binary Microstates

The six oriented boundary gates do not, by themselves, mathematically imply 64 states.

If each of the six gates is assigned an independent binary variable,

[
b_iin{0,1},
]

then the binary boundary microstate space is

[
{0,1}^6
]

and has cardinality

[
2^6=64.
]

This is a six-bit state space with 64 possible configurations.

It should therefore be described as a **6-bit / 64-state boundary register**, not as a 64-bit architecture.

If opposite directions are instead treated as mutually exclusive ternary states on each spatial axis, the resultant space is

[
{-1,0,+1}^3
]

with

[
3^3=27
]

states.

Thus the number 64 requires the independent-six-binary-channel assumption.

### 11.1 Binary-to-Ternary Resultants

For one oriented axis pair, define

[
(00)mapsto0,quad
(11)mapsto0,quad
(10)mapsto+1,quad
(01)mapsto-1.
]

Across three axes this maps the 64 binary microstates onto the 27 ternary spatial resultants.

The 27 resultants decompose by support size as

[
1+6+12+8=27.
]

The corresponding binary preimage counts are

[
8+24+24+8=64.
]

Two useful centered subsets are:

[
S_7={0,pm e_x,pm e_y,pm e_z},
]

with seven states, and the center-plus-eight-corners subset with nine states.

These are geometric cardinalities. Their numerical agreement with other occurrences of 7 or 9 in the architecture does not, without an explicit mapping, establish that the objects are identical.

---

## 12. Status of the Decimal Streams

The implementation retains the decimal integers

[
S_{mathrm{up}}=123456789,
qquad
S_{mathrm{down}}=987654321
]

as exploratory arithmetic probes.

Their difference is

[
Delta S=864197532.
]

A structurally interesting identity is

[
Delta S=108(8{,}001{,}829),
]

so

[
S_{mathrm{up}}equiv S_{mathrm{down}}pmod{108}.
]

Both are congruent to 45 modulo 108.

This is a valid arithmetic observation, but the streams are not required to define the v0.4 kernel.

The historical modulus-31 expression also remains an exact arithmetic identity in the compatibility layer. It is not used here as a derivation of the core architecture, the boundary symmetry, or a physical law.

---

## 13. Non-Gravitational Physical Program

The Universal Matrix is formulated without gravity as a primitive interaction. Its canonical kernel contains no gravitational force variable, gravitational potential, spacetime metric, curvature tensor, geodesic equation, Newtonian gravitational constant, or Einstein field equation.

General Relativity is therefore not an internal component of the model. If the Universal Matrix is extended from a finite mathematical architecture into a physical theory, phenomena conventionally modeled gravitationally must instead emerge from independently specified Matrix dynamics.

This requirement forbids circular reconstruction. A proposed Matrix extension cannot import a Newtonian potential, Schwarzschild metric, Einstein tensor, fitted gravitational acceleration law, or a mathematically equivalent surrogate and then count the resulting agreement as an independent Matrix prediction.

The central empirical question is:

**Can independently defined Matrix dynamics reproduce measured phenomena conventionally attributed to gravity without assuming a gravitational law?**

The first benchmark selected for this program is differential clock frequency shift. A physical Matrix extension must produce a dimensionless predicted fractional shift between two specified experimental configurations. It must define the observable map, dimensional conversion, dynamics, initial and boundary conditions, numerical prediction, uncertainty, and falsification criterion before comparison with the benchmark measurement.

A disagreement between a future Matrix prediction and a relativistic prediction would become a discriminating test only if experimental uncertainty is small enough to distinguish them. Agreement with an already known observation after fitting free parameters is not an independent prediction.

Version 0.4 does not yet contain the dimensional observable map required to calculate a clock-frequency shift. Consequently the absence of gravity and General Relativity from the kernel is a property of the model, while empirical displacement of General Relativity remains an open test objective rather than a result already obtained.

Other proposed mappings, including quantum-entanglement, black-hole/white-hole, biological, anatomical, chakra, meridian, or consciousness interpretations, likewise require separately stated mappings and tests.

---

## 14. Computational Reference Implementation

The canonical executable specification is maintained in:

```text
src/canonical_kernel.py
```

with regression tests in:

```text
tests/test_canonical_kernel.py
```

The implementation checks, among other identities,

[
E^{12}=I,
qquad
T^{36}=I,
qquad
P^2=I,
]

[
T^3=E^7,
qquad
T^{18}=E^6=P,
]

[
F^2=I,
qquad
FTF=T^{-1},
qquad
FEF=E^{-1},
]

and the projection carry theorem over the complete finite state space.

This executable layer is intended to prevent prose, visualization code, experimental simulations, and compatibility modules from silently redefining the mathematical architecture.

---

## 15. Research Program

The next stage is to treat proposed physical interpretations as explicit extensions rather than assumptions embedded in the kernel. A candidate extension should specify:

1. the observable represented by each mathematical state;
2. units and dimensional mappings;
3. the dynamical law connecting successive states;
4. initial and boundary conditions;
5. a prediction not inserted through calibration;
6. an experimental protocol capable of falsifying that prediction;
7. comparison with the relevant established model.

This separation permits the finite architecture to be evaluated on its own mathematical merits while allowing physical hypotheses to be tested independently.

---

## Conclusion

The v0.4 Universal Matrix is a finite discrete architecture with a clearly separated internal routing space and external boundary:

[
oxed{mathcal{A}=mathbb{Z}_{108}sqcup B_6}.
]

Its principal exact structures are

[
E=T_9,
qquad
P=T_{54},
qquad
F(n)=107-n,
]

the synchronization class

[
{T_{21},T_{57},T_{93}},
]

the minimal-positive-lift convention

[
T=T_{21},
]

and the canonical register projection

[
pi(n)=7npmod{64}.
]

These yield three 36-state routing cycles, a 12-state interface cycle, 54 polarity pairs, seven routing windings for the selected lift, an exact carry-aware register law, 44 double-hit register addresses, 20 single-hit addresses, and an abstract order-48 symmetry of the six oriented boundary directions.

The central result of this revision is not a new physical claim. It is a sharper mathematical object: definitions, theorems, conventions, computational observations, and hypotheses are now separated so that each can be evaluated on its appropriate standard.
