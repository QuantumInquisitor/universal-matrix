import os

class SystemConfig:
    SYSTEM_MODE = os.getenv("SYSTEM_MODE", "MOCK").upper()
    USE_REAL_HARDWARE = SYSTEM_MODE == "REAL"
    CAN_CHANNEL = os.getenv("CAN_CHANNEL", "can0")
    CUDA_DEVICE_ID = int(os.getenv("CUDA_DEVICE_ID", "0"))
    EVM_RPC_URL = os.getenv("EVM_RPC_URL", "https://rpc.sepolia.org")

config = SystemConfig()

