import unittest
import time
from src.spatial_teleoperation_gateway import SpatialTeleoperationGateway, TeleoperationPacket

class TestSpatialTeleoperationGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = SpatialTeleoperationGateway()

    def test_nominal_teleop_command(self):
        packet = TeleoperationPacket(
            session_id="xr_session_88",
            operator_id="operator_admin_01",
            target_hardware_node="node_kuka_arm",
            teleop_command_type="POSITION_DELTA",
            command_vector=[0.01, -0.02, 0.05],
            timestamp_ns=time.time_ns()
        )
        res = self.gateway.process_teleop_command(packet)
        self.assertEqual(res["status"], "TELEOP_COMMAND_PROCESSED")
        self.assertTrue(res["command_executed"])
        self.assertEqual(res["spatial_vector_applied"], [0.01, -0.02, 0.05])

if __name__ == '__main__':
    unittest.main()
