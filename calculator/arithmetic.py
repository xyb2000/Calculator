"""ROS-independent arithmetic with an explicit signed 64-bit wire contract.

AddTwoInts has no error field, so sums wrap using two's complement arithmetic.
For example INT64_MAX + 1 returns INT64_MIN. Operands outside the wire type
are rejected before computation. No ROS imports are required to test this module.
"""

INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
_MODULUS = 1 << 64


def validate_int64(value: int) -> int:
    """Return an integer that fits the service type; reject bools and coercion."""
    if type(value) is not int:
        raise TypeError("operand must be an integer (bool is not supported)")
    if not INT64_MIN <= value <= INT64_MAX:
        raise ValueError(f"operand must be between {INT64_MIN} and {INT64_MAX}")
    return value


def add_int64(a: int, b: int) -> int:
    """Add two int64 operands, wrapping the result into the signed int64 range."""
    validate_int64(a)
    validate_int64(b)
    return (a + b - INT64_MIN) % _MODULUS + INT64_MIN
