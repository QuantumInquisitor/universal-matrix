#!/usr/bin/env python3
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: import calculator as mc
except ImportError: sys.exit("CRITICAL: calculator.py missing.")

class FieldSynthesizer:
    def __init__(self):
        self.major_radius, self.minor_radius = 50.0, 15.0
    def calculate_digital_root(self, n):
        return 0 if n == 0 else (9 if n % 9 == 0 else n % 9)
    def synthesize_waveguide(self, node_id, external_flux_voltage=1.0):
        if node_id < 0 or node_id >= mc.M_TOTAL: return {"error": "Out of bounds"}
        bit_offset = (node_id * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_offset) & 1
        d_root = self.calculate_digital_root(node_id)
        is_tesla_vector = d_root in [3, 6, 9]
        base_phase = (2.0 * math.pi * node_id) / mc.M_TOTAL
        phase_modulation = base_phase + (mc.ALPHA_GEOMETRIC * external_flux_voltage * (1.0 if up_bit else -1.0))
        target_frequency_hz = 114.0 * (d_root + 1) * (100.0 if is_tesla_vector else 10.0)
        amplitude_ratio = 1.0 + (mc.ALPHA_GEOMETRIC * (mc.DELTA_S % 7)) if not is_tesla_vector else 3.0
        return {
            "node_id": node_id, "vortex_root": d_root, "control_path": "Crimson Active Triad" if is_tesla_vector else "Blue Material Path",
            "rf_synthesis": {"frequency_hz": round(target_frequency_hz, 2), "amplitude_volts": round(amplitude_ratio * external_flux_voltage, 4), "phase_radians": round(phase_modulation % (2 * math.pi), 6)}
        }

def main():
    synthesizer = FieldSynthesizer()
    print("🔮 Initializing Uncharted Waveguide Matrix Synthesis for Nodes 3, 6, 9...")
    for test_node in [3, 6, 9]:
        profile = synthesizer.synthesize_waveguide(test_node, external_flux_voltage=2.4)
        print(f"\\nNode {test_node} Verification Metadata:")
        print(json.dumps(profile, indent=4))

if __name__ == "__main__": main()
