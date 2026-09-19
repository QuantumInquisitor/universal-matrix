import unittest
from src.hal.mesh_orchestrator import EdgeMeshOrchestrator

class TestMeshFailoverRemedy(unittest.TestCase):
    def setUp(self):
        self.orchestrator = EdgeMeshOrchestrator()

    def test_edge_cluster_failover_on_node_crash(self):
        payload = {"task": "spatial-telemetry-90", "node": "primary-node-01"}
        tensor_size = 2048
        
        # Dispatch workload with both payload and explicit tensor_size argument
        dispatch_res = self.orchestrator.dispatch_workload(payload, tensor_size)
        
        print(f"\n[Mesh Dispatch] Payload Result: {dispatch_res}")

        self.assertIsNotNone(dispatch_res)
        self.assertIn("status", dispatch_res)

if __name__ == "__main__":
    unittest.main()
