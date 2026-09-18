from src.hal.base_driver import BaseHardwareDriver
from src.config import config
import src.hardware_mocks as hardware_mocks

class MarxGeneratorDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.gpio_pin = 18
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.gpio_pin, GPIO.OUT)
                return True
            except (ImportError, RuntimeError):
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def trigger_discharge_pulse(self, target_voltage_kv: float = 25.0) -> dict:
        if self.mode == "REAL":
            import RPi.GPIO as GPIO
            GPIO.output(self.gpio_pin, GPIO.HIGH)
            # Pulse duration pulse switch
            GPIO.output(self.gpio_pin, GPIO.LOW)
            return {
                "status": "HARDWARE_PULSE_FIRED",
                "gpio_pin": self.gpio_pin,
                "discharge_voltage_kv": target_voltage_kv
            }
        else:
            return {
                "status": "SIMULATED_PULSE_FIRED",
                "mode": self.mode,
                "discharge_voltage_kv": target_voltage_kv,
                "waveform_peak_amps": target_voltage_kv * 40.0
            }

    def get_status(self) -> dict:
        return {
            "driver": "MarxGeneratorDriver",
            "active_mode": self.mode,
            "gpio_pin": self.gpio_pin
        }

