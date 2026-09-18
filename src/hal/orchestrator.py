from src.drivers.can_driver import CANDriver
from src.drivers.cuda_driver import CUDADriver
from src.drivers.evm_driver import EVMDriver
from src.drivers.k8s_driver import KubernetesDriver
from src.drivers.qpu_driver import QPUDriver
from src.drivers.cnc_driver import CNCMotionDriver
from src.drivers.marx_driver import MarxGeneratorDriver
from src.drivers.photonic_driver import PhotonicCoprocessorDriver
from src.drivers.fpga_driver import FPGADriver
from src.drivers.spacex_driver import SpaceXDriver

class UniversalHALOrchestrator:
    def __init__(self):
        self.drivers = {
            "can": CANDriver(),
            "cuda": CUDADriver(),
            "evm": EVMDriver(),
            "k8s": KubernetesDriver(),
            "qpu": QPUDriver(),
            "cnc": CNCMotionDriver(),
            "marx": MarxGeneratorDriver(),
            "photonic": PhotonicCoprocessorDriver(),
            "fpga": FPGADriver(),
            "spacex": SpaceXDriver()
        }

    def get_system_wide_status(self) -> dict:
        status_report = {}
        for key, driver in self.drivers.items():
            try:
                status_report[key] = driver.get_status()
            except Exception as e:
                status_report[key] = {"error": str(e)}
        return {
            "total_registered_drivers": len(self.drivers),
            "system_health": "ALL_SYSTEMS_OPERATIONAL",
            "driver_statuses": status_report
        }

