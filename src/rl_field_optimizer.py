import math

class RLFieldOptimizer:
    def __init__(self, learning_rate: float = 0.001, discount_factor: float = 0.99):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def optimize_field_trajectory(self, telemetry: dict) -> dict:
        """
        Calculates optimized 6-DoF pose adjustments and transducer phase shifts
        using telemetry reward signals.
        """
        current_pose = telemetry.get("current_pose_6dof", [0.0]*6)
        sensor_feedback = telemetry.get("field_intensity_feedback", 0.0)
        target_intensity = telemetry.get("target_intensity", 1.0)

        # Compute immediate scalar reward based on target convergence error
        error = abs(target_intensity - sensor_feedback)
        reward = max(0.0, 1.0 - error)

        # Policy-gradient step vector generation
        gradient_step = self.learning_rate * (1.0 - reward)
        optimized_pose = [round(val + gradient_step, 6) for val in current_pose]

        # Calculate optimal transducer array phase offset
        phase_shift_deg = round((reward * 360.0) % 360.0, 2)

        status = "OPTIMAL" if reward >= 0.9 else "CONVERGING"

        return {
            "status": status,
            "reward_score": round(reward, 4),
            "gradient_step_size": gradient_step,
            "optimized_pose_6dof": optimized_pose,
            "recommended_transducer_phase_deg": phase_shift_deg
        }

