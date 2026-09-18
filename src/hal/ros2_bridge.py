from src.config import config

class ROS2BridgeDriver:
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.active_topic = "/universal_matrix/spatial_cmd"
        self.published_messages_count = 0

    def publish_spatial_twist(self, linear_velocity: list, angular_velocity: list) -> dict:
        self.published_messages_count += 1
        return {
            "status": "MESSAGE_PUBLISHED",
            "mode": self.mode,
            "topic": self.active_topic,
            "geometry_msg": {
                "linear": {"x": linear_velocity[0], "y": linear_velocity[1], "z": linear_velocity[2]},
                "angular": {"x": angular_velocity[0], "y": angular_velocity[1], "z": angular_velocity[2]}
            },
            "sequence_id": self.published_messages_count
        }
