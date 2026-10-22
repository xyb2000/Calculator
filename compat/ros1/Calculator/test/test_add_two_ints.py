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

    def assert_sum(self, a: int, b: int, expected: int) -> None:
        # Explicit expectations do not reuse the implementation's helper.
        response = self.add_two_ints(a, b)
        self.assertEqual(response.sum, expected)

    def test_positive(self) -> None:
        self.assert_sum(1, 2, 3)

    def test_zero(self) -> None:
        self.assert_sum(0, 0, 0)

    def test_negative(self) -> None:
        self.assert_sum(-7, -9, -16)

    def test_mixed_signs(self) -> None:
        self.assert_sum(-7, 9, 2)

    def test_large_values(self) -> None:
        self.assert_sum(123456789, 987654321, 1111111110)

    def test_maximum(self) -> None:
        self.assert_sum(9223372036854775807, 0, 9223372036854775807)

    def test_minimum(self) -> None:
        self.assert_sum(-9223372036854775808, 0, -9223372036854775808)

    def test_opposite_limits(self) -> None:
        self.assert_sum(9223372036854775807, -9223372036854775808, -1)

    def test_positive_overflow(self) -> None:
        self.assert_sum(9223372036854775807, 1, -9223372036854775808)

    def test_negative_overflow(self) -> None:
        self.assert_sum(-9223372036854775808, -1, 9223372036854775807)

    def test_maximum_plus_maximum(self) -> None:
        self.assert_sum(9223372036854775807, 9223372036854775807, -2)

    def test_minimum_plus_minimum(self) -> None:
        self.assert_sum(-9223372036854775808, -9223372036854775808, 0)

    def test_topic_smoke(self) -> None:
        message = rospy.wait_for_message("chatter", String, timeout=10.0)
        self.assertRegex(message.data, r"^hello world [0-9]+$")


if __name__ == "__main__":
    rospy.init_node("calculator_integration_test", anonymous=True)
    rostest.rosrun("Calculator", "calculator_integration", CalculatorIntegrationTest)
