#!/usr/bin/env python3
"""Publish a readable sequence of strings on the relative chatter topic."""

import math

import rospy
from std_msgs.msg import String


def main() -> None:
    rospy.init_node("talker")
    rate_hz = float(rospy.get_param("~rate_hz", 10.0))
    if not math.isfinite(rate_hz) or rate_hz <= 0:
        raise ValueError("~rate_hz must be a finite positive number")
    publisher = rospy.Publisher("chatter", String, queue_size=10)
    rate = rospy.Rate(rate_hz)
    sequence = 0
    while not rospy.is_shutdown():
        message = String(data=f"hello world {sequence}")
        publisher.publish(message)
        rospy.loginfo("Published: %s", message.data)
        sequence += 1
        rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
