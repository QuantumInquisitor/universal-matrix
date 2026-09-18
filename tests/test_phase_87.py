import unittest
from src.hal.ros2_bridge import ROS2BridgeDriver

class TestPhase87ROS2(unittest.TestCase):
    def setUp(self):
        self.driver = ROS2BridgeDriver()

    def test_twist_publication(self):
        res = self.driver.publish_spatial_twist([1.0, 0.0, 0.0], [0.0, 0.0, 0.5])
        self.assertEqual(res["status"], "MESSAGE_PUBLISHED")
        self.assertEqual(res["geometry_msg"]["linear"]["x"], 1.0)
        self.assertEqual(res["sequence_id"], 1)

if __name__ == "__main__":
    unittest.main()
