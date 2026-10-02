# Breathing coupled to the relative-fold control

The specimen now expands and contracts while performing the existing relative fold. This is a prescribed kinematic control, not a derived oscillator or physical breathing mechanism.

The live repository's Q-ball analysis must remain separate: its t=2.5 trace was bounded, but retained intervals 1.375 and 0.675 did not support a consistent breathing period. No frequency or amplitude is imported from those data. See qball_peak_period_classification_v0.1.md.

## Explicit inputs

For cycle phase p in [0,1], use s(p)=1+epsilon*sin(2*pi*p), with default epsilon=0.1. The amplitude must satisfy 0<=epsilon<1. Phase is dimensionless and has no assigned duration. Coupling this breathing cycle and the fold to the same phase is an explicit test choice, not an established natural phase relation.

Every panel point becomes s(p) times its computed folding position. Collar geometry and thickness also scale: total core thickness is 0.02*s. The cycle starts and ends at the same geometry and breathing rate. The fold returns to its reference shape; the largest size is 1.1 and the smallest is 0.9.

## Panel content conservation

Let A_fold be the affine panel area ratio relative to its reference. The combined area ratio is s^2*A_fold. An initially uniform material surface density transforms by its reciprocal. Independent polygon area integration in both 3D and 4D verifies that integrated panel content is constant. This assumes no exchange across material edges. It supplies no constitutive stress law or inter-panel current.

## Separate moving-volume control

For uniform 3D similarity expansion only, density transforms as rho=rho0/s^3, a relative current as J_rel=J0/s^2, and the material velocity is w=(s'/s)*x. The laboratory current must include advection:

`J_lab = rho*w + J_rel`.

For uniform reference density and constant reference current, independent finite differences verify `d(rho)/dp + div(J_lab)=0`. The current relative to a moving material face has the original integrated flux because area scales as s^2. Omitting advection fails continuity during changing size. This does not solve the full volume current for the nonuniform panel fold or implement a four-dimensional physical flow.

## Continuous core clearance

All distances and offset radii scale by the same positive s at each phase. Therefore each prior continuous core-clearance bound b becomes at least (1-epsilon)*b. The minimum reference cycle scale is 0.9, yielding lower bounds approximately 0.00449582 in 3D and 0.00530299 in 4D. The inherited bounds are floating-point analytic inequalities, not interval arithmetic.

The excluded hinge collars remain excluded. Breathing does not repair or certify joints, nor does it remove existing intersections. Independent breathing amplitudes at different recursive levels would require new interface and clearance checks; they are not implemented here.

## Outputs and remaining work

The exporter provides 101 combined geometry states in each reference dimension and a 3D diagnostic figure. It labels the unmodeled hinge regions. The surface density, similarity-volume density, and relative-current scalings retain their different scopes.

A connected hinge model, complete moving-volume field, energy/work balance, material response, and a derived or measured breathing evolution law remain open. The geometric control should not be promoted to an autonomous living-fractal result.
