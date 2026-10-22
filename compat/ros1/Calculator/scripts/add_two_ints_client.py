#!/usr/bin/env python3
"""Call the addition service once; unavailable services produce a nonzero exit."""

import argparse
import math
import sys

import rospy

from Calculator.srv import AddTwoInts
from calculator_legacy.arithmetic import parse_int64


def positive_timeout(text: str) -> float:
    value = float(text)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("timeout must be a finite positive number")
    return value


def int64_operand(text: str) -> int:
    try:
        return parse_int64(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("a", type=int64_operand)
    parser.add_argument("b", type=int64_operand)
    parser.add_argument(
        "--timeout",
        type=positive_timeout,
        default=5.0,
        help="service discovery timeout in seconds (default: 5)",
    )
    args = parser.parse_args(rospy.myargv()[1:])
    rospy.init_node("add_two_ints_client", anonymous=True)
    try:
        rospy.wait_for_service("add_two_ints", timeout=args.timeout)
        add_two_ints = rospy.ServiceProxy("add_two_ints", AddTwoInts)
        response = add_two_ints(args.a, args.b)
    except (rospy.ROSException, rospy.ServiceException) as error:
        rospy.logerr("add_two_ints request failed: %s", error)
        return 1
    print(response.sum)
    return 0


if __name__ == "__main__":
    sys.exit(main())
