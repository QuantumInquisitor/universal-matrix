"""Exact zero-thickness recursive body clearance on the bounded fold-state grid."""

import argparse
import hashlib
import json
import math
from itertools import combinations, product
from pathlib import Path

import numpy as np

try:
    from .report_fold_constitutive import geometry
    from .report_fold_recursive_material_placement import (
        BASE_MODULE_LENGTH_M,
        Q_GRID,
        RECIPROCAL_RING_PAIRS,
        candidate_nodes,
        footprint_requirements,
        pair_clearance_requirement,
        rotation,
    )
except ImportError:
    from report_fold_constitutive import geometry
    from report_fold_recursive_material_placement import (
        BASE_MODULE_LENGTH_M,
        Q_GRID,
        RECIPROCAL_RING_PAIRS,
        candidate_nodes,
        footprint_requirements,
        pair_clearance_requirement,
        rotation,
    )


EPS = 1e-14
COLLISION_TOLERANCE_M = BASE_MODULE_LENGTH_M * 1e-10
COARSE_MULTIPLIERS = (1.0, 1.5, 2.0, 3.0, 5.0)


def clamp01(value):
    return min(1.0, max(0.0, float(value)))


def point_segment_distance(point, a, b):
    point, a, b = (np.asarray(value, dtype=float) for value in (point, a, b))
    direction = b - a
    denominator = float(direction @ direction)
    if denominator <= EPS:
        return float(np.linalg.norm(point - a))
    t = clamp01((point - a) @ direction / denominator)
    return float(np.linalg.norm(point - (a + t * direction)))


def segment_segment_distance(p1, q1, p2, q2):
    p1, q1, p2, q2 = (np.asarray(value, dtype=float) for value in (p1, q1, p2, q2))
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a = float(d1 @ d1)
    e = float(d2 @ d2)
    f = float(d2 @ r)

    if a <= EPS and e <= EPS:
        return float(np.linalg.norm(p1 - p2))
    if a <= EPS:
        s, t = 0.0, clamp01(f / e)
    else:
        c = float(d1 @ r)
        if e <= EPS:
            t, s = 0.0, clamp01(-c / a)
        else:
            b = float(d1 @ d2)
            denominator = a * e - b * b
            s = 0.0 if abs(denominator) <= EPS else clamp01((b * f - c * e) / denominator)
            t = (b * s + f) / e
            if t < 0.0:
                t, s = 0.0, clamp01(-c / a)
            elif t > 1.0:
                t, s = 1.0, clamp01((b - c) / a)

    closest1 = p1 + s * d1
    closest2 = p2 + t * d2
    return float(np.linalg.norm(closest1 - closest2))


def point_triangle_distance(point, a, b, c):
    point, a, b, c = (np.asarray(value, dtype=float) for value in (point, a, b, c))
    ab, ac, ap = b - a, c - a, point - a
    normal = np.cross(ab, ac)
    if float(normal @ normal) <= EPS:
        return min(
            point_segment_distance(point, a, b),
            point_segment_distance(point, b, c),
            point_segment_distance(point, c, a),
        )

    d1, d2 = float(ab @ ap), float(ac @ ap)
    if d1 <= 0.0 and d2 <= 0.0:
        return float(np.linalg.norm(ap))

    bp = point - b
    d3, d4 = float(ab @ bp), float(ac @ bp)
    if d3 >= 0.0 and d4 <= d3:
        return float(np.linalg.norm(bp))

    vc = d1 * d4 - d3 * d2
    if vc <= 0.0 and d1 >= 0.0 and d3 <= 0.0:
        v = d1 / (d1 - d3)
        return float(np.linalg.norm(point - (a + v * ab)))

    cp = point - c
    d5, d6 = float(ab @ cp), float(ac @ cp)
    if d6 >= 0.0 and d5 <= d6:
        return float(np.linalg.norm(cp))

    vb = d5 * d2 - d1 * d6
    if vb <= 0.0 and d2 >= 0.0 and d6 <= 0.0:
        w = d2 / (d2 - d6)
        return float(np.linalg.norm(point - (a + w * ac)))

    va = d3 * d6 - d5 * d4
    if va <= 0.0 and (d4 - d3) >= 0.0 and (d5 - d6) >= 0.0:
        direction = c - b
        w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return float(np.linalg.norm(point - (b + w * direction)))

    denominator = 1.0 / (va + vb + vc)
    v, w = vb * denominator, vc * denominator
    projection = a + ab * v + ac * w
    return float(np.linalg.norm(point - projection))


def segment_intersects_triangle(p, q, a, b, c):
    p, q, a, b, c = (np.asarray(value, dtype=float) for value in (p, q, a, b, c))
    direction = q - p
    edge1, edge2 = b - a, c - a
    h = np.cross(direction, edge2)
    determinant = float(edge1 @ h)
    if abs(determinant) <= EPS:
        return False
    inverse = 1.0 / determinant
    s = p - a
    u = inverse * float(s @ h)
    if u < -EPS or u > 1.0 + EPS:
        return False
    qvec = np.cross(s, edge1)
    v = inverse * float(direction @ qvec)
    if v < -EPS or u + v > 1.0 + EPS:
        return False
    t = inverse * float(edge2 @ qvec)
    return -EPS <= t <= 1.0 + EPS


def segment_triangle_distance(p, q, a, b, c):
    if segment_intersects_triangle(p, q, a, b, c):
        return 0.0
    return min(
        point_triangle_distance(p, a, b, c),
        point_triangle_distance(q, a, b, c),
        segment_segment_distance(p, q, a, b),
        segment_segment_distance(p, q, b, c),
        segment_segment_distance(p, q, c, a),
    )


def triangle_triangle_distance(a0, a1, a2, b0, b1, b2):
    edges_a = ((a0, a1), (a1, a2), (a2, a0))
    edges_b = ((b0, b1), (b1, b2), (b2, b0))
    values = [segment_triangle_distance(p, q, b0, b1, b2) for p, q in edges_a]
    values.extend(segment_triangle_distance(p, q, a0, a1, a2) for p, q in edges_b)
    return min(values)


def triangulate(vertices):
    vertices = np.asarray(vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 3:
        raise ValueError("panel vertices must be an Nx3 array with N >= 3")
    return tuple(
        (vertices[0], vertices[index], vertices[index + 1]) for index in range(1, len(vertices) - 1)
    )


def body_kind(body_id):
    if body_id.startswith("panel-"):
        return "panel"
    if body_id.startswith("bridge-"):
        return "bridge"
    if body_id.startswith("hub-"):
        return "hub"
    raise ValueError("unknown body kind")


def body_distance(body_a, body_b):
    kind_a, vertices_a = body_a["kind"], body_a["vertices"]
    kind_b, vertices_b = body_b["kind"], body_b["vertices"]

    if kind_a == "hub" and kind_b == "hub":
        return float(np.linalg.norm(vertices_a[0] - vertices_b[0]))

    if kind_a == "hub" and kind_b == "bridge":
        return point_segment_distance(vertices_a[0], vertices_b[0], vertices_b[1])
    if kind_b == "hub" and kind_a == "bridge":
        return point_segment_distance(vertices_b[0], vertices_a[0], vertices_a[1])

    if kind_a == "hub" and kind_b == "panel":
        return min(
            point_triangle_distance(vertices_a[0], *triangle)
            for triangle in triangulate(vertices_b)
        )
    if kind_b == "hub" and kind_a == "panel":
        return min(
            point_triangle_distance(vertices_b[0], *triangle)
            for triangle in triangulate(vertices_a)
        )

    if kind_a == "bridge" and kind_b == "bridge":
        return segment_segment_distance(
            vertices_a[0],
            vertices_a[1],
            vertices_b[0],
            vertices_b[1],
        )

    if kind_a == "bridge" and kind_b == "panel":
        return min(
            segment_triangle_distance(vertices_a[0], vertices_a[1], *triangle)
            for triangle in triangulate(vertices_b)
        )
    if kind_b == "bridge" and kind_a == "panel":
        return min(
            segment_triangle_distance(vertices_b[0], vertices_b[1], *triangle)
            for triangle in triangulate(vertices_a)
        )

    if kind_a == "panel" and kind_b == "panel":
        return min(
            triangle_triangle_distance(*triangle_a, *triangle_b)
            for triangle_a in triangulate(vertices_a)
            for triangle_b in triangulate(vertices_b)
        )

    raise RuntimeError("unhandled body-kind combination")


def aabb_distance(minimum_a, maximum_a, minimum_b, maximum_b):
    separation = np.maximum(
        np.maximum(minimum_b - maximum_a, minimum_a - maximum_b),
        0.0,
    )
    return float(np.linalg.norm(separation))


def path_category(path_a, path_b):
    if len(path_a) < len(path_b) and path_b[: len(path_a)] == path_a:
        return "parent_child" if len(path_b) == len(path_a) + 1 else "ancestor_descendant"
    if len(path_b) < len(path_a) and path_a[: len(path_b)] == path_b:
        return "parent_child" if len(path_a) == len(path_b) + 1 else "ancestor_descendant"
    if len(path_a) == len(path_b) and path_a and path_a[:-1] == path_b[:-1]:
        return "siblings"
    return "cross_branch"


def local_geometry_cache(nodes):
    cache = {}
    for path, node in nodes.items():
        transform = rotation(node["orientation_rad"])
        state_rows = []
        for q_index, q in enumerate(Q_GRID):
            bodies = []
            radius = 0.0
            for row in geometry(q, length_m=BASE_MODULE_LENGTH_M * node["scale"]):
                vertices = np.asarray(row["vertices_m"], dtype=float)
                rotated = vertices.copy()
                rotated[:, :2] = vertices[:, :2] @ transform.T
                radius = max(radius, float(np.max(np.linalg.norm(rotated, axis=1))))
                bodies.append(
                    {
                        "id": row["id"],
                        "kind": body_kind(row["id"]),
                        "vertices": rotated,
                        "aabb_min": np.min(rotated, axis=0),
                        "aabb_max": np.max(rotated, axis=0),
                    }
                )
            state_rows.append(
                {
                    "q_index": q_index,
                    "q": list(q),
                    "bodies": bodies,
                    "radius": radius,
                }
            )
        center_coefficient = np.r_[
            BASE_MODULE_LENGTH_M * node["center_normalized"],
            0.0,
        ]
        cache[path] = {
            "path": path,
            "scale": node["scale"],
            "center_coefficient": center_coefficient,
            "states": state_rows,
        }
    return cache


def module_pair_clearance(module_a, state_a, module_b, state_b, ratio, best_limit):
    center_a = ratio * module_a["center_coefficient"]
    center_b = ratio * module_b["center_coefficient"]
    module_lower = max(
        0.0,
        float(np.linalg.norm(center_a - center_b)) - state_a["radius"] - state_b["radius"],
    )
    search_limit = best_limit if best_limit > COLLISION_TOLERANCE_M else COLLISION_TOLERANCE_M + EPS
    if module_lower >= search_limit:
        return None

    best = search_limit
    detail = None
    for body_a in state_a["bodies"]:
        minimum_a = body_a["aabb_min"] + center_a
        maximum_a = body_a["aabb_max"] + center_a
        vertices_a = body_a["vertices"] + center_a
        translated_a = {**body_a, "vertices": vertices_a}
        for body_b in state_b["bodies"]:
            minimum_b = body_b["aabb_min"] + center_b
            maximum_b = body_b["aabb_max"] + center_b
            lower = aabb_distance(minimum_a, maximum_a, minimum_b, maximum_b)
            if lower >= best:
                continue
            vertices_b = body_b["vertices"] + center_b
            translated_b = {**body_b, "vertices": vertices_b}
            distance = body_distance(translated_a, translated_b)
            if distance < best:
                best = distance
                detail = {
                    "body_a": body_a["id"],
                    "body_b": body_b["id"],
                    "distance_m": distance,
                }
                if best <= COLLISION_TOLERANCE_M:
                    return detail
    return detail


def scan_ratio(cache, ratio):
    paths = sorted(cache, key=lambda path: (len(path), path))
    best = math.inf
    governing = None
    collision_state_pairs = 0
    colliding_module_pairs = set()
    category_pairs = {}
    category_collision_pairs = {}

    for path_a, path_b in combinations(paths, 2):
        category = path_category(path_a, path_b)
        category_pairs[category] = category_pairs.get(category, 0) + 1
        pair_collides = False
        module_a, module_b = cache[path_a], cache[path_b]

        for state_a, state_b in product(module_a["states"], module_b["states"]):
            center_a = ratio * module_a["center_coefficient"]
            center_b = ratio * module_b["center_coefficient"]
            sphere_lower = max(
                0.0,
                float(np.linalg.norm(center_a - center_b)) - state_a["radius"] - state_b["radius"],
            )
            if sphere_lower > COLLISION_TOLERANCE_M and sphere_lower >= best:
                continue
            if sphere_lower > COLLISION_TOLERANCE_M and best <= COLLISION_TOLERANCE_M:
                continue

            detail = module_pair_clearance(
                module_a,
                state_a,
                module_b,
                state_b,
                ratio,
                best,
            )
            if detail is None:
                continue
            distance = detail["distance_m"]
            if distance < best:
                best = distance
                governing = {
                    **detail,
                    "path_a": list(path_a),
                    "path_b": list(path_b),
                    "category": category,
                    "q_a": state_a["q"],
                    "q_b": state_b["q"],
                }
            if distance <= COLLISION_TOLERANCE_M:
                collision_state_pairs += 1
                pair_collides = True

        if pair_collides:
            key = (path_a, path_b)
            colliding_module_pairs.add(key)
            category_collision_pairs[category] = category_collision_pairs.get(category, 0) + 1

    if not math.isfinite(best):
        raise RuntimeError("clearance scan produced no finite body distance")

    return {
        "vessel_radius_per_module_length": ratio,
        "collision_free": collision_state_pairs == 0,
        "minimum_clearance_m": best,
        "minimum_clearance_per_root_module_length": best / BASE_MODULE_LENGTH_M,
        "collision_state_pair_count": collision_state_pairs,
        "colliding_module_pair_count": len(colliding_module_pairs),
        "module_pair_count_by_category": category_pairs,
        "colliding_module_pair_count_by_category": category_collision_pairs,
        "governing_case": governing,
    }


def report():
    footprint = footprint_requirements()
    canonical_pair = RECIPROCAL_RING_PAIRS[0]
    _, nodes = candidate_nodes(canonical_pair)
    cache = local_geometry_cache(nodes)

    local_ratio = footprint["minimum_spherical_bound_per_module_length"]
    conservative_all, conservative_governing = pair_clearance_requirement(
        nodes,
        local_ratio,
    )
    outer_ratio = conservative_all * (1.0 + 1e-6)
    ratios = sorted(
        set(
            [local_ratio * multiplier for multiplier in COARSE_MULTIPLIERS]
            + [conservative_all, outer_ratio]
        )
    )
    rows = [scan_ratio(cache, ratio) for ratio in ratios]
    first_free = next((row for row in rows if row["collision_free"]), None)
    if first_free is None:
        lower_colliding = None
    else:
        lower = [
            row
            for row in rows
            if row["vessel_radius_per_module_length"]
            < first_free["vessel_radius_per_module_length"]
            and not row["collision_free"]
        ]
        lower_colliding = None if not lower else lower[-1]

    return {
        "schema": 1,
        "scope": (
            "exact zero-thickness panel/bridge/hub pairwise proximity on the canonical "
            "Seed-axis recursive placement; finite q-grid and vessel-ratio samples only"
        ),
        "canonical_axis_pair": list(canonical_pair),
        "axis_equivalence_reused_from_prior_audit": True,
        "module_count": len(nodes),
        "module_pair_count": len(nodes) * (len(nodes) - 1) // 2,
        "state_count_per_module": len(Q_GRID),
        "independent_state_pairs_per_module_pair": len(Q_GRID) ** 2,
        "collision_tolerance_m": COLLISION_TOLERANCE_M,
        "zero_thickness_source_geometry": True,
        "local_containment_ratio": local_ratio,
        "conservative_all_module_sphere_ratio": conservative_all,
        "outer_sphere_guard_ratio": outer_ratio,
        "conservative_sphere_governing_pair": conservative_governing,
        "sampled_ratios": ratios,
        "rows": rows,
        "sampled_first_collision_free_ratio": (
            None if first_free is None else first_free["vessel_radius_per_module_length"]
        ),
        "sampled_lower_colliding_ratio": (
            None if lower_colliding is None else lower_colliding["vessel_radius_per_module_length"]
        ),
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_exact_clearance.py",
                "report_fold_recursive_material_placement.py",
                "report_fold_recursive_seed_correspondence.py",
                "report_fold_constitutive.py",
                "report_fold_kinematics.py",
            )
        },
        "continuous_clearance_theorem": False,
        "physical_body_thickness_modeled": False,
        "common_vessel_to_module_ratio_selected": False,
        "connector_attachment_geometry_used": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
