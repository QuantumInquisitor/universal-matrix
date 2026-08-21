import unittest
import json

class TestDistributedStateStorage(unittest.TestCase):

    def test_snapshot_schema_formatting(self):
        """Verify matrix engine snapshot payload serializes into valid JSON for Redis storage."""
        payload = {
            "step": 1050,
            "clock_drift_ns": 42.12,
            "norm_sum": 1.0000,
            "active_nodes": 114,
            "status": "synchronized"
        }
        serialized = json.dumps(payload)
        deserialized = json.loads(serialized)
        
        self.assertEqual(deserialized["step"], 1050)
        self.assertEqual(deserialized["active_nodes"], 114)
        self.assertEqual(deserialized["status"], "synchronized")

if __name__ == "__main__":
    unittest.main()