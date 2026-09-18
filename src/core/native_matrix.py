import numpy as np
from src.config import config

class NativeMatrixEngine:
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"

    def process_high_dim_matrix(self, matrix_data: list) -> dict:
        np_arr = np.array(matrix_data, dtype=np.float32)
        
        if self.mode == "REAL":
            try:
                import torch
                if torch.cuda.is_available():
                    tensor = torch.tensor(np_arr, device="cuda:0")
                    transformed = torch.matmul(tensor, tensor.T)
                    return {
                        "execution_engine": "BARE_METAL_CUDA_VRAM",
                        "shape": list(transformed.shape),
                        "result_matrix": transformed.cpu().numpy().tolist()
                    }
            except Exception:
                pass

        transformed = np.matmul(np_arr, np_arr.T)
        return {
            "execution_engine": "VECTORIZED_NUMPY_SIMULATION",
            "shape": list(transformed.shape),
            "result_matrix": transformed.tolist()
        }
