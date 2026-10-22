"""Validate client inputs without importing or mocking ROS."""

import argparse
import contextlib
import io
import unittest

from calculator.arithmetic import INT64_MAX, INT64_MIN
from calculator.cli import build_parser, parse_int64, parse_positive_seconds


class TestClientArguments(unittest.TestCase):
    def test_int64_limits_and_decimal_values(self):
        for value in (0, -1, 42, INT64_MIN, INT64_MAX):
            self.assertEqual(parse_int64(str(value)), value)

    def test_reject_out_of_range_operands(self):
        for value in (INT64_MIN - 1, INT64_MAX + 1):
            with self.assertRaises(argparse.ArgumentTypeError):
                parse_int64(str(value))

    def test_reject_noninteger_operands(self):
        for value in ("1.5", "word", "", "0xff"):
            with self.assertRaises(argparse.ArgumentTypeError):
                parse_int64(value)

    def test_accept_positive_timeout(self):
        self.assertEqual(parse_positive_seconds("0.05"), 0.05)

    def test_reject_invalid_timeout(self):
        for value in ("0", "-1", "nan", "inf", "-inf", "word"):
            with self.assertRaises(argparse.ArgumentTypeError):
                parse_positive_seconds(value)

    def test_default_timeouts(self):
        options = build_parser().parse_args(["-2", "3"])
        self.assertEqual((options.a, options.b), (-2, 3))
        self.assertEqual(options.discovery_timeout, 5.0)
        self.assertEqual(options.request_timeout, 5.0)

    def test_custom_timeouts(self):
        options = build_parser().parse_args(
            ["2", "3", "--discovery-timeout", "2", "--request-timeout", "0.5"]
        )
        self.assertEqual((options.discovery_timeout, options.request_timeout), (2, 0.5))

    def test_invalid_cli_exits_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                build_parser().parse_args(["bad", "3"])
        self.assertEqual(raised.exception.code, 2)
