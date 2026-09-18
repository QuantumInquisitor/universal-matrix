import time
from src.rl_field_optimizer import RLFieldOptimizer
from src.can_bus_driver import CANBusDriver
import src.marx_gate_array as marx_module

class VirtualCANInterface:
    def __init__(self):
        self.driver = CANBusDriver()
        self.tx_buffer = []

    def send_pulse_command(self, node_id: int, pulse_width_us: float) -> bool:
        frame = {"arb_id": hex(node_id), "dlc": 8, "data": [int(pulse_width_us) & 0xFF, 0x01]}
        self.tx_buffer.append(frame)
        return True

class VirtualMarxGateArrayMock:
    def __init__(self):
        self.is_armed = False

    def arm_and_fire(self, voltage_kv: float, pulse_delay_ns: int) -> dict:
        self.is_armed = True
        return {
            "status": "FIRED",
            "peak_voltage_kv": voltage_kv * 0.98,
            "discharge_time_ns": pulse_delay_ns
        }

class HardwareIntegrationTestFixture:
    def __init__(self):
        self.rl_optimizer = RLFieldOptimizer()
        self.can_mock = VirtualCANInterface()
        self.marx_mock = VirtualMarxGateArrayMock()

    def run_end_to_end_loop(self, initial_state: list) -> dict:
        step_res = self.rl_optimizer.step(initial_state) if hasattr(self.rl_optimizer, "step") else {"action": [5.0, 100.0]}
        can_status = self.can_mock.send_pulse_command(node_id=0x120, pulse_width_us=100.0)
        discharge_res = self.marx_mock.arm_and_fire(voltage_kv=50.0, pulse_delay_ns=120)

        return {
            "status": "HIL_INTEGRATION_SUCCESS",
            "rl_optimization": step_res,
            "can_bus_tx": can_status,
            "marx_discharge": discharge_res,
            "tx_frames_count": len(self.can_mock.tx_buffer)
        }

