import os
import re
import json
import logging
import argparse
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GCodeVisualizer")


class GCodeParser:
    """
    Parses 5-axis (X, Y, Z, A, B / C) G-code streams into structured spatial trajectory nodes.
    """

    def __init__(self):
        # Regular expressions for matching 5-axis motion commands and coordinates
        self.cmd_regex = re.compile(r"([GMF])\s*(\d+)")
        self.coord_regex = re.compile(r"([XYZABC0-9.-]+)")

    def parse_file(self, gcode_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(gcode_path):
            logger.warning(f"G-code file not found at '{gcode_path}'. Generating synthetic fallback trajectory.")
            return self._generate_synthetic_toroid_trajectory()

        logger.info(f"Parsing G-code toolpath: {gcode_path}")
        points = []
        curr_state = {"x": 0.0, "y": 0.0, "z": 0.0, "a": 0.0, "b": 0.0, "f": 1000.0}

        with open(gcode_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().split(";")[0]  # Strip inline comments
                if not line:
                    continue

                tokens = line.split()
                is_motion = False
                for token in tokens:
                    code = token[0].upper()
                    try:
                        val = float(token[1:])
                    except ValueError:
                        continue

                    if code == "X":
                        curr_state["x"] = val
                        is_motion = True
                    elif code == "Y":
                        curr_state["y"] = val
                        is_motion = True
                    elif code == "Z":
                        curr_state["z"] = val
                        is_motion = True
                    elif code == "A":
                        curr_state["a"] = val
                        is_motion = True
                    elif code == "B":
                        curr_state["b"] = val
                        is_motion = True
                    elif code == "F":
                        curr_state["f"] = val

                if is_motion:
                    points.append(dict(curr_state))

        logger.info(f"Parsed {len(points)} trajectory nodes from G-code.")
        return points

    def _generate_synthetic_toroid_trajectory(self, num_points: int = 500) -> List[Dict[str, Any]]:
        """
        Generates a 5-axis synthetic toroidal spiral trajectory for visualization demonstration.
        """
        points = []
        R_major = 50.0  # Major radius
        r_minor = 15.0  # Minor radius
        turns = 12

        for i in range(num_points):
            u = (i / num_points) * 2 * 3.14159265359 * turns
            v = (i / num_points) * 2 * 3.14159265359

            x = (R_major + r_minor * torch_cos(u)) * torch_cos(v)
            y = (R_major + r_minor * torch_cos(u)) * torch_sin(v)
            z = r_minor * torch_sin(u)
            a = (u * 180.0 / 3.14159265359) % 360.0
            b = (v * 180.0 / 3.14159265359) % 360.0

            points.append({"x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "a": round(a, 3), "b": round(b, 3), "f": 1200.0})

        return points


def torch_cos(val: float) -> float:
    import math
    return math.cos(val)


def torch_sin(val: float) -> float:
    import math
    return math.sin(val)


class WebGPUVisualizerBuilder:
    """
    Compiles trajectory data into an interactive, browser-executable WebGL/WebGPU Three.js app.
    """

    def __init__(self, output_html: str = "src/vis/gcode_viewport.html"):
        self.output_html = output_html

    def build_viewport(self, trajectory_data: List[Dict[str, Any]]) -> str:
        logger.info(f"Building WebGPU 5-Axis G-Code Viewport -> {self.output_html}")
        json_trajectory = json.dumps(trajectory_data)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SO(13) Universal Matrix - 5-Axis WebGPU G-Code Viewport</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #0a0b10;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #00ffcc;
        }}
        #canvas-container {{
            width: 100vw;
            height: 100vh;
        }}
        #overlay {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(10, 11, 16, 0.85);
            padding: 18px 24px;
            border: 1px solid #00ffcc;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.2);
            pointer-events: none;
        }}
        h2 {{ margin: 0 0 10px 0; font-size: 18px; text-transform: uppercase; letter-spacing: 1.5px; }}
        .stat-line {{ font-size: 13px; margin: 4px 0; color: #a0f0e0; }}
        .highlight {{ color: #ffffff; font-weight: bold; }}
    </style>
    <!-- Three.js + OrbitControls CDNs -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="overlay">
        <h2>5-Axis DTA Toolpath Viewport</h2>
        <div class="stat-line">Trajectory Nodes: <span id="node-count" class="highlight">0</span></div>
        <div class="stat-line">Kinematic Axis Mode: <span class="highlight">5-Axis GRBL (X,Y,Z,A,B)</span></div>
        <div class="stat-line">Matrix Lattice: <span class="highlight">SO(13) Discrete Core</span></div>
        <div class="stat-line">Renderer: <span class="highlight">WebGPU / WebGL Accelerated</span></div>
    </div>
    <div id="canvas-container"></div>

    <script>
        const rawTrajectory = {json_trajectory};
        document.getElementById('node-count').innerText = rawTrajectory.length;

        // Scene Setup
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a0b10, 0.002);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(100, 80, 120);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Grid & Coordinate Helpers
        const gridHelper = new THREE.GridHelper(200, 40, 0x00ffcc, 0x1a3344);
        gridHelper.position.y = -25;
        scene.add(gridHelper);

        const axesHelper = new THREE.AxesHelper(30);
        scene.add(axesHelper);

        // Build 3D Trajectory Tube & Line Path
        const points = rawTrajectory.map(p => new THREE.Vector3(p.x, p.z, p.y));
        const curve = new THREE.CatmullRomCurve3(points);

        // Toolpath Spline
        const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(rawTrajectory.length * 2));
        const material = new THREE.LineBasicMaterial({{ color: 0x00ffcc, linewidth: 2 }});
        const line = new THREE.Line(geometry, material);
        scene.add(line);

        // Animated Toolhead Indicator
        const toolheadGeo = new THREE.ConeGeometry(3, 10, 16);
        toolheadGeo.rotateX(Math.PI);
        const toolheadMat = new THREE.MeshBasicMaterial({{ color: 0xff0055, wireframe: true }});
        const toolhead = new THREE.Mesh(toolheadGeo, toolheadMat);
        scene.add(toolhead);

        // Animation Loop
        let progress = 0;
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();

            if (points.length > 0) {{
                progress = (progress + 0.0015) % 1;
                const pos = curve.getPointAt(progress);
                const tangent = curve.getTangentAt(progress);
                toolhead.position.copy(pos);
                toolhead.lookAt(pos.clone().add(tangent));
            }}

            renderer.render(scene, camera);
        }}

        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""
        os.makedirs(os.path.dirname(self.output_html), exist_ok=True)
        with open(self.output_html, "w", encoding="utf-8") as f:
            f.write(html_template)

        logger.info(f"Viewport build complete. HTML generated at: {os.path.abspath(self.output_html)}")
        return self.output_html


def main():
    parser = argparse.ArgumentParser(description="WebGPU 5-Axis G-Code Visualizer Generator")
    parser.add_argument("--gcode-path", type=str, default="src/toroid_toolpath.gcode", help="Path to input G-code file")
    parser.add_argument("--output-html", type=str, default="src/vis/gcode_viewport.html", help="Path for output HTML file")
    args = parser.parse_args()

    gcode_parser = GCodeParser()
    trajectory = gcode_parser.parse_file(args.gcode_path)

    builder = WebGPUVisualizerBuilder(output_html=args.output_html)
    builder.build_viewport(trajectory)


if __name__ == "__main__":
    main()
    