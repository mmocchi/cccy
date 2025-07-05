"""Pydantic models for data structures and configuration."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ComplexityResult(BaseModel):
    """単一の関数またはメソッドの複雑度解析結果。"""

    name: str
    cyclomatic_complexity: int = Field(ge=0, description="Cyclomatic complexity score")
    cognitive_complexity: int = Field(ge=0, description="Cognitive complexity score")
    lineno: int = Field(gt=0, description="Line number where function starts")
    col_offset: int = Field(ge=0, description="Column offset where function starts")
    end_lineno: Optional[int] = Field(
        default=None, ge=0, description="Line number where function ends"
    )
    end_col_offset: Optional[int] = Field(
        default=None, ge=0, description="Column offset where function ends"
    )

    model_config = ConfigDict(validate_assignment=True)


class FileComplexityResult(BaseModel):
    """単一ファイルの複雑度解析結果。"""

    file_path: str
    functions: list[ComplexityResult] = Field(default_factory=list)
    total_cyclomatic: int = Field(
        ge=0, description="Sum of all function cyclomatic complexities"
    )
    total_cognitive: int = Field(
        ge=0, description="Sum of all function cognitive complexities"
    )
    max_cyclomatic: int = Field(
        ge=0, description="Maximum cyclomatic complexity in file"
    )
    max_cognitive: int = Field(ge=0, description="Maximum cognitive complexity in file")

    model_config = ConfigDict(validate_assignment=True)

    def get_status(self, thresholds: Optional[dict[str, dict[str, int]]] = None) -> str:
        """複雑度闾値に基づいてステータスを返します。

        Args:
            thresholds: オプションのカスタム闾値辞書。構造:
                       {
                           "medium": {"cyclomatic": 5, "cognitive": 4},
                           "high": {"cyclomatic": 10, "cognitive": 7}
                       }

        Returns:
            ステータス文字列: "OK"、"MEDIUM"、または"HIGH"

        """
        # Use default thresholds if none provided
        if thresholds is None:
            thresholds = {
                "medium": {"cyclomatic": 5, "cognitive": 4},
                "high": {"cyclomatic": 10, "cognitive": 7},
            }

        high_cyclomatic = thresholds["high"]["cyclomatic"]
        high_cognitive = thresholds["high"]["cognitive"]
        medium_cyclomatic = thresholds["medium"]["cyclomatic"]
        medium_cognitive = thresholds["medium"]["cognitive"]

        if self.max_cyclomatic > high_cyclomatic or self.max_cognitive > high_cognitive:
            return "HIGH"
        if (
            self.max_cyclomatic > medium_cyclomatic
            or self.max_cognitive > medium_cognitive
        ):
            return "MEDIUM"
        return "OK"

    @property
    def status(self) -> str:
        """デフォルトの複雑度闾値に基づいてステータスを返します。

        このプロパティは下位互換性のために保持されています。
        設定可能な闾値には、get_status()メソッドを使用してください。
        """
        return self.get_status()


class CccySettings(BaseSettings):
    """cccyの設定。"""

    max_complexity: Optional[int] = Field(
        None, ge=1, description="Maximum allowed cyclomatic complexity"
    )
    max_cognitive: Optional[int] = Field(
        None, ge=1, description="Maximum allowed cognitive complexity"
    )
    exclude: list[str] = Field(
        default_factory=list, description="File patterns to exclude from analysis"
    )
    include: list[str] = Field(
        default_factory=list, description="File patterns to include in analysis"
    )
    paths: list[str] = Field(
        default_factory=lambda: ["."], description="Default paths to analyze"
    )
    status_thresholds: dict[str, dict[str, int]] = Field(
        default_factory=lambda: {
            "medium": {"cyclomatic": 5, "cognitive": 4},
            "high": {"cyclomatic": 10, "cognitive": 7},
        },
        description="Thresholds for status classification",
    )

    model_config = SettingsConfigDict(
        env_prefix="CCCY_", case_sensitive=False, validate_assignment=True
    )

    @field_validator("status_thresholds")
    @classmethod
    def validate_status_thresholds(
        cls, v: dict[str, dict[str, int]]
    ) -> dict[str, dict[str, int]]:
        """ステータス闾値を検証し、デフォルトとマージします。"""
        defaults = cls._get_default_thresholds()
        result = cls._merge_thresholds_with_defaults(defaults, v)
        cls._validate_threshold_ordering(result)
        return result

    @classmethod
    def _get_default_thresholds(cls) -> dict[str, dict[str, int]]:
        """デフォルト闾値値を取得します。"""
        return {
            "medium": {"cyclomatic": 5, "cognitive": 4},
            "high": {"cyclomatic": 10, "cognitive": 7},
        }

    @classmethod
    def _merge_thresholds_with_defaults(
        cls, defaults: dict[str, dict[str, int]], user_input: dict[str, dict[str, int]]
    ) -> dict[str, dict[str, int]]:
        """ユーザー入力をデフォルト闾値とマージします。"""
        result = defaults.copy()
        for level in ["medium", "high"]:
            if level in user_input:
                cls._update_level_thresholds(result, user_input, level)
        return result

    @classmethod
    def _update_level_thresholds(
        cls,
        result: dict[str, dict[str, int]],
        user_input: dict[str, dict[str, int]],
        level: str,
    ) -> None:
        """特定のレベルの闾値を更新します。"""
        for metric in ["cyclomatic", "cognitive"]:
            if metric in user_input[level]:
                cls._validate_threshold_value(user_input[level][metric], metric, level)
                result[level][metric] = user_input[level][metric]

    @classmethod
    def _validate_threshold_value(cls, value: int, metric: str, level: str) -> None:
        """単一の闾値値を検証します。"""
        if not isinstance(value, int) or value < 0:
            raise ValueError(
                f"{metric} threshold for {level} must be a non-negative integer"
            )

    @classmethod
    def _validate_threshold_ordering(cls, result: dict[str, dict[str, int]]) -> None:
        """high闾値がmedium闾値以上であることを検証します。"""
        for metric in ["cyclomatic", "cognitive"]:
            if result["high"][metric] < result["medium"][metric]:
                raise ValueError(f"High {metric} threshold must be >= medium threshold")

    @classmethod
    def from_toml_config(cls, config_data: dict[str, Any]) -> "CccySettings":
        """TOML設定データから設定を作成します。

        Args:
            config_data: pyproject.toml [tool.cccy]セクションからの設定データ

        Returns:
            CccySettingsインスタンス

        """
        # Convert kebab-case keys to snake_case for Pydantic
        converted_data: dict[str, Any] = {}
        for key, value in config_data.items():
            snake_key = key.replace("-", "_")
            converted_data[snake_key] = value

        return cls(**converted_data)
