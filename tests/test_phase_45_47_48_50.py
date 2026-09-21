import unittest
from src.can_bus_driver import CANBusDriver, CANFramePayload
from src.physics_verifier import SymbolicPhysicsVerifier, FieldInvariantPayload
from src.marx_gate_array import MarxGateArrayController, MarxArrayConfig
from src.qiskit_quantum_bridge import QiskitQuantumBridge, QuantumCircuitRequest

class TestPhase45to50Modules(unittest.TestCase):
    def test_can_bus_compiler(self):
        driver = CANBusDriver()
        payload = CANFramePayload(arbitration_id=0x123, data_bytes=[1, 2, 3, 4])
        res = driver.compile_can_frame(payload)
        self.assertEqual(res["status"], "CAN_FRAME_COMPILED")
        self.assertEqual(res["arbitration_id_hex"], "0x123")

    def test_physics_verifier(self):
        verifier = SymbolicPhysicsVerifier()
        payload = FieldInvariantPayload(electric_field_v_m=100.0, magnetic_field_tesla=0.5, frequency_hz=432000000.0)
        res = verifier.verify_invariants(payload)
        self.assertEqual(res["status"], "REFERENCE_EXPRESSIONS_EVALUATED")
        self.assertTrue(res["conservation_laws_satisfied"])

    def test_marx_gate_array(self):
        controller = MarxGateArrayController()
        config = MarxArrayConfig(stage_count=5, charge_voltage_kv=10.0, gate_trigger_delay_ns=10.0)
        res = controller.compute_gate_delays(config)
        self.assertEqual(res["peak_erected_voltage_kv"], 50.0)
        self.assertEqual(len(res["gate_trigger_delays_ns"]), 5)

    def test_qiskit_bridge(self):
        bridge = QiskitQuantumBridge()
        req = QuantumCircuitRequest(qubit_count=3, so13_rotation_angle_rad=0.7854)
        res = bridge.generate_quantum_circuit_manifest(req)
        self.assertEqual(res["status"], "QUANTUM_CIRCUIT_COMPILED")
        self.assertIn("OPENQASM", res["qiskit_compatible_qasm"])

if __name__ == '__main__':
    unittest.main()
