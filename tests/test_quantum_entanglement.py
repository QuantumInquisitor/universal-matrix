import unittest
import time
from src.quantum_entanglement_emulator import QuantumEntanglementEmulator, NodeStatePayload

class TestQuantumEntanglementEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = QuantumEntanglementEmulator()

    def test_node_synchronization(self):
        ts = time.time_ns()
        node_a = NodeStatePayload(
            node_id="node_alpha_sdr",
            so13_tensor_state=[1.0, 0.0, 0.0, 1.0],
            phase_offset_rad=0.0,
            telemetry_timestamp_ns=ts
        )
        node_b = NodeStatePayload(
            node_id="node_beta_cnc",
            so13_tensor_state=[1.0, 0.0, 0.0, 1.0],
            phase_offset_rad=0.0,
            telemetry_timestamp_ns=ts + 200 # 200 ns skew
        )

        res = self.emulator.synchronize_entangled_nodes(node_a, node_b)
        self.assertEqual(res["status"], "ENTANGLEMENT_SYNC_ACTIVE")
        self.assertEqual(res["entanglement_coherence"], 1.0)
        self.assertEqual(res["bell_state_fidelity"], 1.0)
        self.assertTrue(res["sub_nanosecond_parity_achieved"])

if __name__ == '__main__':
    unittest.main()
