# Continuous lifted mirror control

This optional experiment starts from the existing stella-octangula central mirror. It neither replaces the recovered Lynchpin hinges nor identifies that mirror with spherical inversion or the reciprocal scale-address map.

For phase p from 0 to 2, set a=pi*p and use

`F_p(x,y,z) = (x*cos(a)-y*sin(a), x*sin(a)+y*cos(a), z*cos(a), z*sin(a))`.

Phase 0 is the original geometry; phase 1 has XYZ=(-x,-y,-z) and W=0; phase 2 returns to the original. Extra coordinates through dimension 13 are zero padding, not additional dynamics. The embedded object has intrinsic dimension three.

The rectangular derivative A satisfies A-transpose A=I for every phase. Thus all distances, angles, intrinsic volumes, and shared-point incidences are preserved throughout the continuous path, not merely at sampled frames. A transported current and area-dual pairing in the intrinsic tangent chart retains its dot product. This statement is not a physical four-dimensional flux law or an equation of motion.

The XYZ projection has determinant cos(a). At phases 0.5 and 1.5 it has rank two, while the full derivative still has rank three. Points separated in W can coincide in the projected view. A viewer must disclose the omitted coordinate and distinguish projected overlap from an actual intersection in the represented space.

Tests check every existing 64-register mirror endpoint, all pair distances among eight stella vertices, the derivative by finite differences, continuity across landmarks, intrinsic pairing, and rejected invalid inputs. The analytic isometry supplies the continuous-path argument; the exported 65-frame trajectory is a display diagnostic only.

## Limits and next experiment

This is a global rotation in four dimensions. It preserves any existing intersections and performs no relative hinge folding, opening, scale transition, or self-driven evolution. It supplies one continuous endpoint bridge with explicit projection diagnostics. It does not complete the living fractal engine or prove a physical extra dimension.

The next distinct experiment must actuate connected panels or recursive components relative to one another using the already recovered hinge/port incidence. It must specify the metric geometry and admissible contact, then check thickness, ports, conservation, and intermediate clearance. The existing exact-108-degree 4D and deformed-109.471-degree 3D Lynchpin alternatives must remain explicit.

Run the focused tests in tests/test_recursive_mirror_motion_control.py. Export a trajectory with `python scripts/report_recursive_mirror_motion.py <output.json>`.
