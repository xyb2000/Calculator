"""The service's signed 64-bit, two's-complement arithmetic contract."""

INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
UINT64_MODULUS = 1 << 64


def validate_int64(value: int) -> int:
    """Reject implicit conversions and values outside the signed wire type."""
    if type(value) is not int:
        raise TypeError("operand must be an integer (bool is not supported)")
    if not INT64_MIN <= value <= INT64_MAX:
        raise ValueError(f"operand must be between {INT64_MIN} and {INT64_MAX}")
    return value


def parse_int64(text: str) -> int:
    """Parse a command-line operand, rejecting values outside the wire type."""
    value = int(text)
    return validate_int64(value)


def add_int64(a: int, b: int) -> int:
    """Add int64 operands, wrapping overflow into the signed int64 range.

    ROS validates serialized requests against their generated int64 wire types;
    the explicit checks below also protect direct Python callers.
    Python integers do not overflow, so the result is normalized explicitly before
    constructing the response. This also makes the contract testable without ROS.
    """
    validate_int64(a)
    validate_int64(b)
    return (a + b - INT64_MIN) % UINT64_MODULUS + INT64_MIN
