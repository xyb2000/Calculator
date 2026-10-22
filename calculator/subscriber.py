"""Receive and log greetings from the relative ``chatter`` topic."""

from typing import List, Optional

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    """Keep the subscription alive for the lifetime of the node."""

    def __init__(self) -> None:
        super().__init__("listener")
        self._subscription = self.create_subscription(String, "chatter", self._on_message, 10)
        self.get_logger().info(f"Listening on {self._subscription.topic_name}")

    def _on_message(self, message: String) -> None:
        self.get_logger().info(f'I heard: "{message.data}"')


def main(args: Optional[List[str]] = None) -> None:
    """Run the subscriber until ROS shutdown or an interrupt."""
    rclpy.init(args=args)
    node = None
    try:
        node = Listener()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
