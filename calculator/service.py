"""Expose signed 64-bit addition through the standard ROS service schema."""

from typing import List, Optional

import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from calculator.arithmetic import add_int64


class AdditionServer(Node):
    """Serve additions using deterministic two's-complement overflow wrapping."""

    def __init__(self) -> None:
        super().__init__("add_two_ints_server")
        self._service = self.create_service(AddTwoInts, "add_two_ints", self._handle_add)
        self.get_logger().info(f"Addition service ready: {self._service.srv_name}")

    def _handle_add(
        self,
        request: AddTwoInts.Request,
        response: AddTwoInts.Response,
    ) -> AddTwoInts.Response:
        response.sum = add_int64(request.a, request.b)
        if request.a + request.b != response.sum:
            # AddTwoInts contains only an int64 sum, so it cannot carry an error.
            self.get_logger().warning(
                f"int64 overflow wrapped: {request.a} + {request.b} = {response.sum}"
            )
        else:
            self.get_logger().info(f"{request.a} + {request.b} = {response.sum}")
        return response


def main(args: Optional[List[str]] = None) -> None:
    """Run the service until ROS shutdown or an interrupt."""
    rclpy.init(args=args)
    node = None
    try:
        node = AdditionServer()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
