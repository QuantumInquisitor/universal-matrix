from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class EVMDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.w3 = None
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                from web3 import Web3
                self.w3 = Web3(Web3.HTTPProvider(config.EVM_RPC_URL))
                if self.w3.is_connected():
                    return True
                else:
                    self.mode = "MOCK_FALLBACK"
                    return False
            except ImportError:
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def query_chain_state(self, address: str = None) -> dict:
        if self.mode == "REAL" and self.w3 and self.w3.is_connected():
            latest_block = self.w3.eth.block_number
            balance = 0
            if address:
                balance = self.w3.eth.get_balance(address)
            return {
                "status": "EVM_REAL_NODE_QUERY_SUCCESS",
                "rpc_url": config.EVM_RPC_URL,
                "latest_block": latest_block,
                "balance_wei": balance
            }
        else:
            return {
                "status": "EVM_MOCK_QUERY_SUCCESS",
                "mode": self.mode,
                "latest_block": 18923041,
                "simulated_balance_eth": 10.5
            }

    def get_status(self) -> dict:
        return {
            "driver": "EVMDriver",
            "active_mode": self.mode,
            "target_rpc": config.EVM_RPC_URL
        }

