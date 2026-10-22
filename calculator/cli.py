"""Pure command-line validation, kept independent of the ROS runtime."""

import argparse
import math

from calculator.arithmetic import INT64_MAX, INT64_MIN


def parse_int64(text: str) -> int:
    """Parse a decimal integer that fits the AddTwoInts wire format."""
    try:
        value = int(text, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a decimal integer") from exc
    if not INT64_MIN <= value <= INT64_MAX:
        raise argparse.ArgumentTypeError(f"must be between {INT64_MIN} and {INT64_MAX}")
    return value


def parse_positive_seconds(text: str) -> float:
    """Reject non-finite or non-positive timeout values."""
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number of seconds") from exc
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return value


def build_parser() -> argparse.ArgumentParser:
    """Build the one-shot addition client parser."""
    parser = argparse.ArgumentParser(
        description="Add two signed 64-bit integers using the add_two_ints service.",
        epilog="Overflow wraps to signed int64. ROS options follow --ros-args.",
    )
    parser.add_argument("a", type=parse_int64, help="first signed 64-bit operand")
    parser.add_argument("b", type=parse_int64, help="second signed 64-bit operand")
    parser.add_argument(
        "--discovery-timeout",
        type=parse_positive_seconds,
        default=5.0,
        metavar="SECONDS",
        help="maximum time to wait for service discovery (default: 5)",
    )
    parser.add_argument(
        "--request-timeout",
        type=parse_positive_seconds,
        default=5.0,
        metavar="SECONDS",
        help="maximum time to wait for a response (default: 5)",
    )
    return parser
