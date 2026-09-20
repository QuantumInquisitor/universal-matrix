import unittest
from src.metrics import MetricsManager

class TestPhase59TelemetryMetrics(unittest.TestCase):
    def test_metrics_recording_and_export(self):
        MetricsManager.record_compute("Phase_53")
        MetricsManager.set_node_latency("us-east-1", 14.2)
        MetricsManager.set_rl_reward(0.95)

        data, content_type = MetricsManager.export_metrics()
        metrics_text = data.decode("utf-8")

        self.assertTrue("matrix_compute_executions_total" in metrics_text or "matrix_simulation_steps_total" in metrics_text)
        self.assertIn("matrix_cluster_node_latency_ms", metrics_text)
        self.assertIn("matrix_rl_reward_score", metrics_text)
        # Fix: Accept version 1.0.0 returned by the installed library
        self.assertEqual(content_type, "text/plain; version=1.0.0; charset=utf-8")

if __name__ == "__main__":
    unittest.main()

