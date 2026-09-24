# Canonical Polarity–Phase Reduction v0.1

## Purpose

This note connects four existing structures:

1. the exact canonical polarity branch $p\in\{0,1\}$;
2. an independent local phase $\phi$;
3. polarity-sensitive link currents;
4. the fixed-amplitude limit of the complex matter sector.

Implementation:

- `src/matrix_polarity_phase_bridge.py`

Tests:

- `tests/test_matrix_polarity_phase_bridge.py`

The goal is to remove duplicated polarity bookkeeping.

## 1. Exact branch sign

The canonical address decomposition is

$$
n=a+54p,
\qquad
p\in\{0,1\}.
$$

Associate the branch sign

$$
s_p=(-1)^p.
$$

Then

$$
p=0\Rightarrow s_p=+1,
$$

and

$$
p=1\Rightarrow s_p=-1.
$$

Under the exact polarity operation $P=T_{54}$,

$$
p\rightarrow1-p,
$$

so the sign reverses.

## 2. Branch as a phase offset

If $\phi$ is an independent local phase, define

$$
\boxed{
\phi_{\rm eff}
=
\phi+\pi p.
}
$$

Then

$$
e^{i\phi_{\rm eff}}
=
(-1)^p e^{i\phi}.
$$

Therefore the exact canonical branch can be represented as a $\pi$ phase
offset without introducing a second independent polarity degree of freedom.

## 3. Polarity-weighted current identity

Consider the polarity-weighted link factor

$$
s_x s_y
\sin\left(
\phi_y-\phi_x+\theta_{xy}
\right).
$$

Using

$$
\phi_{{\rm eff},x}
=
\phi_x+\pi p_x,
$$

and

$$
\phi_{{\rm eff},y}
=
\phi_y+\pi p_y,
$$

we obtain

$$
\boxed{
s_x s_y
\sin\left(
\phi_y-\phi_x+\theta_{xy}
\right)
=
\sin\left(
\phi_{{\rm eff},y}
-
\phi_{{\rm eff},x}
+
\theta_{xy}
\right).
}
$$

The regression tests verify this for all four branch pairings.

This means that when the polarity variable in a current model means exactly the
canonical $T_{54}$ branch, it does not need to be stored independently from
an effective phase representation.

## 4. Fixed-amplitude complex matter reduces to the rotor link

The existing complex matter sector uses the nearest-neighbor term

$$
\left|
e^{i\theta_{xy}}\Phi_y-\Phi_x
\right|^2.
$$

For equal fixed amplitude

$$
|\Phi_x|
=
|\Phi_y|
=
R,
$$

with

$$
\Phi_x
=
R e^{i\phi_{{\rm eff},x}},
$$

and

$$
\Phi_y
=
R e^{i\phi_{{\rm eff},y}},
$$

the link energy becomes

$$
\boxed{
\left|
e^{i\theta_{xy}}\Phi_y-\Phi_x
\right|^2
=
2R^2
\left[
1-\cos\Delta_{xy}
\right]
}
$$

where

$$
\Delta_{xy}
=
\phi_{{\rm eff},y}
-
\phi_{{\rm eff},x}
+
\theta_{xy}.
$$

Therefore the minimal rotor interaction

$$
K
\left[
1-\cos\Delta_{xy}
\right]
$$

is exactly the fixed-amplitude sector of the existing complex matter gradient
when

$$
\boxed{
K=2R^2
}
$$

for the current normalization.

This is an exact algebraic reduction, not an analogy.

## 5. Relation to the canonical polarity clock

The canonical routing operator satisfies

$$
T^{18}=P.
$$

The polarity clock advances by

$$
\Delta\phi_P
=
\pi
$$

over the same 18 routing ticks.

Therefore one half-cycle can be represented either as:

- an exact branch flip $p\rightarrow1-p$, or
- a $\pi$ advance of a phase variable that already represents the canonical
  polarity clock.

If both are applied to the same physical polarity effect,

$$
\pi+\pi=2\pi,
$$

and the sign returns to its original value.

That is a double-counting error.

## 6. Representation rule

The engine should distinguish two cases.

### Independent-phase representation

If $\phi$ is an independent matter or cell phase, canonical polarity may be
encoded by

$$
\phi_{\rm eff}=\phi+\pi p.
$$

### Clock-locked representation

If $\phi$ already is the canonical polarity-clock phase, then the half-cycle
$\pi$ shift already represents the polarity reversal.

Do not multiply by another copy of the same canonical branch sign.

## 7. What this resolves

This reduction answers part of the earlier polarity question.

The engine no longer needs to assume that every appearance of

- polarity branch;
- polarity sign;
- half-cycle phase reversal;
- polarity-sensitive current sign;

represents a separate physical variable.

Several are mathematically reducible to one another.

This reduces the primitive state count and removes one source of accidental
double counting.

## 8. What remains open

The following are still unresolved:

1. whether canonical polarity should physically couple to all matter sectors or
   only selected ones;
2. whether branch flips are dynamical local events or only routing/address
   structure;
3. whether neighboring scales should alternate canonical branch, effective
   phase, interaction orientation, or some combination;
4. whether the observed attraction/repulsion behavior should emerge from link
   energy, gauge charge, geometry, or another invariant;
5. whether variable-amplitude matter dynamically freezes into a rotor-like
   fixed-amplitude sector in any physically relevant regime.

## 9. Next creator question

The next question becomes more precise:

> What dynamical mechanism determines whether amplitude remains free, freezes
> to a stable value, or forms localized defects, and can that mechanism produce
> stable particle-like excitations without inserting particle species by hand?

This moves the program from bookkeeping reduction toward the first genuine
matter-formation problem.

## Status

**Exact algebraic bridge between existing representations, with physical
interpretation still experimental.**
