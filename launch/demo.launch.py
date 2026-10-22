"""Launch both exercises with shared namespace and explicit configuration."""

from typing import List

from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description() -> LaunchDescription:
    arguments = {
        "namespace": ("", "Namespace shared by all four nodes."),
        "publish_period": ("0.5", "Message interval in seconds."),
        "prefix": ("Hello World: ", "Text before the counter."),
        "start_client": ("true", "Run one example addition request."),
        "a": ("2", "First signed 64-bit operand."),
        "b": ("3", "Second signed 64-bit operand."),
        "discovery_timeout": ("5.0", "Service discovery limit in seconds."),
        "request_timeout": ("5.0", "Service response limit in seconds."),
    }
    declarations = [
        DeclareLaunchArgument(name, default_value=default, description=description)
        for name, (default, description) in arguments.items()
    ]

    def include(filename: str, names: List[str]) -> IncludeLaunchDescription:
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("Calculator"),
                        "launch",
                        filename,
                    ]
                )
            ),
            launch_arguments={name: LaunchConfiguration(name) for name in names}.items(),
        )

    return LaunchDescription(
        declarations
        + [
            include("topics.launch.py", ["namespace", "publish_period", "prefix"]),
            include(
                "service.launch.py",
                [
                    "namespace",
                    "start_client",
                    "a",
                    "b",
                    "discovery_timeout",
                    "request_timeout",
                ],
            ),
        ]
    )
