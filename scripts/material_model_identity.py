"""Explicit identity for the existing point-inertia powered material contract."""

POINT_POWERED_IDENTITY = {
    "inertia_model": "material-body-point-inertia-v1",
    "state_layout": "material-powered-node9-edge2-input1-v1",
    "energy_ownership": "material-powered-node-edge-group-ledgers-v1",
}


def point_powered_identity():
    """Return a fresh descriptor so callers cannot mutate later exports."""
    return dict(POINT_POWERED_IDENTITY)


def require_point_powered_identity(container, *, allow_legacy=False):
    """Reject explicit foreign/partial identities; absence is opt-in legacy only."""
    if not isinstance(container, dict):
        raise ValueError("model identity requires an object")
    if "model_identity" not in container:
        if allow_legacy:
            return "legacy-point-assumption"
        raise ValueError("explicit model_identity required")
    identity = container["model_identity"]
    if not isinstance(identity, dict) or identity != POINT_POWERED_IDENTITY:
        raise ValueError("unsupported inertia, state layout or energy ownership")
    return "explicit-point-identity"
