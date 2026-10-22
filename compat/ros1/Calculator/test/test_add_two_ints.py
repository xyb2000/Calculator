#!/usr/bin/env python3
"""Exercise actual service round trips and the live topic under rostest."""

import unittest

import rospy
import rostest
from std_msgs.msg import String

from Calculator.srv import AddTwoInts


class CalculatorIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rospy.wait_for_service("add_two_ints", timeout=10.0)
        cls.add_two_ints = rospy.ServiceProxy("add_two_ints", AddTwoInts)

    def test_service_round_trips(self) -> None:
        # Expected values are explicit so the test does not duplicate the helper.
        cases = [
            (1, 2, 3),
            (0, 0, 0),
            (-7, -9, -16),
            (-7, 9, 2),
            (123456789, 987654321, 1111111110),
            (9223372036854775807, 0, 9223372036854775807),
            (-9223372036854775808, 0, -9223372036854775808),
            (9223372036854775807, -9223372036854775808, -1),
            (9223372036854775807, 1, -9223372036854775808),
            (-9223372036854775808, -1, 9223372036854775807),
            (9223372036854775807, 9223372036854775807, -2),
            (-9223372036854775808, -9223372036854775808, 0),
        ]
        for a, b, expected in cases:
            with self.subTest(a=a, b=b):
                response = self.add_two_ints(a, b)
                self.assertEqual(response.sum, expected)

    def test_topic_smoke(self) -> None:
        message = rospy.wait_for_message("chatter", String, timeout=10.0)
        self.assertRegex(message.data, r"^hello world [0-9]+$")


if __name__ == "__main__":
    rospy.init_node("calculator_integration_test", anonymous=True)
    rostest.rosrun("Calculator", "calculator_integration", CalculatorIntegrationTest)
