# Toroidal fixed bend-interface obstruction v0.1

Status: bounded geometric obstruction for the current separated-shell route.
This note supplements the inversion control and does not change routing,
currents, junction ports, or the mod-9 construction.

## Question and result

Can the two known collisions be removed by deforming only the interiors of
their quarter bends, while fixing both bend end faces and the neighboring
straight shells? **No, for the reference gap-3, bend-margin-0.05 geometry.**
Both bends already have an end-face point strictly inside the neighboring
finite straight shell. The points are constructed analytically and verified
against the actual finite segments; this result does not depend on whether a
volume sampling grid happens to detect the nearby overlap.

This rules out an endpoint-preserving local bulge for these pairs. It does
not rule out relative rearrangement of a bend together with its adjacent
straight sections. Bend/straight joins are internal route interfaces, not
the graph's junction ports.

## Witness construction

Let an end-face point at the interior annulus radius be

$$
x(\theta)=C+r(n\cos\theta+b\sin\theta),\qquad
r=(r_{\mathrm{inner}}+r_{\mathrm{outer}})/2.
$$

Here $n$ and $b$ span the face and its tangent $t$ is perpendicular to it.
The supported configuration has a neighboring straight axis parallel to
$n$, with no offset in the $b$ direction. If its separation from $C$ in the
$t$ direction is $d$, the radial distance to that axis is

$$
\rho(\theta)=\sqrt{d^2+r^2\sin^2\theta}.
$$

Intersect the open radial range $(|d|,\sqrt{d^2+r^2})$ with the neighboring
shell's open annulus and select a radial midpoint. Solve for $\sin\theta$,
then check both signs of the axial and binormal components against the
**finite** straight segment. Every reported point must have strictly
positive radial and axial penetration, exceeding the numerical tolerance.

The implementation checks both end faces of every nonzero, same-face,
ordered incident bend/straight pair. It only constructs witnesses on this
mid-annulus circle and in the supported alignment. An absent witness means
unclassified, not clear. Slight floating-point alignment tolerances cannot
produce an accepted witness without passing the final finite-shell check.

## Reference result

Command: `python -m src.toroidal_fixed_interface_obstruction`.

Parameters: vesica current 1, return split 0.4, shell gap 3,
bend margin 0.05, node gap 1, edge gap 0.5. Eight interface/pair
combinations are examined and two strict witnesses are found.

| Node / face | Bend / straight edge | Bend coordinate | Neighbor penetration |
| --- | --- | --- | --- |
| cusp_a / lower | 2 / 3 | $\phi=0$, $q=0.5$, $\theta\approx1.16193800157$ | 0.2 |
| cusp_b / upper | 2 / 3 | $\phi=\pi/2$, $q=0.5$, $\theta\approx1.16193800157$ | 0.2 |

The witness points are approximately
`(-62.920455425269, 9.25, -175.671941867437)` and
`(46.404099895068, 9.25, 175.671941867437)`. Here $r=9$, $d=9.25$,
and the neighboring annulus is $(12.2,12.6)$, so $\rho=12.4$.
Their axial coordinates are well inside the finite neighboring segments.
Nearby points strictly inside each original bend also penetrate the shell.

## Consequence for continuous deformations

Suppose $F_s$ is a continuous bend deformation that fixes its end face,
and the neighboring straight volume $S$ stays fixed. A face witness $x$
satisfies $F_s(x)=x\in\operatorname{interior}(S)$ for every $s$.
Thus an intersection persists at every stage. Continuity gives nearby
interior bend parameters whose images also lie inside $S$; a regular
embedding makes this a volume overlap, not merely surface contact.

The reported penetration is the minimum of the two axial and two radial
margins. Each margin is 1-Lipschitz in Cartesian position. Consequently,
with the neighbor fixed, displacing a witness by less than 0.2 cannot
remove it from the neighboring shell. This is a necessary displacement
bound for these particular points, not a sufficient routing repair.

The starting reference geometry already collides, so it cannot serve as
the start of a collision-free motion that includes its initial state.

## Next bounded design and limits

Allow the internal bend joins and adjacent straight sections to move while
keeping graph junction ports connected. Recheck all changed volumes and
intermediate states, positive Jacobians, and flux/interface matching.
The original route-envelope certificates cannot simply be reused for
displaced geometry. No new deformation or global clearance claim is made
here, and no existing routing or field implementation is replaced.

Verification covers direct geometric membership, finite axial clipping,
reversed segment orientation, rigid transformations, scaling, signed
current independence, contact rejection, unsupported configurations, and
the two actual reference witnesses. The existing toroidal tests remain
the regression checks for routing and flux.
