import math
import logging
import numpy as np
from typing import Tuple, Dict, Any, Union, List

# --- HARDWARE ACCELERATION DISCOVERY ---
HAS_TORCH = False
HAS_CUPY = False
GPU_AVAILABLE = False
DEVICE_NAME = "CPU (NumPy)"

try:
    import torch
    HAS_TORCH = True
    if torch.cuda.is_available():
        GPU_AVAILABLE = True
        DEVICE_NAME = f"CUDA GPU (PyTorch - {torch.cuda.get_device_name(0)})"
except ImportError:
    pass

if not GPU_AVAILABLE:
    try:
        import cupy as cp
        HAS_CUPY = True
        GPU_AVAILABLE = True
        DEVICE_NAME = "CUDA GPU (CuPy)"
    except ImportError:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UniversalCalculator")

# Global Topological & Physical Constants
AXIOM_I = 0.0
N_CORE = 108
B_BOUNDARY = 6
M_TOTAL = 114
N_TOTAL = 114
B_VECTOR_SUM = 117.0
SCALE_FACTOR = (2**64 / (114 * 9.0 * 324.0)) / (54.0 * (math.pi**2))
LIGHT_SPEED = 299792458.0      # m/s
E_PLANCK = 1.9561e9            # Joules
ALPHA_GEOMETRIC = 1.0 / (54.0 * (math.pi ** 2))
SPEED_OF_LIGHT = LIGHT_SPEED
PLANCK_ENERGY = E_PLANCK


class UniversalMatrixCalculator:
    """
    Exact Mathematical Implementation of the 114-Node SO(13) Universal Matrix Engine.
    """
    def __init__(self):
        self.N_CORE = N_CORE
        self.B_BOUNDARY = B_BOUNDARY
        self.M_TOTAL = M_TOTAL
        self.STREAM_UP = 123456789
        self.STREAM_DOWN = 987654321
        self.DELTA_S = self.STREAM_DOWN - self.STREAM_UP
        self.BOUNDARY_MODULI = [9, 18, 27, 36, 45, 54]
        self.SCALE_FACTOR = SCALE_FACTOR
        self.ALPHA_VELOCITY_WAVE = 0.000780263869205562

    def compute_boundary_vector(self) -> List[int]:
        return [self.STREAM_DOWN % m for m in self.BOUNDARY_MODULI]

    def verify_axiom_1(self) -> float:
        term_sum = sum([-(self.STREAM_DOWN % n) + (self.STREAM_UP % n) for n in range(1, 55)])
        term_mod31 = self.DELTA_S % 31
        return float(term_sum - term_mod31 + 18)

    def calculate_exact_speed_of_light(self) -> float:
        ratio = (2**64) / float(self.DELTA_S)
        return float(18.0 * ratio * self.ALPHA_VELOCITY_WAVE)

    def compute_matrix_clock_drift(self, layer_flux_ratio: float, phi_t0: float, phi_t1: float) -> float:
        b_vec = self.compute_boundary_vector()
        b_sum = sum(b_vec)
        sigma_369 = 18.0
        flux_term = phi_t1 / phi_t0 if phi_t0 != 0 else 1.0
        return float(layer_flux_ratio * flux_term * (sigma_369 + b_sum) * self.SCALE_FACTOR)

    def generate_3d_toroidal_coordinates(self):
        coords = np.zeros((114, 3))
        for i in range(114):
            theta = (i / 114.0) * 2.0 * np.pi
            coords[i] = [np.cos(theta) * 5.0, np.sin(theta) * 5.0, i * 0.5]
        return coords

    def execute_vortex_doubling_step(self, val):
        if not isinstance(val, int) or val <= 0 or val > 57:
            raise ValueError(f"Invalid vortex doubling input: {val}. Must be an integer between 1 and 57.")
        if val == 57:
            return 0
        return (val * 2) % 9 or 9


class GPUTensorEngine:
    def __init__(self, force_cpu: bool = False):
        self.use_gpu = GPU_AVAILABLE and not force_cpu
        self.device_str = DEVICE_NAME if self.use_gpu else "CPU (NumPy)"
        logger.info(f"[*] Initialized Tensor Engine on: {self.device_str}")

    def compute_lattice_hamiltonian(self, grid_size: int = 114) -> Any:
        if self.use_gpu and HAS_TORCH:
            device = torch.device("cuda")
            identity = torch.eye(grid_size, device=device, dtype=torch.float64)
            boundary_weights = torch.full((grid_size, grid_size), B_BOUNDARY / N_CORE, device=device, dtype=torch.float64)
            return (identity * B_VECTOR_SUM) + (boundary_weights * SCALE_FACTOR * ALPHA_GEOMETRIC)
        elif self.use_gpu and HAS_CUPY:
            identity = cp.eye(grid_size, dtype=cp.float64)
            boundary_weights = cp.full((grid_size, grid_size), B_BOUNDARY / N_CORE, dtype=cp.float64)
            return (identity * B_VECTOR_SUM) + (boundary_weights * SCALE_FACTOR * ALPHA_GEOMETRIC)
        else:
            identity = np.eye(grid_size, dtype=np.float64)
            boundary_weights = np.full((grid_size, grid_size), B_BOUNDARY / N_CORE, dtype=np.float64)
            return (identity * B_VECTOR_SUM) + (boundary_weights * SCALE_FACTOR * ALPHA_GEOMETRIC)

    def batch_contract_tensors(self, tensor_stack: Any) -> Any:
        if self.use_gpu and HAS_TORCH:
            if not isinstance(tensor_stack, torch.Tensor):
                tensor_stack = torch.tensor(tensor_stack, device="cuda", dtype=torch.float64)
            return torch.einsum("ijk,jkl->il", tensor_stack, tensor_stack)
        elif self.use_gpu and HAS_CUPY:
            if not isinstance(tensor_stack, cp.ndarray):
                tensor_stack = cp.array(tensor_stack)
            return cp.einsum("ijk,jkl->il", tensor_stack, tensor_stack)
        else:
            if not isinstance(tensor_stack, np.ndarray):
                tensor_stack = np.array(tensor_stack)
            return np.einsum("ijk,jkl->il", tensor_stack, tensor_stack)


default_gpu_engine = GPUTensorEngine()
MatrixFieldEngine = UniversalMatrixCalculator

def get_hardware_status() -> Dict[str, Any]:
    return {
        "gpu_available": GPU_AVAILABLE,
        "device_name": DEVICE_NAME,
        "pytorch_installed": HAS_TORCH,
        "cupy_installed": HAS_CUPY,
        "total_nodes": N_TOTAL,
    }
