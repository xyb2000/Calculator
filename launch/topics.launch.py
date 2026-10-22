"""Launch the greeting publisher and subscriber in one namespace."""

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration("namespace")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "namespace", default_value="", description="Namespace shared by both nodes."
            ),
            DeclareLaunchArgument(
                "publish_period", default_value="0.5", description="Message interval in seconds."
            ),
            DeclareLaunchArgument(
                "prefix", default_value="Hello World: ", description="Text before the counter."
            ),
            Node(
                package="Calculator",
                executable="talker",
                namespace=namespace,
                output="screen",
                parameters=[
                    {
                        "publish_period": ParameterValue(
                            LaunchConfiguration("publish_period"), value_type=float
                        ),
                        "prefix": ParameterValue(LaunchConfiguration("prefix"), value_type=str),
                    }
                ],
            ),
            Node(
                package="Calculator",
                executable="listener",
                namespace=namespace,
                output="screen",
            ),
        ]
    )
