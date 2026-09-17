class GridPowerManager:
    def __init__(self, max_bus_voltage_v: float = 48.0, max_current_amps: float = 50.0):
        self.max_bus_voltage_v = max_bus_voltage_v
        self.max_current_amps = max_current_amps

    def evaluate_power_state(self, telemetry: dict) -> dict:
        voltage = telemetry.get("bus_voltage_v", 0.0)
        current = telemetry.get("bus_current_amps", 0.0)
        temp_c = telemetry.get("battery_temp_c", 25.0)

        power_watts = voltage * current
        overvoltage = voltage > self.max_bus_voltage_v
        overcurrent = current > self.max_current_amps
        thermal_throttle = temp_c > 65.0

        status = "NOMINAL"
        duty_cycle_limit = 1.0

        if overvoltage or overcurrent or temp_c > 80.0:
            status = "TRIPPED_OVERLOAD"
            duty_cycle_limit = 0.0
        elif thermal_throttle:
            status = "THERMAL_THROTTLED"
            duty_cycle_limit = 0.50

        return {
            "status": status,
            "power_watts": power_watts,
            "duty_cycle_limit": duty_cycle_limit,
            "overvoltage_flag": overvoltage,
            "overcurrent_flag": overcurrent,
            "thermal_throttle_flag": thermal_throttle
        }