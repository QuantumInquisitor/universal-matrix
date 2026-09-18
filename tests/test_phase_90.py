import unittest
from src.hal.mesh_orchestrator import EdgeMeshOrchestrator

class TestPhase90Mesh(unittest.TestCase):
    def setUp(self):
        self.orchestrator = EdgeMeshOrchestrator()

    def test_workload_dispatch(self):
        res = self.orchestrator.dispatch_workload("task-101", 2048)
        self.assertEqual(res["status"], "WORKLOAD_DISPATCHED")
        self.assertIn(res["assigned_node"], ["node-alpha", "node-beta"])
        self.assertEqual(res["tensor_size"], 2048)

if __name__ == "__main__":
    unittest.main()
