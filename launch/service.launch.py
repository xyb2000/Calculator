"""Launch the addition server and, optionally, one bounded client request."""

from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration("namespace")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "namespace", default_value="", description="Namespace shared by both nodes."
            ),
            DeclareLaunchArgument(
                "start_client", default_value="true", description="Run one example request."
            ),
            DeclareLaunchArgument("a", default_value="2", description="First int64 operand."),
            DeclareLaunchArgument("b", default_value="3", description="Second int64 operand."),
            DeclareLaunchArgument(
                "discovery_timeout", default_value="5.0", description="Service discovery limit."
            ),
            DeclareLaunchArgument(
                "request_timeout", default_value="5.0", description="Service response limit."
            ),
            Node(
                package="Calculator",
                executable="add_two_ints_server",
                namespace=namespace,
                output="screen",
            ),
            Node(
                package="Calculator",
                executable="add_two_ints_client",
                namespace=namespace,
                output="screen",
                condition=IfCondition(LaunchConfiguration("start_client")),
                arguments=[
                    LaunchConfiguration("a"),
                    LaunchConfiguration("b"),
                    "--discovery-timeout",
                    LaunchConfiguration("discovery_timeout"),
                    "--request-timeout",
                    LaunchConfiguration("request_timeout"),
                ],
            ),
        ]
    )
