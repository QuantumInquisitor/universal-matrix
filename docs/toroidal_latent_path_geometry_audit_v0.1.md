# Toroidal latent-path geometry audit v0.1

## Purpose

The Flower-derived Tree keeps same-ring weave edges in its declared topology
even when their current is exactly zero. The current separated toroidal
geometry allocates channel shells and annular junction ports to every declared
edge before the incident collision audit filters inactive currents.

This checkpoint measures the geometric effect of those dormant pathways. It
does not decide whether they should be retained or removed.

## Compared representations

For the same Tree circulation with nonzero radial current and zero weave
current, the audit builds:

1. the **full topology**, including zero-current weave edges;
2. the **active-only topology**, containing only nonzero directed currents.

It compares only matching active radial edges.

## Measurements

The audit records:

- full, active, and latent edge counts;
- the number of zero-current annular ports;
- minimum and maximum active-channel center displacement;
- active toroidal major-radius residual;
- minimum active annular-port width ratio;
- maximum active annular-port width difference.

If dormant edges are purely bookkeeping, active geometry would ideally be
unchanged. If dormant pathways are intended to remain as persistent geometry,
a nonzero effect is meaningful and must become an explicit model choice.

## Tree growth

For zero weave current, the current Tree construction has

$$
N_{\rm active}=12r^2
$$

active radial directed edges and

$$
N_{\rm latent}=3r(r+1)
$$

zero-current weave paths at ring depth $r$.

The focused audit evaluates $r=1,2,3$.

## Measured checkpoint

Running `python -m src.toroidal_latent_path_geometry_audit` with the default
geometry gives:

| Ring depth | Active edges | Latent edges | Latent ports | Active center shift | Minimum active port-width ratio |
| --- | --- | --- | --- | --- | --- |
| 1 | 12 | 6 | 12 | -3 | 0.5 |
| 2 | 48 | 18 | 36 | -9 | 0.5 |
| 3 | 108 | 36 | 72 | -18 | 0.5 |

The center shift is uniform across matching active channels at each depth.
Their major-radius residual is zero, while the maximum absolute port-width
difference is 0.5 in the implementation's coordinate units at every tested
depth. Thus the measured latent-path effect is material: at least one active
port is half as wide when dormant paths are retained.

The current Tree ordering appends latent weave edges after active radial edges.
For that ordering, retaining $L$ latent channels changes the common stack
midpoint and gives

$$
\Delta z=-\frac{L}{2}(2w+g_z),
$$

where $w$ is shell width and $g_z$ is axial gap. This is a property of the
current allocation rule, not an order-independent topology theorem. Focused
controls verify current reversal and magnitude changes, nondefault axial
spacing, and independence of this displacement from radial shell gap. The
audit uses an absolute current tolerance of $10^{-12}$; radial currents at or
below that magnitude are rejected rather than treated as active support.

## Evidence boundary

This audit can establish whether latent zero-current pathways alter active
channel placement or active junction-port geometry in the current
implementation.

It does not establish:

- whether persistent latent geometry is physically correct;
- a contraction law for dormant pathways;
- Flower/Tree collision clearance;
- recursive scale invariance;
- a biological or consciousness interpretation.

## Decision gate

If the effect is negligible, topology-scale testing can proceed without a new
latent-path rule.

If the effect is material, the engine must explicitly choose and test one of
three semantics before topology-scale conclusions are trusted:

1. **persistent latent geometry**: dormant pathways keep finite geometry;
2. **active-support geometry**: zero-current pathways are removed;
3. **adaptive geometry**: dormant pathways contract continuously rather than
   switching discontinuously between present and absent.

The third option is the natural candidate for a morphing or living-fractal
geometry, but it requires a separately stated dynamics or interpolation law.
