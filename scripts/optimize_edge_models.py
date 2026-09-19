import os
import sys
import time
import logging
import argparse
from typing import Dict, Any, Tuple

import numpy as np
import torch
import torch.nn as nn

try:
    import onnx
    import onnxruntime as ort
    from onnxruntime.quantization import (
        quantize_dynamic,
        QuantType,
    )
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EdgeOptimizer")


class StandalonePINONetwork(nn.Module):
    """
    Self-contained Physics-Informed Neural Operator (PINO) Guardrail Network
    for sub-millisecond edge latency benchmarking.
    """
    def __init__(self, in_features=13, hidden_dim=64):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden_dim)
        self.act1 = nn.GELU()
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.act2 = nn.GELU()
        self.fc3 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        h = self.act1(self.fc1(x))
        h = self.act2(self.fc2(h))
        energy_norm = torch.sigmoid(self.fc3(h))
        safety_flag = (energy_norm > 0.85).float()
        return energy_norm, safety_flag


class EdgeModelOptimizer:
    """
    Orchestrates ONNX export, graph optimization, and INT8 quantization
    for embedded real-time PINO safety guardrails.
    """

    def __init__(self, output_dir: str = "models/exported"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.fp32_onnx_path = os.path.join(self.output_dir, "pino_guardrail_fp32.onnx")
        self.int8_onnx_path = os.path.join(self.output_dir, "pino_guardrail_int8.onnx")

    def export_pino_to_onnx(self, pino_model: nn.Module, sample_input: torch.Tensor) -> str:
        logger.info(f"Exporting PyTorch FP32 Engine -> {self.fp32_onnx_path}")
        pino_model.eval()

        torch.onnx.export(
            pino_model,
            sample_input,
            self.fp32_onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["input_tensor"],
            output_names=["energy_norm", "safety_flag"],
            dynamic_axes={
                "input_tensor": {0: "batch_size"},
                "energy_norm": {0: "batch_size"},
                "safety_flag": {0: "batch_size"}
            },
            dynamo=False
        )
        logger.info("FP32 ONNX export completed.")
        return self.fp32_onnx_path

    def quantize_int8_dynamic(self) -> str:
        if not HAS_ONNX:
            raise ImportError("onnxruntime and onnx packages are required for quantization.")

        logger.info(f"Applying Dynamic INT8 Quantization -> {self.int8_onnx_path}")
        
        # Quantize direct ONNX graph bypassing shape inference checks
        quantize_dynamic(
            model_input=self.fp32_onnx_path,
            model_output=self.int8_onnx_path,
            weight_type=QuantType.QUInt8,
            nodes_to_quantize=['/fc1/MatMul', '/fc2/MatMul', '/fc3/MatMul'] if os.path.exists(self.fp32_onnx_path) else None
        )
        logger.info("Dynamic INT8 quantization completed.")
        return self.int8_onnx_path

    def benchmark_execution_latency(self, input_shape: Tuple[int, ...], iterations: int = 1000):
        logger.info("Starting sub-millisecond edge latency benchmark...")
        dummy_np = np.random.randn(*input_shape).astype(np.float32)

        # Benchmark FP32 vs INT8
        for path, name in [(self.fp32_onnx_path, "FP32"), (self.int8_onnx_path, "INT8")]:
            if HAS_ONNX and os.path.exists(path):
                session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
                input_name = session.get_inputs()[0].name
                
                # Warmup
                for _ in range(50):
                    session.run(None, {input_name: dummy_np})

                start_time = time.perf_counter()
                for _ in range(iterations):
                    session.run(None, {input_name: dummy_np})
                elapsed = time.perf_counter() - start_time
                avg_micros = (elapsed / iterations) * 1e6

                logger.info(f"[ONNX {name} Edge Engine] Avg Latency: {avg_micros:.2f} µs per evaluation")
                if name == "INT8" and avg_micros < 200.0:
                    logger.info("PERFORMANCE VERIFIED: Sub-200 microsecond E-STOP latency target ACHIEVED.")


def main():
    parser = argparse.ArgumentParser(description="Edge PINO Engine ONNX Optimizer & INT8 Quantizer")
    parser.add_argument("--output-dir", type=str, default="models/exported", help="Path for exported models")
    parser.add_argument("--benchmark-iters", type=int, default=1000, help="Number of benchmark iterations")
    args = parser.parse_args()

    pino_engine = StandalonePINONetwork()
    sample_input = torch.randn(1, 13)

    optimizer = EdgeModelOptimizer(output_dir=args.output_dir)
    optimizer.export_pino_to_onnx(pino_engine, sample_input)
    
    if HAS_ONNX:
        optimizer.quantize_int8_dynamic()
        optimizer.benchmark_execution_latency(input_shape=(1, 13), iterations=args.benchmark_iters)


if __name__ == "__main__":
    main()
    