from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class CUDADriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.device = "cpu"
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                import torch
                if torch.cuda.is_available():
                    self.device = f"cuda:{config.CUDA_DEVICE_ID}"
                    return True
                else:
                    self.mode = "CPU_FALLBACK"
                    return False
            except ImportError:
                self.mode = "CPU_FALLBACK"
                return False
        else:
            return True

    def execute_tensor_transform(self, input_tensor: list, scale_factor: float) -> dict:
        if self.mode == "REAL" and self.device.startswith("cuda"):
            import torch
            tensor = torch.tensor(input_tensor, dtype=torch.float32, device=self.device)
            transformed = (tensor * scale_factor).cpu().tolist()
            return {
                "status": "EXECUTED_REAL_CUDA_KERNEL",
                "device": self.device,
                "transformed_tensor": transformed
            }
        else:
            # CPU/Mock vector acceleration fallback
            transformed = [float(x) * scale_factor for x in input_tensor]
            return {
                "status": "EXECUTED_FALLBACK_VECTOR_KERNEL",
                "mode": self.mode,
                "transformed_tensor": transformed
            }

    def get_status(self) -> dict:
        return {
            "driver": "CUDADriver",
            "active_mode": self.mode,
            "target_device": self.device
        }

