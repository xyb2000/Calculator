#!/usr/bin/env python3
"""Serve signed int64 addition, including deterministic overflow wrapping."""

import rospy

from Calculator.srv import AddTwoInts, AddTwoIntsRequest, AddTwoIntsResponse
from calculator_legacy.arithmetic import add_int64


def handle_add_two_ints(request: AddTwoIntsRequest) -> AddTwoIntsResponse:
    result = add_int64(request.a, request.b)
    rospy.loginfo("add_two_ints: %d + %d = %d", request.a, request.b, result)
    return AddTwoIntsResponse(sum=result)


def main() -> None:
    rospy.init_node("add_two_ints_server")
    service = rospy.Service("add_two_ints", AddTwoInts, handle_add_two_ints)
    rospy.loginfo("Ready on %s", service.resolved_name)
    rospy.spin()


if __name__ == "__main__":
    main()
