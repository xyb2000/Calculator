#!/usr/bin/env python3
"""Receive and log strings from the relative chatter topic."""

import rospy
from std_msgs.msg import String


def handle_message(message: String) -> None:
    rospy.loginfo("Received: %s", message.data)


def main() -> None:
    rospy.init_node("listener")
    subscriber = rospy.Subscriber("chatter", String, handle_message, queue_size=10)
    rospy.loginfo("Listening on %s", subscriber.resolved_name)
    rospy.spin()


if __name__ == "__main__":
    main()
