"""Configuration merging and processing utilities."""

from typing import Optional, Union

from cccy.domain.entities.complexity import CccySettings


class ConfigMerger:
    """設定のマージとCLIオプションとの統合を処理するクラス。"""

    def __init__(self, settings: CccySettings) -> None:
        """設定マージャーを初期化します。

        Args:
            settings: ベースとなる設定オブジェクト

        """
        self.settings = settings

    def merge_with_cli_options(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[list[str]] = None,
        include: Optional[list[str]] = None,
        paths: Optional[list[str]] = None,
    ) -> dict[str, Union[str, int, list[str], None]]:
        """設定をCLIオプションとマージし、CLIが優先されます。

        Args:
            max_complexity: CLIで指定された最大循環的複雑度
            max_cognitive: CLIで指定された最大認知的複雑度
            exclude: CLIで指定された除外パターン
            include: CLIで指定された包含パターン
            paths: CLIで指定されたパス

        Returns:
            マージされた設定辞書

        """
        return {
            "max_complexity": self._merge_value(
                max_complexity, self.settings.max_complexity
            ),
            "max_cognitive": self._merge_value(
                max_cognitive, self.settings.max_cognitive
            ),
            "exclude": self._merge_list(exclude, self.settings.exclude),
            "include": self._merge_list(include, self.settings.include),
            "paths": self._merge_list(paths, self.settings.paths),
        }

    def _merge_value(
        self, cli_value: Optional[int], config_value: Optional[int]
    ) -> Optional[int]:
        """単一値のマージを処理します(CLIが優先)。

        Args:
            cli_value: CLIからの値
            config_value: 設定ファイルからの値

        Returns:
            マージされた値

        """
        return cli_value if cli_value is not None else config_value

    def _merge_list(
        self, cli_list: Optional[list[str]], config_list: list[str]
    ) -> list[str]:
        """リスト値のマージを処理します(CLIが優先)。

        Args:
            cli_list: CLIからのリスト
            config_list: 設定ファイルからのリスト

        Returns:
            マージされたリスト

        """
        return list(cli_list) if cli_list else config_list


class ConfigValidator:
    """設定の検証を行うクラス。"""

    @staticmethod
    def validate_complexity_thresholds(
        max_complexity: Optional[int], max_cognitive: Optional[int]
    ) -> None:
        """複雑度閾値の妥当性を検証します。

        Args:
            max_complexity: 最大循環的複雑度
            max_cognitive: 最大認知的複雑度

        Raises:
            ValueError: 閾値が無効な場合

        """
        if max_complexity is not None and max_complexity < 1:
            raise ValueError(f"max_complexity must be >= 1, got {max_complexity}")

        if max_cognitive is not None and max_cognitive < 0:
            raise ValueError(f"max_cognitive must be >= 0, got {max_cognitive}")

    @staticmethod
    def validate_paths(paths: list[str]) -> None:
        """パスの妥当性を検証します。

        Args:
            paths: 検証するパスのリスト

        Raises:
            ValueError: パスが無効な場合

        """
        if not paths:
            raise ValueError("At least one path must be specified")

        for path in paths:
            if not path.strip():
                raise ValueError("Empty path is not allowed")
