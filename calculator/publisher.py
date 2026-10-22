"""Publish a configurable greeting on the relative ``chatter`` topic."""

import math
from typing import List, Optional

import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """Publish one greeting per timer tick, starting with counter zero."""

    def __init__(self) -> None:
        super().__init__("talker")
        try:
            self.declare_parameter(
                "publish_period",
                0.5,
                ParameterDescriptor(
                    description="Seconds between messages; finite and greater than zero.",
                    read_only=True,
                ),
            )
            self.declare_parameter(
                "prefix",
                "Hello World: ",
                ParameterDescriptor(
                    description="Text prepended to the message counter.",
                    read_only=True,
                ),
            )
            period = self.get_parameter("publish_period").value
            if not math.isfinite(period) or period <= 0:
                raise ValueError("publish_period must be finite and greater than zero")

            self._prefix = self.get_parameter("prefix").value
            self._counter = 0
            self._publisher = self.create_publisher(String, "chatter", 10)
            self._timer = self.create_timer(period, self._publish_message)
        except Exception:
            # Construction failures must not leave a partly initialized ROS node.
            self.destroy_node()
            raise

        self.get_logger().info(
            f"Publishing on {self._publisher.topic_name} every {period:g} seconds"
        )

    def _publish_message(self) -> None:
        message = String()
        message.data = f"{self._prefix}{self._counter}"
        self._publisher.publish(message)
        self.get_logger().info(f'Publishing: "{message.data}"')
        self._counter += 1


def main(args: Optional[List[str]] = None) -> None:
    """Run the publisher until ROS shutdown or an interrupt."""
    rclpy.init(args=args)
    node = None
    try:
        node = Talker()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
