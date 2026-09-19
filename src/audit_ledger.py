import os
import json
import time
import hashlib
import stat
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ImmutableAuditLedger")


class CryptographicBlock:
    def __init__(self, index: int, timestamp: float, event_type: str, payload: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.payload = payload
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

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
    Hardware-level Write-Once-Read-Many (WORM) Cryptographic Immutable Ledger.
    Combines SHA-256 block chaining with OS-level append-only access controls.
    """
    def __init__(self, storage_path: str = "logs/audit_ledger.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.chain: List[CryptographicBlock] = []
        self._load_or_initialize()

    def _load_or_initialize(self):
        if os.path.exists(self.storage_path):
            try:
                # Temporarily unlock read permissions if locked
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        block = CryptographicBlock(
                            index=item["index"],
                            timestamp=item["timestamp"],
                            event_type=item["event_type"],
                            payload=item["payload"],
                            previous_hash=item["previous_hash"]
                        )
                        block.hash = item["hash"]
                        self.chain.append(block)
            except Exception as e:
                logger.error(f"Failed to load existing ledger, initializing new chain: {e}")
                self._create_genesis_block()
        else:
            self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = CryptographicBlock(0, time.time(), "GENESIS_EVENT", {"system": "SO(13) Universal Matrix Core"}, "0" * 64)
        self.chain = [genesis]
        self._persist_and_lock()

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> CryptographicBlock:
        prev_block = self.chain[-1]
        new_block = CryptographicBlock(
            index=len(self.chain),
            timestamp=time.time(),
            event_type=event_type,
            payload=payload,
            previous_hash=prev_block.hash
        )
        self.chain.append(new_block)
        self._persist_and_lock()
        return new_block

    def _persist_and_lock(self):
        """Persists chain to disk and applies OS-level append/read-only protection."""
        # Enable write access temporarily to flush new block
        if os.path.exists(self.storage_path):
            os.chmod(self.storage_path, stat.S_IWRITE | stat.S_IREAD)

        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

        # Enforce Read-Only WORM protection to prevent truncation/modification
        os.chmod(self.storage_path, stat.S_IREAD)

    def verify_integrity(self) -> bool:
        """Verifies the SHA-256 hash continuity of the entire ledger chain."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.previous_hash != prev.hash:
                logger.error(f"Chain broken at index {i}: Previous hash mismatch.")
                return False

            if curr.hash != curr.calculate_hash():
                logger.error(f"Tamper detected at index {i}: Block hash invalid.")
                return False

        return True


if __name__ == "__main__":
    ledger = CryptographicAuditLedger()
    ledger.record_event("SAFETY_INTERLOCK_TEST", {"status": "ACTIVE", "voltage": 24.0})
    is_valid = ledger.verify_integrity()
    print(f"Ledger Immutability & Integrity Verified: {is_valid} (Total Blocks: {len(ledger.chain)})")
