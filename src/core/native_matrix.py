import torch
import numpy as np

class NativeSO13TensorCore:
    """
    Bare-Metal SO(13) Tensor Core executing 13-Dimensional Givens Rotations
    G(i, j, theta) in SO(13) Lie Algebra space.
    """
    def __init__(self, dim: int = 13):
        self.dim = dim

    def construct_givens_matrix(self, i: int, j: int, theta: float) -> torch.Tensor:
        """Generates a 13x13 Givens rotation matrix for plane (i, j)."""
        G = torch.eye(self.dim, dtype=torch.float64)
        c, s = np.cos(theta), np.sin(theta)
        G[i, i] = c
        G[i, j] = -s
        G[j, i] = s
        G[j, j] = c
        return G

    def rotate_so13_manifold(self, tensor: torch.Tensor, i: int = 0, j: int = 1, theta: float = 0.1) -> torch.Tensor:
        """Applies SO(13) rotational transformation to the input state tensor."""
        if tensor.dtype != torch.float64:
            tensor = tensor.to(torch.float64)
            
        G = self.construct_givens_matrix(i, j, theta)
        
        if tensor.ndim == 1:
            return torch.matmul(G, tensor)
        return torch.matmul(tensor, G.T)
