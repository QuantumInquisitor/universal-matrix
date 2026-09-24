# Q-Ball Branch Diagnostics v0.1

## Status

This layer adds differential consistency diagnostics to the controlled radial
charged-matter continuation branch.

It does not replace direct time evolution and does not turn a branch-slope rule
into a universal stability theorem.

## Stationary family identity

For a smooth family of constrained stationary solutions, the repository
normalization implies

$$
\boxed{
\frac{dE}{dQ}
=
\omega.
}
$$

The implementation evaluates finite secants between neighboring accepted branch
points:

$$
\frac{\Delta E}{\Delta Q}
$$

and compares them with the midpoint frequency.

Agreement is a numerical consistency test that the continuation points behave
like one stationary family rather than unrelated BVP roots.

## Charge-frequency slope

The branch diagnostic also records

$$
\frac{dQ}{d\omega}.
$$

For standard one-field Q-ball families, a negative value is commonly associated
with the candidate classically stable branch under the relevant spectral
assumptions.

In this repository that sign is treated only as a branch diagnostic.

Direct nonlinear persistence remains separate evidence.

## Binding threshold

The continuation already shows

$$
E/Q>1
$$

for lower-amplitude points and

$$
E/Q<1
$$

near $A_0=1$.

This layer interpolates the crossing of

$$
E/Q=m_{\rm free}.
$$

That gives an approximate location where the energetic binding diagnostic
changes sign along the tracked family.

## Combined interpretation

The useful hierarchy is now:

1. analytic Q-ball frequency window,
2. converged nodeless continuation,
3. small virial residual,
4. stationary-family check $dE/dQ\approx\omega$,
5. charge-frequency slope diagnostic,
6. $E/Q<m_{\rm free}$,
7. direct 3D persistence,
8. perturbed 3D persistence.

No single item is promoted beyond what it establishes.

## Next creator question

Once the branch diagnostics are verified, the next step is to refine the
continuation around the energetic threshold and any future turning points, then
compare those branch locations against direct perturbative survival.

That will begin turning one persistent candidate into a numerical stability
diagram.
