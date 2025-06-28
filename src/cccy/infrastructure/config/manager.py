"""Configuration management for cccy."""

from pathlib import Path
from typing import Optional, Union

from pydantic import ValidationError

from cccy.domain.entities.complexity import CccySettings
from cccy.infrastructure.config.loaders import ConfigLoaderFactory
from cccy.infrastructure.config.merger import ConfigMerger, ConfigValidator


class CccyConfig:
    """cccyの設定ローダー。"""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """設定ローダーを初期化します。

        Args:
            config_path: pyproject.tomlファイルのパス。Noneの場合は検索します。

        """
        self.config_path = config_path or self._find_config_file()
        self._settings: Optional[CccySettings] = None

    def _find_config_file(self) -> Optional[Path]:
        """現在のディレクトリまたは親ディレクトリでpyproject.tomlファイルを検索します。"""
        current_dir = Path.cwd()

        # Look in current directory and parents
        for path in [current_dir, *current_dir.parents]:
            pyproject_path = path / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path

        return None

    def _load_config(self) -> dict[str, object]:
        """pyproject.tomlファイルから設定を読み込みます。"""
        if not self.config_path:
            return {}

        loader = ConfigLoaderFactory.create_loader()
        return loader.load_config(self.config_path)

    def _get_settings(self) -> CccySettings:
        """Pydantic設定インスタンスを取得します。"""
        if self._settings is None:
            config_data = self._load_config()
            try:
                self._settings = CccySettings.from_toml_config(config_data)
            except ValidationError as e:
                # Convert validation error to user-friendly message
                raise ValueError(f"Configuration error in pyproject.toml: {e}") from e
        return self._settings

    def get_max_complexity(self) -> Optional[int]:
        """最大循環的複雑度闾値を取得します。"""
        return self._get_settings().max_complexity

    def get_max_cognitive(self) -> Optional[int]:
        """最大認知的複雑度闾値を取得します。"""
        return self._get_settings().max_cognitive

    def get_exclude_patterns(self) -> list[str]:
        """除外するファイルパターンを取得します。"""
        return self._get_settings().exclude

    def get_include_patterns(self) -> list[str]:
        """含めるファイルパターンを取得します。"""
        return self._get_settings().include

    def get_default_paths(self) -> list[str]:
        """解析するデフォルトパスを取得します。"""
        return self._get_settings().paths

    def get_status_thresholds(self) -> dict[str, dict[str, int]]:
        """ステータス分類闾値を取得します。"""
        return self._get_settings().status_thresholds

    def merge_with_cli_options(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[list[str]] = None,
        include: Optional[list[str]] = None,
        paths: Optional[list[str]] = None,
    ) -> dict[str, Union[str, int, list[str], None]]:
        """設定をCLIオプションとマージし、CLIが優先されます。"""
        settings = self._get_settings()
        merger = ConfigMerger(settings)
        merged_config = merger.merge_with_cli_options(
            max_complexity=max_complexity,
            max_cognitive=max_cognitive,
            exclude=exclude,
            include=include,
            paths=paths,
        )

        # 設定値の検証
        max_complexity_val = merged_config["max_complexity"]
        max_cognitive_val = merged_config["max_cognitive"]
        paths_val = merged_config["paths"]

        max_complexity_typed = (
            max_complexity_val
            if isinstance(max_complexity_val, (int, type(None)))
            else None
        )
        max_cognitive_typed = (
            max_cognitive_val
            if isinstance(max_cognitive_val, (int, type(None)))
            else None
        )

        ConfigValidator.validate_complexity_thresholds(
            max_complexity_typed, max_cognitive_typed
        )

        if paths_val and isinstance(paths_val, list):
            ConfigValidator.validate_paths(paths_val)

        return merged_config
