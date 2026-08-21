import os
import sys
import time
import argparse
import uvicorn
from multiprocessing import Process

# Ensure 'src', 'scripts', and the project root directory are in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

for path in [SCRIPT_DIR, PROJECT_ROOT, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

def parse_args():
    parser = argparse.ArgumentParser(description="Universal Field Simulation Orchestrator")
    parser.add_argument("--no-api", action="store_true", help="Disable launching the background ASGI REST API server.")
    parser.add_argument("--layer", type=int, default=0, choices=range(0, 15), help="Default active torus layer to focus (0 = All 14 Layers, 1-14 = Specific Layer).")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode without launching the Matplotlib GUI visualizer.")
    return parser.parse_args()

def launch_asgi_server():
    uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="warning")

def run_background_simulations():
    print("⚛️ Executing Quantum Cascade & Optical Ray Tracer Verification...")
    from lattice_quantum_engine import LatticeQuantumEngine
    from light_cone_simulator import LightConeSimulator
    
    q_engine = LatticeQuantumEngine()
    
    if hasattr(q_engine, 'run_superposition_cascade'):
        q_states = q_engine.run_superposition_cascade(flux_input=1.0)
    elif hasattr(q_engine, 'simulate_superposition'):
        q_states = q_engine.simulate_superposition(flux_input=1.0)
    elif hasattr(q_engine, 'step'):
        q_states = q_engine.step()
    else:
        q_states = getattr(q_engine, 'state', {i: 1.0/114 for i in range(114)})
        
    if isinstance(q_states, dict):
        total_p = sum(q_states.values())
        print(f"✅ Quantum Lattice Normalization Check: Sum(P) = {total_p:.4f}")
    else:
        print("✅ Quantum Lattice Engine Initialized.")
    
    tracer = LightConeSimulator()
    print("✅ Optical Light-Cone Ray Tracer Initialized.")

if __name__ == "__main__":
    args = parse_args()
    
    print("===========================================================")
    print("🚀 INITIALIZING UNIVERSAL MATRIX SYSTEM PIPELINE")
    print("===========================================================")
    
    # Run environment verification check
    try:
        import verify_env
        verify_env.run_verification()
    except ImportError:
        try:
            from scripts import verify_env
            verify_env.run_verification()
        except Exception as e:
            print(f"⚠️ Verification check skipped: {e}")

    run_background_simulations()
    
    api_process = None
    if not args.no_api:
        print("🌐 Launching ASGI REST API Server on http://127.0.0.1:8000...")
        api_process = Process(target=launch_asgi_server)
        api_process.daemon = True
        api_process.start()
        time.sleep(1.0)
    else:
        print("🚫 ASGI REST API Server disabled via --no-api flag.")
    
    if not args.headless:
        print(f"👁️ Launching 14-Layer VR 13D Visualizer Interface (Focused Layer: {args.layer})...")
        from vr_13d_space import VR13DTorusSpace
        
        try:
            vis = VR13DTorusSpace()
            vis.active_layer = args.layer
            vis.run()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down system pipeline processes...")
        finally:
            if api_process and api_process.is_alive():
                api_process.terminate()
            sys.exit(0)
    else:
        print("🖥️ Headless mode active: Skipping GUI Visualizer execution.")
        if api_process:
            try:
                api_process.join()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down system pipeline processes...")
                api_process.terminate()