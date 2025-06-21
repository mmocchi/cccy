"""Pydantic models for data structures and configuration."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ComplexityResult(BaseModel):
    """Result of complexity analysis for a single function or method."""

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
    """Result of complexity analysis for a single file."""

    file_path: str
    functions: List[ComplexityResult] = Field(default_factory=list)
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

    def get_status(self, thresholds: Optional[dict] = None) -> str:
        """Return status based on complexity thresholds.

        Args:
            thresholds: Optional custom thresholds dict with structure:
                       {
                           "medium": {"cyclomatic": 5, "cognitive": 4},
                           "high": {"cyclomatic": 10, "cognitive": 7}
                       }

        Returns:
            Status string: "OK", "MEDIUM", or "HIGH"

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
        """Return status based on default complexity thresholds.

        This property is kept for backward compatibility.
        For configurable thresholds, use get_status() method.
        """
        return self.get_status()


class PyComplexSettings(BaseSettings):
    """Configuration settings for pycomplex."""

    max_complexity: Optional[int] = Field(
        None, ge=1, description="Maximum allowed cyclomatic complexity"
    )
    max_cognitive: Optional[int] = Field(
        None, ge=1, description="Maximum allowed cognitive complexity"
    )
    exclude: List[str] = Field(
        default_factory=list, description="File patterns to exclude from analysis"
    )
    include: List[str] = Field(
        default_factory=list, description="File patterns to include in analysis"
    )
    paths: List[str] = Field(
        default_factory=lambda: ["."], description="Default paths to analyze"
    )
    status_thresholds: dict = Field(
        default_factory=lambda: {
            "medium": {"cyclomatic": 5, "cognitive": 4},
            "high": {"cyclomatic": 10, "cognitive": 7},
        },
        description="Thresholds for status classification",
    )

    model_config = SettingsConfigDict(
        env_prefix="PYCOMPLEX_", case_sensitive=False, validate_assignment=True
    )

    @field_validator("status_thresholds")
    @classmethod
    def validate_status_thresholds(cls, v: dict) -> Dict[str, Dict[str, int]]:
        """Validate and merge status thresholds with defaults."""
        # Start with defaults
        defaults = {
            "medium": {"cyclomatic": 5, "cognitive": 4},
            "high": {"cyclomatic": 10, "cognitive": 7},
        }

        # Merge user input with defaults
        result = defaults.copy()
        for level in ["medium", "high"]:
            if level in v:
                for metric in ["cyclomatic", "cognitive"]:
                    if metric in v[level]:
                        if (
                            not isinstance(v[level][metric], int)
                            or v[level][metric] < 0
                        ):
                            raise ValueError(
                                f"{metric} threshold for {level} must be a non-negative integer"
                            )
                        result[level][metric] = v[level][metric]

        # Validate that high thresholds are >= medium thresholds
        for metric in ["cyclomatic", "cognitive"]:
            if result["high"][metric] < result["medium"][metric]:
                raise ValueError(f"High {metric} threshold must be >= medium threshold")

        return result

    @classmethod
    def from_toml_config(cls, config_data: dict) -> "PyComplexSettings":
        """Create settings from TOML configuration data.

        Args:
            config_data: Configuration data from pyproject.toml [tool.pycomplex] section

        Returns:
            PyComplexSettings instance

        """
        # Convert kebab-case keys to snake_case for Pydantic
        converted_data = {}
        for key, value in config_data.items():
            snake_key = key.replace("-", "_")
            converted_data[snake_key] = value

        return cls(**converted_data)

