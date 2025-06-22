"""設定値のためのタイプヘルパー関数。"""

from typing import Union


def get_int_value(value: Union[str, int, list[str], None]) -> int:
    """設定から整数値を検証付きで抽出します。"""
    if isinstance(value, int):
        return value
    if value is None:
        raise ValueError("Expected integer value, got None")
    raise ValueError(f"Expected integer, got {type(value).__name__}")


def get_optional_int_value(value: Union[str, int, list[str], None]) -> Union[int, None]:
    """設定からオプションの整数値を抽出します。"""
    if value is None or isinstance(value, int):
        return value
    raise ValueError(f"Expected integer or None, got {type(value).__name__}")


def get_list_value(value: Union[str, int, list[str], None]) -> list[str]:
    """設定からlist[str]値を抽出します。"""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    raise ValueError(f"Expected list, got {type(value).__name__}")
