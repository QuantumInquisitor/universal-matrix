"""Central runtime security configuration.

No reusable credentials are stored in source. Production deployments should set
UNIVERSAL_MATRIX_JWT_SECRET and, if the legacy operator login is enabled,
UNIVERSAL_MATRIX_OPERATOR_PASSWORD.
"""

from __future__ import annotations

import logging
import os
import secrets

logger = logging.getLogger("UniversalMatrixSecurity")

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.getenv("UNIVERSAL_MATRIX_JWT_SECRET", "").strip()
if not JWT_SECRET:
    JWT_SECRET = secrets.token_urlsafe(48)
    logger.warning(
        "UNIVERSAL_MATRIX_JWT_SECRET is unset; using an ephemeral process-local secret"
    )

OPERATOR_PASSWORD = os.getenv("UNIVERSAL_MATRIX_OPERATOR_PASSWORD", "")
REDIS_URL = os.getenv("UNIVERSAL_MATRIX_REDIS_URL", "redis://localhost:6379")
