"""Launch the installed ROS nodes and verify their public middleware contracts.

The caller chooses ROS_DOMAIN_ID before starting the test process. Every endpoint
in this suite also lives under /integration to exercise launch namespacing.
Pure-Python environments skip this module rather than replacing ROS with mocks.
"""

# Imports after importorskip keep plain Python checks independent of ROS.
# ruff: noqa: E402

import re
import subprocess
import time
import unittest
from pathlib import Path

import pytest

rclpy = pytest.importorskip("rclpy")
launch = pytest.importorskip("launch")
launch_testing = pytest.importorskip("launch_testing")
pytest.importorskip("launch_ros")
pytest.importorskip("example_interfaces")

from ament_index_python.packages import get_package_prefix, get_package_share_directory
from example_interfaces.srv import AddTwoInts
from launch_testing.actions import ReadyToTest
from launch_testing.asserts import assertExitCodes
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import String

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


@pytest.mark.launch_test
def generate_test_description():
    """Use the installed public launch files, including their launch arguments."""
    launch_directory = Path(get_package_share_directory("Calculator")) / "launch"
    topics = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(launch_directory / "topics.launch.py")),
        launch_arguments={
            "namespace": "integration",
            "publish_period": "0.05",
            "prefix": "Test: ",
        }.items(),
    )
    service = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(launch_directory / "service.launch.py")),
        launch_arguments={
            "namespace": "integration",
            "start_client": "false",
        }.items(),
    )
    return launch.LaunchDescription([topics, service, ReadyToTest()])


class TestCalculatorIntegration(unittest.TestCase):
    """All sums travel through DDS to the separately launched service process."""

    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        rclpy.init(args=[], context=cls.context)
        cls.node = rclpy.create_node(
            "calculator_integration_probe", namespace="/integration", context=cls.context
        )
        cls.executor = SingleThreadedExecutor(context=cls.context)
        cls.executor.add_node(cls.node)
        cls.client = cls.node.create_client(AddTwoInts, "add_two_ints")
        if not cls.client.wait_for_service(timeout_sec=10.0):
            cls.tearDownClass()
            raise AssertionError("/integration/add_two_ints was not discovered within 10s")
        cls.client_executable = (
            Path(get_package_prefix("Calculator")) / "lib" / "Calculator" / "add_two_ints_client"
        )
        if not cls.client_executable.is_file():
            cls.tearDownClass()
            raise AssertionError("the installed one-shot client executable is missing")

    @classmethod
    def tearDownClass(cls):
        cls.executor.shutdown(timeout_sec=2.0)
        cls.node.destroy_node()
        if cls.context.ok():
            rclpy.shutdown(context=cls.context)

    def assert_sum(self, a, b, expected):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        future = self.client.call_async(request)
        try:
            self.executor.spin_until_future_complete(future, timeout_sec=5.0)
            self.assertTrue(future.done(), "service response did not arrive within 5s")
            self.assertFalse(future.cancelled(), "service request was cancelled")
            self.assertIsNone(future.exception())
            response = future.result()
            self.assertIsNotNone(response)
            self.assertEqual(response.sum, expected)
        finally:
            if not future.done():
                self.client.remove_pending_request(future)
                future.cancel()

    def run_client(self, a, b, *, remap=None, discovery="5", response="5"):
        command = [
            str(self.client_executable),
            str(a),
            str(b),
            "--discovery-timeout",
            discovery,
            "--request-timeout",
            response,
            "--ros-args",
            "-r",
            "__ns:=/integration",
        ]
        if remap is not None:
            command.extend(["-r", "add_two_ints:=" + remap])
        return subprocess.run(command, capture_output=True, text=True, timeout=15.0, check=False)

    def test_positive_operands(self):
        self.assert_sum(2, 3, 5)

    def test_zero_operands(self):
        self.assert_sum(0, 0, 0)

    def test_negative_operands(self):
        self.assert_sum(-7, -9, -16)

    def test_mixed_sign_operands(self):
        self.assert_sum(-7, 12, 5)

    def test_cancelling_operands(self):
        self.assert_sum(123456789, -123456789, 0)

    def test_large_positive_values(self):
        self.assert_sum(123456789, 987654321, 1111111110)

    def test_maximum_int64_endpoint(self):
        self.assert_sum(9223372036854775807, 0, 9223372036854775807)

    def test_minimum_int64_endpoint(self):
        self.assert_sum(-9223372036854775808, 0, -9223372036854775808)

    def test_opposite_int64_endpoints(self):
        self.assert_sum(9223372036854775807, -9223372036854775808, -1)

    def test_positive_overflow_wraps(self):
        self.assert_sum(9223372036854775807, 1, -9223372036854775808)

    def test_negative_overflow_wraps(self):
        self.assert_sum(-9223372036854775808, -1, 9223372036854775807)

    def test_same_int64_endpoints_wrap(self):
        self.assert_sum(9223372036854775807, 9223372036854775807, -2)
        self.assert_sum(-9223372036854775808, -9223372036854775808, 0)

    def test_server_accepts_requests_after_overflow(self):
        self.assert_sum(9223372036854775807, 1, -9223372036854775808)
        self.assert_sum(20, 22, 42)
        self.assert_sum(-9223372036854775808, -1, 9223372036854775807)
        self.assert_sum(1, 1, 2)

    def test_topic_has_configured_prefix_and_increasing_counter(self, proc_output):
        messages = []
        subscription = self.node.create_subscription(
            String, "chatter", lambda message: messages.append(message.data), 10
        )
        try:
            deadline = time.monotonic() + 10.0
            while len(messages) < 3 and time.monotonic() < deadline:
                remaining = max(0.0, deadline - time.monotonic())
                self.executor.spin_once(timeout_sec=min(0.1, remaining))
            self.assertGreaterEqual(len(messages), 3, "fewer than three topic messages arrived")
            counters = []
            for text in messages:
                match = re.fullmatch(r"Test: ([0-9]+)", text)
                self.assertIsNotNone(match, "publisher ignored the configured prefix")
                counters.append(int(match.group(1)))
            self.assertTrue(all(a < b for a, b in zip(counters, counters[1:])))
            proc_output.assertWaitFor('I heard: "Test: ', timeout=10.0)
        finally:
            self.node.destroy_subscription(subscription)

    def test_one_shot_client_succeeds_and_exits_zero(self):
        result = self.run_client(12, 30)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Result: 12 + 30 = 42", output)

    def test_client_missing_service_exits_one_with_bounded_discovery(self):
        result = self.run_client(1, 2, remap="/integration/unavailable_for_test", discovery="0.2")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        self.assertIn("unavailable after 0.2s", output)

    def test_client_response_timeout_exits_one(self):
        # A real DDS endpoint advertises the service, but this node has no
        # executor. No callback runs, so the client must honor its response bound.
        quiet_node = rclpy.create_node(
            "unspun_service_probe", namespace="/integration", context=self.context
        )
        service = quiet_node.create_service(
            AddTwoInts, "withheld_response", lambda request, response: response
        )
        try:
            result = self.run_client(1, 2, remap="/integration/withheld_response", response="0.2")
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 1, output)
            self.assertIn("no response from /integration/withheld_response after 0.2s", output)
        finally:
            quiet_node.destroy_service(service)
            quiet_node.destroy_node()

    def test_client_invalid_operands_exit_two(self):
        for operand in ("9223372036854775808", "-9223372036854775809", "not-an-integer"):
            with self.subTest(operand=operand):
                result = self.run_client(operand, 1)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("error:", result.stderr)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    def test_nodes_exit_cleanly(self, proc_info):
        assertExitCodes(proc_info, allowable_exit_codes=[0])
