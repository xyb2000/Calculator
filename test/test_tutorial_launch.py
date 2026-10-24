"""Exercise the installed tutorial launch through real turtlesim interfaces."""

# Pure Python runs skip ROS; an installed ROS environment must have all dependencies.
# ruff: noqa: E402

import time
import unittest
from functools import partial
from pathlib import Path

import pytest

rclpy = pytest.importorskip("rclpy")
launch = pytest.importorskip("launch")
launch_testing = pytest.importorskip("launch_testing")

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from launch_testing.actions import ReadyToTest
from launch_testing.asserts import assertExitCodes
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from std_srvs.srv import Empty
from turtlesim.msg import Pose

from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource


@pytest.mark.launch_test
def generate_test_description():
    tutorial = Path(get_package_share_directory("Calculator")) / "launch" / "multisim.launch.py"
    return launch.LaunchDescription(
        [
            # Use real Qt nodes without requiring an X server in CI containers.
            SetEnvironmentVariable("QT_QPA_PLATFORM", "offscreen"),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(str(tutorial))),
            ReadyToTest(),
        ]
    )


class TestTutorialLaunch(unittest.TestCase):
    namespaces = ("turtlesim1", "turtlesim2")

    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        rclpy.init(args=[], context=cls.context)
        cls.addClassCleanup(rclpy.try_shutdown, context=cls.context)
        cls.node = rclpy.create_node("tutorial_launch_probe", context=cls.context)
        cls.addClassCleanup(cls.node.destroy_node)
        cls.executor = SingleThreadedExecutor(context=cls.context)
        cls.executor.add_node(cls.node)
        cls.addClassCleanup(cls.executor.shutdown, timeout_sec=2.0)
        cls.poses = {}
        cls.samples = dict.fromkeys(cls.namespaces, 0)
        cls.publishers = {}
        cls.reset_clients = {}
        for namespace in cls.namespaces:
            cls.node.create_subscription(
                Pose, f"/{namespace}/turtle1/pose", partial(cls._record_pose, namespace), 10
            )
            cls.publishers[namespace] = cls.node.create_publisher(
                Twist, f"/{namespace}/turtle1/cmd_vel", 10
            )
            cls.reset_clients[namespace] = cls.node.create_client(Empty, f"/{namespace}/reset")
            if not cls.reset_clients[namespace].wait_for_service(timeout_sec=10.0):
                raise AssertionError(f"/{namespace}/reset was not discovered within 10s")
        cls._wait_until(lambda: len(cls.poses) == 2, "both turtles must publish their pose")

    @classmethod
    def _record_pose(cls, namespace, message):
        cls.poses[namespace] = message
        cls.samples[namespace] += 1

    @classmethod
    def _wait_until(cls, predicate, description, timeout=5.0):
        deadline = time.monotonic() + timeout
        while not predicate():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AssertionError(description)
            cls.executor.spin_once(timeout_sec=min(0.05, remaining))

    def _reset_turtles(self):
        futures = [client.call_async(Empty.Request()) for client in self.reset_clients.values()]
        self._wait_until(lambda: all(future.done() for future in futures), "reset timed out")
        for future in futures:
            self.assertIsNone(future.exception())
            self.assertIsNotNone(future.result())
        self.poses.clear()
        self._wait_until(lambda: len(self.poses) == 2, "poses missing after reset")

    def _drive_until(self, commands, predicate, description):
        def publish_commands():
            for namespace, command in commands.items():
                self.publishers[namespace].publish(command)

        timer = self.node.create_timer(0.05, publish_commands)
        try:
            self._wait_until(predicate, description)
        finally:
            self.node.destroy_timer(timer)
            for publisher in self.publishers.values():
                publisher.publish(Twist())

    def test_nodes_have_the_tutorial_namespaces(self):
        expected = {("turtlesim", "/turtlesim1"), ("turtlesim", "/turtlesim2")}
        self._wait_until(
            lambda: expected.issubset(set(self.node.get_node_names_and_namespaces())),
            "the two namespaced turtlesim nodes were not discovered",
        )

    def test_both_pose_topics_have_publishers(self):
        for namespace in self.namespaces:
            self.assertGreaterEqual(self.node.count_publishers(f"/{namespace}/turtle1/pose"), 1)

    def test_command_to_first_namespace_does_not_move_second(self):
        self._reset_turtles()
        first_x = self.poses["turtlesim1"].x
        second = self.poses["turtlesim2"]
        second_samples = self.samples["turtlesim2"]
        command = Twist()
        command.linear.x = 1.0
        self._drive_until(
            {"turtlesim1": command},
            lambda: self.poses["turtlesim1"].x > first_x + 0.25
            and self.samples["turtlesim2"] > second_samples + 1,
            "the first turtle did not move while the second kept publishing",
        )
        self.assertAlmostEqual(self.poses["turtlesim2"].x, second.x, places=3)
        self.assertAlmostEqual(self.poses["turtlesim2"].y, second.y, places=3)
        self.assertAlmostEqual(self.poses["turtlesim2"].theta, second.theta, places=3)

    def test_tutorial_commands_rotate_turtles_in_opposite_directions(self):
        self._reset_turtles()
        commands = {}
        for namespace, angular_speed in zip(self.namespaces, (1.8, -1.8)):
            command = Twist()
            command.linear.x = 2.0
            command.angular.z = angular_speed
            commands[namespace] = command
        self._drive_until(
            commands,
            lambda: self.poses["turtlesim1"].theta > 0.15
            and self.poses["turtlesim2"].theta < -0.15,
            "the tutorial velocity commands did not produce opposite rotations",
        )


@launch_testing.post_shutdown_test()
class TestTutorialShutdown(unittest.TestCase):
    def test_turtlesim_nodes_exit_cleanly(self, proc_info):
        assertExitCodes(proc_info, allowable_exit_codes=[0])
