import time
import jwt
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

SECRET_KEY = "UNIVERSAL_MATRIX_SECRET_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"

class TenantCredentials(BaseModel):
    tenant_id: str
    role: str = "operator"  # "admin", "operator", "read_only"
    hardware_access_keys: list[str] = Field(default_factory=lambda: ["SDR", "CNC", "SWARM"])

class HardwareAuthGateway:
    """
    Phase 24: Enterprise JWT authentication, RBAC authorization,
    and multi-tenant hardware session key management.
    """
    def generate_token(self, creds: TenantCredentials, expires_in_sec: int = 3600) -> str:
        payload = {
            "tenant_id": creds.tenant_id,
            "role": creds.role,
            "hardware_access": creds.hardware_access_keys,
            "exp": int(time.time()) + expires_in_sec
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {"valid": True, "payload": decoded}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token signature"}

    def authorize_hardware_access(self, token: str, required_hardware: str) -> bool:
        res = self.verify_token(token)
        if not res["valid"]:
            return False
        user_hardware = res["payload"].get("hardware_access", [])
        return required_hardware in user_hardware or "ALL" in user_hardware
