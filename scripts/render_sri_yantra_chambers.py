"""Render the computed chamber complex: python -m scripts.render_sri_yantra_chambers."""

from pathlib import Path

from src.sri_yantra_chambers import extract_chambers


def render() -> str:
    geometry = extract_chambers()
    colors = ("#69d5d1", "#6cacf0", "#b295eb", "#ef9bc5", "#ffdc86")
    rings = geometry.rings
    chamber_colors = {i: colors[k] for k, ring in enumerate(rings) for i in ring}

    def point(index):
        x, y = geometry.vertices[index]
        # Undo Chiodo's quarter-turn for the conventional upright drawing.
        return f"{365 + 560 * y:.6f},{160 + 560 * x:.6f}"

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="840" viewBox="0 0 1120 840" role="img" aria-labelledby="title desc">',
        '<title id="title">Sri Yantra: 43 chambers recovered from geometry</title>',
        '<desc id="desc">Computed Huet reference geometry. Five colors identify circuits of 14, 10, 10, 8 and 1 triangular chambers. Dark gaps remain unselected.</desc>',
        '<rect width="1120" height="840" fill="#0b182b"/>',
        '<g font-family="DejaVu Sans, sans-serif">',
        '<text x="50" y="62" fill="#f3f7ff" font-size="28" font-weight="bold">Sri Yantra: chambers derived from geometry</text>',
        '<text x="50" y="96" fill="#bdcbe0" font-size="16">Huet reference parameters • finite edges • numerical incidence</text>',
        '<circle cx="365" cy="440" r="280" fill="none" stroke="#465875" stroke-width="1"/>',
    ]
    for i, face in enumerate(geometry.faces):
        polygon = " ".join(point(v) for v in face.corners)
        color = chamber_colors.get(i, "#16263d")
        parts.append(f'<polygon points="{polygon}" fill="{color}"/>')
    for a, b in geometry.edges:
        parts.append(
            f'<polyline points="{point(a)} {point(b)}" fill="none" stroke="#b7c9df" stroke-width="0.9"/>'
        )
    parts.append(
        '<text x="728" y="186" fill="#f3f7ff" font-size="21" font-weight="bold">Outer to inner</text>'
    )
    for k, ring in enumerate(rings):
        y = 228 + 48 * k
        depth = geometry.faces[ring[0]].depth
        parts.extend(
            [
                f'<rect x="730" y="{y - 16}" width="18" height="18" rx="4" fill="{colors[k]}"/>',
                f'<text x="765" y="{y}" fill="#e9f1ff" font-size="18">{len(ring)} chambers</text>',
                f'<text x="928" y="{y}" fill="#bdcbe0" font-size="14">depth {depth}</text>',
            ]
        )
    total = len(geometry.chamber_ids)
    parts.extend(
        [
            f'<text x="730" y="498" fill="#ffdc86" font-size="26" font-weight="bold">{total} selected triangles</text>',
            f'<text x="730" y="539" fill="#bdcbe0" font-size="16">{len(geometry.faces)} bounded regions in total</text>',
            f'<text x="730" y="569" fill="#bdcbe0" font-size="16">{len(geometry.faces) - total} intervening gaps</text>',
            '<text x="730" y="614" fill="#bdcbe0" font-size="15">Chambers meet at vertices.</text>',
            '<text x="730" y="642" fill="#bdcbe0" font-size="15">They do not tile the whole figure.</text>',
            '<text x="50" y="776" fill="#bdcbe0" font-size="14">Selection: odd generator coverage. Ring depth: minimum edge crossings from the exterior.</text>',
            '<text x="50" y="804" fill="#859bb8" font-size="13">Numerically verified for this planar reference. Historical spherical and Meru incidence maps remain open.</text>',
            "</g></svg>",
        ]
    )
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    destination = Path(__file__).resolve().parents[1] / "docs/assets/sri_yantra_chambers.svg"
    destination.write_text(render(), encoding="utf-8")
    print(destination)
