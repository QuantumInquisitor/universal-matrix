import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AuditLedger")


class AuditBlock:
    """
    Represents an individual immutable block in the SO(13) hardware audit ledger.
    """
    def __init__(self, index: int, timestamp: float, event_type: str, payload: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.payload = payload
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash
        }
        block_bytes = json.dumps(block_content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(block_bytes).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class CryptographicAuditLedger:
    """
    Manages an append-only cryptographic audit chain for enterprise safety and licensing compliance.
    """
    def __init__(self, storage_path: str = "logs/audit_ledger.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.chain: List[AuditBlock] = []
        self._initialize_ledger()

    def _initialize_ledger(self):
        if os.path.exists(self.storage_path):
            self.load_ledger()
        else:
            # Create Genesis Block
            genesis_block = AuditBlock(
                index=0,
                timestamp=time.time(),
                event_type="GENESIS",
                payload={"system": "SO(13) Universal Matrix Core initialized"},
                previous_hash="0" * 64
            )
            self.chain.append(genesis_block)
            self.save_ledger()

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> AuditBlock:
        last_block = self.chain[-1]
        new_block = AuditBlock(
            index=len(self.chain),
            timestamp=time.time(),
            event_type=event_type,
            payload=payload,
            previous_hash=last_block.hash
        )
        self.chain.append(new_block)
        self.save_ledger()
        logger.info(f"Recorded Audit Event #{new_block.index} [{event_type}]: {new_block.hash[:12]}...")
        return new_block

    def verify_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                logger.error(f"Tamper detected at block #{current.index}: Invalid hash signature.")
                return False

            if current.previous_hash != previous.hash:
                logger.error(f"Tamper detected at block #{current.index}: Broken chain link.")
                return False

        logger.info("Ledger integrity verified successfully. Zero tampering detected.")
        return True

    def save_ledger(self):
        data = [block.to_dict() for block in self.chain]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_ledger(self):
        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.chain = []
            for item in data:
                block = AuditBlock(
                    index=item["index"],
                    timestamp=item["timestamp"],
                    event_type=item["event_type"],
                    payload=item["payload"],
                    previous_hash=item["previous_hash"]
                )
                block.hash = item["hash"]
                self.chain.append(block)


if __name__ == "__main__":
    ledger = CryptographicAuditLedger()
    ledger.record_event("HARDWARE_ESTOP", {"reason": "PINO state divergence threshold exceeded", "latency_ms": 0.18})
    ledger.record_event("LICENSE_CHECK", {"client_id": "ENTERPRISE_CORP_001", "status": "ACTIVE_TIER1"})
    ledger.verify_integrity()
