import unittest
from src.swarm_robotics_controller import SwarmRoboticsController, RobotTargetPose

class TestSwarmRoboticsController(unittest.TestCase):
    def setUp(self):
        self.controller = SwarmRoboticsController()

    def test_inverse_kinematics_generation(self):
        pose = RobotTargetPose(
            robot_id="kuka_arm_alpha",
            target_xyz=[0.4, 0.2, 0.5],
            target_rpy_deg=[0.0, 45.0, 90.0],
            so13_rotation_angle_rad=0.7854
        )
        res = self.controller.compute_inverse_kinematics_6dof(pose)
        self.assertEqual(res["status"], "TRAJECTORY_GENERATED")
        self.assertEqual(res["robot_id"], "kuka_arm_alpha")
        self.assertEqual(len(res["joint_angles_deg"]), 6)
        self.assertTrue(res["kinematic_reachability"])

if __name__ == '__main__':
    unittest.main()
