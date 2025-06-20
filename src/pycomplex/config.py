"""Configuration management for pycomplex."""

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    # Python < 3.11
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class PyComplexConfig:
    """Configuration loader for pycomplex."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize configuration loader.

        Args:
            config_path: Path to pyproject.toml file. If None, searches for it.

        """
        self.config_path = config_path or self._find_config_file()
        self._config_data: Optional[Dict[str, Any]] = None

    def _find_config_file(self) -> Optional[Path]:
        """Find pyproject.toml file in current directory or parent directories."""
        current_dir = Path.cwd()

        # Look in current directory and parents
        for path in [current_dir, *current_dir.parents]:
            pyproject_path = path / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path

        return None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from pyproject.toml file."""
        if self._config_data is not None:
            return self._config_data

        if not self.config_path or not self.config_path.exists():
            self._config_data = {}
            return self._config_data

        if tomllib is None:
            # No TOML parser available, return empty config
            self._config_data = {}
            return self._config_data

        try:
            with self.config_path.open("rb") as f:
                config_data = tomllib.load(f)
                self._config_data = config_data.get("tool", {}).get("pycomplex", {})
        except Exception:
            # If parsing fails, use empty config
            self._config_data = {}

        return self._config_data

    def get_max_complexity(self) -> Optional[int]:
        """Get maximum cyclomatic complexity threshold."""
        config = self._load_config()
        return config.get("max-complexity")

    def get_max_cognitive(self) -> Optional[int]:
        """Get maximum cognitive complexity threshold."""
        config = self._load_config()
        return config.get("max-cognitive")

    def get_exclude_patterns(self) -> List[str]:
        """Get file patterns to exclude."""
        config = self._load_config()
        patterns = config.get("exclude", [])
        return list(patterns) if patterns else []

    def get_include_patterns(self) -> List[str]:
        """Get file patterns to include."""
        config = self._load_config()
        patterns = config.get("include", [])
        return list(patterns) if patterns else []

    def get_default_paths(self) -> List[str]:
        """Get default paths to analyze."""
        config = self._load_config()
        paths = config.get("paths", [])

        # If no paths configured, use current directory
        if not paths:
            return ["."]

        return list(paths) if paths else ["."]

    def get_status_thresholds(self) -> Dict[str, Dict[str, int]]:
        """Get status classification thresholds."""
        config = self._load_config()
        default_thresholds = self._get_default_thresholds()
        configured_thresholds = config.get("status-thresholds", {})

        return self._merge_thresholds(default_thresholds, configured_thresholds)

    def _get_default_thresholds(self) -> Dict[str, Dict[str, int]]:
        """Get the default status thresholds.

        Returns:
            Default threshold configuration

        """
        return {
            "medium": {
                "cyclomatic": 5,
                "cognitive": 4,
            },
            "high": {
                "cyclomatic": 10,
                "cognitive": 7,
            },
        }

    def _merge_thresholds(
        self, defaults: Dict[str, Dict[str, int]], overrides: Dict[str, Any]
    ) -> Dict[str, Dict[str, int]]:
        """Merge default thresholds with configuration overrides.

        Args:
            defaults: Default threshold values
            overrides: Configuration override values

        Returns:
            Merged threshold configuration

        """
        result = defaults.copy()

        for level in ["medium", "high"]:
            if level in overrides:
                self._update_threshold_level(result[level], overrides[level])

        return result

    def _update_threshold_level(
        self, default_level: Dict[str, int], override_level: Dict[str, Any]
    ) -> None:
        """Update a specific threshold level with overrides.

        Args:
            default_level: Default values for this level (modified in place)
            override_level: Override values for this level

        """
        for metric in ["cyclomatic", "cognitive"]:
            if metric in override_level:
                default_level[metric] = override_level[metric]

    def merge_with_cli_options(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Merge configuration with CLI options, CLI takes precedence."""
        return {
            "max_complexity": max_complexity or self.get_max_complexity(),
            "max_cognitive": max_cognitive or self.get_max_cognitive(),
            "exclude": list(exclude) if exclude else self.get_exclude_patterns(),
            "include": list(include) if include else self.get_include_patterns(),
            "paths": list(paths) if paths else self.get_default_paths(),
        }
