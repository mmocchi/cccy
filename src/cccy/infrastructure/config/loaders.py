"""Configuration loading strategies."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol


class TomlLoader(Protocol):
    """TOML読み込み機能のプロトコル。"""

    def load(self, fp: object) -> dict[str, object]:
        """ファイルポインターからTOMLデータを読み込みます。"""
        ...


class ConfigLoadingStrategy(ABC):
    """設定読み込み戦略の抽象基底クラス。"""

    @abstractmethod
    def load_config(self, config_path: Path) -> dict[str, object]:
        """設定ファイルから設定を読み込みます。

        Args:
            config_path: 設定ファイルのパス

        Returns:
            読み込まれた設定辞書

        """
        pass


class TomlLibConfigLoader(ConfigLoadingStrategy):
    """Python 3.11+ の標準 tomllib を使用するローダー。"""

    def __init__(self) -> None:
        """ローダーを初期化します。"""
        try:
            import tomllib  # noqa: PLC0415

            self.toml_loader: TomlLoader = tomllib
        except ImportError as e:
            raise ImportError("tomllib is not available") from e

    def load_config(self, config_path: Path) -> dict[str, object]:
        """Tomlllib を使用して設定を読み込みます。"""
        if not config_path.exists():
            return {}

        try:
            with config_path.open("rb") as f:
                config_data = self.toml_loader.load(f)
                return self._extract_cccy_config(config_data)
        except Exception:
            return {}

    def _extract_cccy_config(self, config_data: dict) -> dict[str, object]:
        """設定データからcccy設定を抽出します。"""
        tool_config = config_data.get("tool", {})
        if isinstance(tool_config, dict):
            cccy_config = tool_config.get("cccy", {})
            if isinstance(cccy_config, dict):
                return cccy_config
        return {}


class TomliConfigLoader(ConfigLoadingStrategy):
    """tomli ライブラリを使用するローダー (Python < 3.11)。"""

    def __init__(self) -> None:
        """ローダーを初期化します。"""
        try:
            import tomli  # noqa: PLC0415

            self.toml_loader: TomlLoader = tomli
        except ImportError as e:
            raise ImportError("tomli is not available") from e

    def load_config(self, config_path: Path) -> dict[str, object]:
        """Tomli を使用して設定を読み込みます。"""
        if not config_path.exists():
            return {}

        try:
            with config_path.open("rb") as f:
                config_data = self.toml_loader.load(f)
                return self._extract_cccy_config(config_data)
        except Exception:
            return {}

    def _extract_cccy_config(self, config_data: dict) -> dict[str, object]:
        """設定データからcccy設定を抽出します。"""
        tool_config = config_data.get("tool", {})
        if isinstance(tool_config, dict):
            cccy_config = tool_config.get("cccy", {})
            if isinstance(cccy_config, dict):
                return cccy_config
        return {}


class NoTomlConfigLoader(ConfigLoadingStrategy):
    """TOML パーサーが利用できない場合のフォールバックローダー。"""

    def load_config(self, config_path: Path) -> dict[str, object]:  # noqa: ARG002
        """空の設定を返します(TOMLパーサーが利用できないため)。"""
        return {}


class ConfigLoaderFactory:
    """設定ローダーを作成するファクトリー。"""

    @staticmethod
    def create_loader() -> ConfigLoadingStrategy:
        """利用可能なTOMLライブラリに基づいてローダーを作成します。

        Returns:
            適切な設定ローダーインスタンス

        """
        # Python 3.11+ の標準 tomllib を優先
        try:
            return TomlLibConfigLoader()
        except ImportError:
            pass

        # Python < 3.11 の tomli をフォールバック
        try:
            return TomliConfigLoader()
        except ImportError:
            pass

        # どちらも利用できない場合はフォールバックローダー
        return NoTomlConfigLoader()
