# Recursive connector port-to-body correspondence audit

The recursive spatial connector audit established that a parent-aligned attachment frame can
preserve the already validated local connector after physical Seed-axis placement. That result
does not yet make the attachment physical because the connector's two-component port remains an
abstract reduced coordinate.

This checkpoint searches the existing 22-body source geometry for a material point whose motion
can represent that abstract port without state-dependent fitting.

## Candidate points

Every named source point emitted by the constitutive geometry is tested:

- every panel vertex;
- every bridge endpoint;
- every hub marker.

Body labels are retained even when geometric points coincide, because an eventual mechanical
attachment needs a body identity as well as a coordinate.

## Fixed transform search

For one candidate point x(q), the audit asks whether a single fixed 2x3 matrix A can satisfy

p(q) = A [x(q) - x(Q0)]

and

Jp(q) = A Jx(q)

over the full admitted state region, where p and Jp are the existing abstract mapped-port
displacement and Jacobian.

The transform is fitted once on an interior training grid using both displacement and Jacobian
constraints. It is then validated on a separate state grid and at module lengths 0.1, 0.05,
0.025 and 0.0125 m.

No state-dependent transform is allowed.

## Three correspondence strengths

The report distinguishes:

1. exact fixed linear correspondence;
2. exact scaled-orthogonal correspondence, where A A^T is proportional to the identity and the
   transform is therefore a uniform scale plus an orthogonal projection/rotation;
3. exact unit orthogonal projection, the strongest literal geometric interpretation.

An exact anisotropic linear transform is useful as a reduced-coordinate correspondence but is
not counted as a literal physical projection.

If no exact fixed linear point exists, the lowest residual candidates are retained instead of
silently adding more fitting freedom.

## Interpretation

A literal material attachment candidate should ideally survive both the displacement and
Jacobian checks with a fixed scaled-orthogonal projection.

An exact anisotropic transform would show that the abstract port can be reconstructed from a
material point, but only after coordinate rescaling. That would support a reduced-coordinate
interpretation, not by itself a physical connector attachment.

If no existing source point passes even the fixed linear test, the current abstract port remains
an independent reduced coordinate and a new attachment geometry would need separate mechanical
justification.
