import unittest
from src.swarm_controller import SwarmClusterOrchestrator, HardwareNodeStatus, SwarmCommandPayload

class TestSwarmClusterOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = SwarmClusterOrchestrator()

    def test_node_registration(self):
        new_node = HardwareNodeStatus(
            node_id="node_gamma_sensor",
            ip_address="192.168.1.103",
            hardware_type="SENSOR_RIG"
        )
        res = self.orchestrator.register_node(new_node)
        self.assertEqual(res["status"], "REGISTERED")
        self.assertIn("node_gamma_sensor", self.orchestrator.nodes)

    def test_swarm_command_dispatch(self):
        cmd = SwarmCommandPayload(
            so13_rotation_angle_rad=0.7854,
            rf_carrier_freq_hz=432000000.0
        )
        res = self.orchestrator.dispatch_swarm_command(cmd)
        self.assertGreater(res["dispatched_nodes_count"], 0)
        self.assertIn("swarm_execution_id", res)

if __name__ == '__main__':
    unittest.main()
