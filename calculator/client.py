"""Perform one service call with bounded discovery and response waits."""

import sys
from typing import List, Optional

import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from calculator.cli import build_parser


class AdditionClient(Node):
    """Use asynchronous ROS requests while keeping a simple one-shot interface."""

    def __init__(self) -> None:
        super().__init__("add_two_ints_client")
        self._client = self.create_client(AddTwoInts, "add_two_ints")

    def add(
        self,
        a: int,
        b: int,
        *,
        discovery_timeout: float,
        request_timeout: float,
    ) -> int:
        """Return the sum or raise a descriptive communication error."""
        self.get_logger().info(f"Waiting up to {discovery_timeout:g}s for {self._client.srv_name}")
        if not self._client.wait_for_service(timeout_sec=discovery_timeout):
            raise TimeoutError(
                f"service {self._client.srv_name} unavailable after {discovery_timeout:g}s"
            )

        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        future = self._client.call_async(request)
        try:
            rclpy.spin_until_future_complete(self, future, timeout_sec=request_timeout)
            if not future.done():
                raise TimeoutError(
                    f"no response from {self._client.srv_name} after {request_timeout:g}s"
                )
            if future.cancelled():
                raise RuntimeError("service request was cancelled")
            if future.exception() is not None:
                raise RuntimeError(
                    f"service request failed: {future.exception()}"
                ) from future.exception()
            response = future.result()
            if response is None:
                raise RuntimeError("service returned no response")
            return response.sum
        finally:
            if not future.done():
                # Stop tracking late replies after a timeout or interruption.
                # This cancels local waiting, not work already running on a server.
                self._client.remove_pending_request(future)
                future.cancel()


def main(args: Optional[List[str]] = None) -> int:
    """Return 0 on success, 1 on communication failure, or argparse's exit code."""
    command_line = sys.argv if args is None else [sys.argv[0], *args]
    options = build_parser().parse_args(remove_ros_args(args=command_line)[1:])
    rclpy.init(args=command_line)
    node = None
    try:
        node = AdditionClient()
        result = node.add(
            options.a,
            options.b,
            discovery_timeout=options.discovery_timeout,
            request_timeout=options.request_timeout,
        )
        node.get_logger().info(f"Result: {options.a} + {options.b} = {result}")
        return 0
    except (KeyboardInterrupt, ExternalShutdownException):
        return 1
    except (TimeoutError, RuntimeError) as exc:
        if node is not None:
            node.get_logger().error(str(exc))
        else:
            print(f"Unable to create addition client: {exc}", file=sys.stderr)
        return 1
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
