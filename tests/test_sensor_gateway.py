import unittest
from src.sensor_network_gateway import PhysicalFieldCorrector, SensorTelemetryPayload

class TestSensorNetworkGateway(unittest.TestCase):
    def setUp(self):
        self.corrector = PhysicalFieldCorrector(baseline_field_uT=45.0)

    def test_sensor_ingestion_and_correction(self):
        payload = SensorTelemetryPayload(
            magnetometer_uT=[30.0, 40.0, 0.0],  # Magnitude = 50 uT
            hall_effect_voltage_v=2.6,
            clock_drift_nanoseconds=12.5
        )
        res = self.corrector.process_sensor_feed(payload)
        self.assertEqual(res["magnetic_magnitude_uT"], 50.0)
        self.assertEqual(res["field_delta_uT"], 5.0)
        self.assertTrue(res["correction_applied"])

if __name__ == '__main__':
    unittest.main()
