from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ControllerTransform(BaseModel):
    position_xyz: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation_quaternion: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])

class SpatialXRState(BaseModel):
    left_hand: ControllerTransform = Field(default_factory=ControllerTransform)
    right_hand: ControllerTransform = Field(default_factory=ControllerTransform)
    toroidal_coherence: float = Field(0.85, ge=0.0, le=1.0)

class WebXRHapticController:
    """
    Phase 26: WebXR spatial tracking controller translating 6-DoF hand poses into
    SO(13) plane rotations and triggering bio-adaptive haptic pulse feedback.
    """
    def process_xr_frame(self, state: SpatialXRState) -> Dict[str, Any]:
        # Compute spatial hand distance for toroidal field scaling
        lx, ly, lz = state.left_hand.position_xyz
        rx, ry, rz = state.right_hand.position_xyz
        hand_distance = ((rx - lx)**2 + (ry - ly)**2 + (rz - lz)**2) ** 0.5

        # Translate right hand pitch/yaw quaternion into SO(13) rotation angle
        qx, qy, qz, qw = state.right_hand.rotation_quaternion
        so13_rotation_angle_rad = round(2.0 * (qw * qz + qx * qy), 4)

        # Trigger haptic feedback intensity if coherence drops below threshold (0.65)
        haptic_intensity = 0.0
        if state.toroidal_coherence < 0.65:
            haptic_intensity = round((0.65 - state.toroidal_coherence) / 0.65, 2)

        return {
            "hand_distance_meters": round(hand_distance, 4),
            "so13_rotation_angle_rad": so13_rotation_angle_rad,
            "haptic_feedback": {
                "trigger_haptic": haptic_intensity > 0.0,
                "intensity": haptic_intensity,
                "frequency_hz": 150.0 if haptic_intensity > 0.0 else 0.0
            }
        }
