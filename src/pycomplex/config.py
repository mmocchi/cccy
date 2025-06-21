"""Configuration management for pycomplex."""

from pathlib import Path
from typing import Optional, Protocol, Union

from pydantic import ValidationError

from .models import PyComplexSettings


class TomlLoader(Protocol):
    """Protocol for TOML loading functionality."""

    def load(self, fp: object) -> dict[str, object]:
        """Load TOML data from file pointer."""
        ...


try:
    import tomllib

    toml_loader: Optional[TomlLoader] = tomllib
except ImportError:
    # Python < 3.11
    try:
        import tomli

        toml_loader = tomli  # type: ignore[assignment]
    except ImportError:
        toml_loader = None


class PyComplexConfig:
    """Configuration loader for pycomplex."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize configuration loader.

        Args:
            config_path: Path to pyproject.toml file. If None, searches for it.

        """
        self.config_path = config_path or self._find_config_file()
        self._settings: Optional[PyComplexSettings] = None

    def _find_config_file(self) -> Optional[Path]:
        """Find pyproject.toml file in current directory or parent directories."""
        current_dir = Path.cwd()

        # Look in current directory and parents
        for path in [current_dir, *current_dir.parents]:
            pyproject_path = path / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path

        return None

    def _load_config(self) -> dict[str, object]:
        """Load configuration from pyproject.toml file."""
        if not self.config_path or not self.config_path.exists():
            return {}

        if toml_loader is None:
            # No TOML parser available, return empty config
            return {}

        try:
            with self.config_path.open("rb") as f:
                config_data = toml_loader.load(f)
                tool_config = config_data.get("tool", {})
                if isinstance(tool_config, dict):
                    pycomplex_config = tool_config.get("pycomplex", {})
                    if isinstance(pycomplex_config, dict):
                        return pycomplex_config
                return {}
        except Exception:
            # If parsing fails, use empty config
            return {}

    def _get_settings(self) -> PyComplexSettings:
        """Get Pydantic settings instance."""
        if self._settings is None:
            config_data = self._load_config()
            try:
                self._settings = PyComplexSettings.from_toml_config(config_data)
            except ValidationError as e:
                # Convert validation error to user-friendly message
                raise ValueError(f"Configuration error in pyproject.toml: {e}") from e
        return self._settings

    def get_max_complexity(self) -> Optional[int]:
        """Get maximum cyclomatic complexity threshold."""
        return self._get_settings().max_complexity

    def get_max_cognitive(self) -> Optional[int]:
        """Get maximum cognitive complexity threshold."""
        return self._get_settings().max_cognitive

    def get_exclude_patterns(self) -> list[str]:
        """Get file patterns to exclude."""
        return self._get_settings().exclude

    def get_include_patterns(self) -> list[str]:
        """Get file patterns to include."""
        return self._get_settings().include

    def get_default_paths(self) -> list[str]:
        """Get default paths to analyze."""
        return self._get_settings().paths

    def get_status_thresholds(self) -> dict[str, dict[str, int]]:
        """Get status classification thresholds."""
        return self._get_settings().status_thresholds

    def merge_with_cli_options(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[list[str]] = None,
        include: Optional[list[str]] = None,
        paths: Optional[list[str]] = None,
    ) -> dict[str, Union[str, int, list[str], None]]:
        """Merge configuration with CLI options, CLI takes precedence."""
        settings = self._get_settings()
        return {
            "max_complexity": max_complexity or settings.max_complexity,
            "max_cognitive": max_cognitive or settings.max_cognitive,
            "exclude": list(exclude) if exclude else settings.exclude,
            "include": list(include) if include else settings.include,
            "paths": list(paths) if paths else settings.paths,
        }
