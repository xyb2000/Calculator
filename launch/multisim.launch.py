# SPDX-License-Identifier: CC-BY-4.0
"""Reproduce the Humble tutorial's two namespaced turtlesim nodes.

Adapted from ros2/ros2_documentation; only formatting, this attribution and
the return annotation were added. See THIRD_PARTY_NOTICES.md for the source.
"""

import launch_ros.actions

from launch import LaunchDescription


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            launch_ros.actions.Node(
                namespace="turtlesim1",
                package="turtlesim",
                executable="turtlesim_node",
                output="screen",
            ),
            launch_ros.actions.Node(
                namespace="turtlesim2",
                package="turtlesim",
                executable="turtlesim_node",
                output="screen",
            ),
        ]
    )
