"""Type helper functions for configuration values."""

from typing import Union


def get_int_value(value: Union[str, int, list[str], None]) -> int:
    """Extract integer value from configuration, with validation."""
    if isinstance(value, int):
        return value
    if value is None:
        raise ValueError("Expected integer value, got None")
    raise ValueError(f"Expected integer, got {type(value).__name__}")


def get_optional_int_value(value: Union[str, int, list[str], None]) -> Union[int, None]:
    """Extract optional integer value from configuration."""
    if value is None or isinstance(value, int):
        return value
    raise ValueError(f"Expected integer or None, got {type(value).__name__}")


def get_list_value(value: Union[str, int, list[str], None]) -> list[str]:
    """Extract list[str] value from configuration."""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    raise ValueError(f"Expected list, got {type(value).__name__}")
