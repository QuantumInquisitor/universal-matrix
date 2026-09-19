import os
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MicroMacroVREngine")


class MicroMacroVRLabBuilder:
    """
    Builds a Scale-Invariant WebXR Exploration Engine traversing from
    sub-nuclear quantum fields (10^-18 m) to cosmic constellations (10^21 m).
    """

    def __init__(self, output_path: str = "src/vis/micro_macro_vr.html"):
        self.output_path = output_path

    def build(self) -> str:
        logger.info(f"Generating Micro-to-Macro WebXR Engine -> {self.output_path}")

        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SO(13) Matrix - Micro to Macro Scale-Invariant VR</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #020305;
            font-family: 'Segoe UI', Roboto, monospace;
            color: #00f3ff;
        }
        #hud {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(2, 5, 12, 0.9);
            padding: 18px 25px;
            border: 1px solid #00f3ff;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
            pointer-events: none;
            z-index: 100;
        }
        h2 { margin: 0 0 6px 0; font-size: 18px; color: #ffffff; text-transform: uppercase; letter-spacing: 1.5px; }
        .hud-line { font-size: 13px; margin: 4px 0; color: #a0f0f5; }
        .highlight { color: #ffffff; font-weight: bold; }
        .scale-val { color: #ff0055; font-weight: bold; }
        #slider-container {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            background: rgba(2, 5, 12, 0.85);
            padding: 15px 25px;
            border: 1px solid #00f3ff;
            border-radius: 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 100;
        }
        input[type=range] {
            width: 80%;
            cursor: pointer;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/webxr/VRButton.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="hud">
        <h2>Scale-Invariant VR Explorer</h2>
        <div class="hud-line">Current Tier: <span id="tier-name" class="highlight">Sub-Nuclear Field</span></div>
        <div class="hud-line">Log Scale: <span id="scale-exp" class="scale-val">10^-18 meters</span></div>
        <div class="hud-line">Active Dynamics: <span id="dynamics-info" class="highlight">Quarks & Gluon Lattices</span></div>
    </div>

    <div id="slider-container">
        <span style="font-size: 12px; color: #00f3ff;">10^-18m</span>
        <input type="range" id="scaleSlider" min="-18" max="21" value="-18" step="0.1">
        <span style="font-size: 12px; color: #00f3ff;">10^21m</span>
    </div>

    <script>
        let camera, scene, renderer;
        let activeScaleGroup;
        const tiers = [
            { exp: -18, name: "Sub-Nuclear", info: "Quarks, Gluon Field & Color Charge" },
            { exp: -15, name: "Nuclear & Atomic", info: "Protons, Neutrons & Electron Orbitals" },
            { exp: -10, name: "Atomic & Molecular", info: "Covalent Bonds & Frequency Fields" },
            { exp: -8,  name: "DNA & Molecular", info: "Double Helix & Nucleotide Sequences" },
            { exp: -5,  name: "Cellular & Organelle", info: "Cell Membranes & Mitochondria" },
            { exp: -2,  name: "Organs & Body", info: "Vascular System & Neural Networks" },
            { exp: 3,   name: "Planetary Earth", info: "Atmospheric Layers & Core Dynamics" },
            { exp: 12,  name: "Solar System", info: "Heliosphere & Planetary Orbits" },
            { exp: 21,  name: "Constellations & Galaxy", info: "Stellar Clusters & Cosmic Lattice" }
        ];

        init();
        animate();

        function init() {
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x020305, 0.03);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 2, 5);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0x00f3ff, 1.5);
            dirLight.position.set(5, 10, 7);
            scene.add(dirLight);

            activeScaleGroup = new THREE.Group();
            scene.add(activeScaleGroup);

            buildLayerForScale(-18);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.xr.enabled = true;
            document.body.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.target.set(0, 0, 0);
            controls.update();

            document.body.appendChild(VRButton.createButton(renderer));

            document.getElementById('scaleSlider').addEventListener('input', (e) => {
                const val = parseFloat(e.target.value);
                updateScale(val);
            });

            window.addEventListener('resize', onWindowResize);
        }

        function updateScale(expVal) {
            document.getElementById('scale-exp').innerText = `10^${expVal.toFixed(1)} meters`;
            
            // Find closest tier
            let closestTier = tiers[0];
            let minDiff = Math.abs(expVal - tiers[0].exp);
            for (let i = 1; i < tiers.length; i++) {
                const diff = Math.abs(expVal - tiers[i].exp);
                if (diff < minDiff) {
                    minDiff = diff;
                    closestTier = tiers[i];
                }
            }

            document.getElementById('tier-name').innerText = closestTier.name;
            document.getElementById('dynamics-info').innerText = closestTier.info;

            buildLayerForScale(expVal);
        }

        function buildLayerForScale(expVal) {
            // Clear current objects
            while (activeScaleGroup.children.length > 0) {
                const obj = activeScaleGroup.children[0];
                activeScaleGroup.remove(obj);
            }

            if (expVal < -12) {
                // Sub-Nuclear: Quarks & Lattice
                const geo = new THREE.SphereGeometry(0.3, 16, 16);
                const mat1 = new THREE.MeshStandardMaterial({ color: 0xff0055, wireframe: true });
                const mat2 = new THREE.MeshStandardMaterial({ color: 0x00f3ff, wireframe: true });
                const mat3 = new THREE.MeshStandardMaterial({ color: 0xffff00, wireframe: true });

                const q1 = new THREE.Mesh(geo, mat1); q1.position.set(-0.6, 0, 0);
                const q2 = new THREE.Mesh(geo, mat2); q2.position.set(0.6, 0, 0);
                const q3 = new THREE.Mesh(geo, mat3); q3.position.set(0, 0.8, 0);

                activeScaleGroup.add(q1, q2, q3);
            } else if (expVal < -6) {
                // DNA Double Helix
                const group = new THREE.Group();
                for (let i = -20; i < 20; i++) {
                    const t = i * 0.2;
                    const x1 = Math.sin(t) * 1.0;
                    const z1 = Math.cos(t) * 1.0;
                    const x2 = Math.sin(t + Math.PI) * 1.0;
                    const z2 = Math.cos(t + Math.PI) * 1.0;

                    const g1 = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), new THREE.MeshBasicMaterial({ color: 0x00f3ff }));
                    g1.position.set(x1, t * 0.3, z1);
                    const g2 = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff0055 }));
                    g2.position.set(x2, t * 0.3, z2);

                    group.add(g1, g2);
                }
                activeScaleGroup.add(group);
            } else if (expVal < 2) {
                // Cellular / Organ Topology
                const geo = new THREE.IcosahedronGeometry(1.2, 3);
                const mat = new THREE.MeshStandardMaterial({ color: 0x00f3ff, wireframe: true, transparent: true, opacity: 0.7 });
                const cell = new THREE.Mesh(geo, mat);
                activeScaleGroup.add(cell);
            } else {
                // Stellar Constellations & Galaxy Mesh
                const particles = 2000;
                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(particles * 3);

                for (let i = 0; i < particles * 3; i += 3) {
                    positions[i] = (Math.random() - 0.5) * 20;
                    positions[i + 1] = (Math.random() - 0.5) * 20;
                    positions[i + 2] = (Math.random() - 0.5) * 20;
                }

                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                const material = new THREE.PointsMaterial({ color: 0xffffff, size: 0.05 });
                const starField = new THREE.Points(geometry, material);
                activeScaleGroup.add(starField);
            }
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            renderer.setAnimationLoop(render);
        }

        function render() {
            if (activeScaleGroup) {
                activeScaleGroup.rotation.y += 0.005;
            }
            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Scale-Invariant VR Engine created at: {os.path.abspath(self.output_path)}")
        return self.output_path


def main():
    parser = argparse.ArgumentParser(description="Micro-to-Macro Scale-Invariant WebXR Engine")
    parser.add_argument("--output-path", type=str, default="src/vis/micro_macro_vr.html", help="Path for generated HTML file")
    args = parser.parse_args()

    builder = MicroMacroVRLabBuilder(output_path=args.output_path)
    builder.build()


if __name__ == "__main__":
    main()
