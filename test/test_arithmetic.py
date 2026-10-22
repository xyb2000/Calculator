"""Boundary and algebraic tests independent of ROS middleware."""

import random
import unittest

from calculator.arithmetic import INT64_MAX, INT64_MIN, add_int64, validate_int64


class TestArithmetic(unittest.TestCase):
    def test_positive_operands(self):
        self.assertEqual(add_int64(2, 3), 5)

    def test_zero_identity(self):
        self.assertEqual(add_int64(0, 0), 0)
        self.assertEqual(add_int64(42, 0), 42)

    def test_negative_operands(self):
        self.assertEqual(add_int64(-7, -9), -16)

    def test_mixed_signs(self):
        self.assertEqual(add_int64(-7, 12), 5)
        self.assertEqual(add_int64(7, -12), -5)

    def test_cancellation(self):
        self.assertEqual(add_int64(123456, -123456), 0)

    def test_exact_limits(self):
        self.assertEqual(add_int64(INT64_MAX - 1, 1), INT64_MAX)
        self.assertEqual(add_int64(INT64_MIN + 1, -1), INT64_MIN)

    def test_positive_overflow_wraps(self):
        self.assertEqual(add_int64(INT64_MAX, 1), INT64_MIN)
        self.assertEqual(add_int64(INT64_MAX, INT64_MAX), -2)

    def test_negative_overflow_wraps(self):
        self.assertEqual(add_int64(INT64_MIN, -1), INT64_MAX)
        self.assertEqual(add_int64(INT64_MIN, INT64_MIN), 0)

    def test_opposite_limits(self):
        self.assertEqual(add_int64(INT64_MIN, INT64_MAX), -1)

    def test_operand_range_validation(self):
        for value in (INT64_MIN - 1, INT64_MAX + 1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    add_int64(value, 0)
                with self.assertRaises(ValueError):
                    add_int64(0, value)

    def test_operand_type_validation(self):
        for value in (True, False, None, "3", 3.0, [], {}):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    add_int64(value, 0)
                with self.assertRaises(TypeError):
                    add_int64(0, value)

    def test_validator_returns_boundary_values(self):
        self.assertEqual(validate_int64(INT64_MIN), INT64_MIN)
        self.assertEqual(validate_int64(INT64_MAX), INT64_MAX)

    def test_seeded_algebraic_properties(self):
        """An independent bit-mask oracle checks 1,000 reproducible input pairs."""
        rng = random.Random(20261022)
        for _ in range(1000):
            a = rng.randint(INT64_MIN, INT64_MAX)
            b = rng.randint(INT64_MIN, INT64_MAX)
            unsigned = (a + b) & ((1 << 64) - 1)
            expected = unsigned if unsigned < 1 << 63 else unsigned - (1 << 64)
            self.assertEqual(add_int64(a, b), expected)
            self.assertEqual(add_int64(a, b), add_int64(b, a))
            self.assertEqual(add_int64(a, 0), a)
