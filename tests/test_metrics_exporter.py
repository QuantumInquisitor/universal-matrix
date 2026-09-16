import unittest
from src.metrics_exporter import PrometheusMetricsExporter

class TestPrometheusMetricsExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = PrometheusMetricsExporter()

    def test_record_and_export(self):
        self.exporter.record_transformation(12.4)
        output = self.exporter.generate_prometheus_metrics()
        self.assertIn("universal_matrix_so13_transforms_total 1", output)
        self.assertIn("universal_matrix_transform_latency_ms 12.4", output)
        self.assertIn("universal_matrix_available_cpu_cores", output)

if __name__ == '__main__':
    unittest.main()
