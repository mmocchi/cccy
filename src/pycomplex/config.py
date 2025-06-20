"""Configuration management for pycomplex."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import tomllib
except ImportError:
    # Python < 3.11
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


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
        for path in [current_dir] + list(current_dir.parents):
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
            with open(self.config_path, "rb") as f:
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
        return config.get("exclude", [])

    def get_include_patterns(self) -> List[str]:
        """Get file patterns to include."""
        config = self._load_config()
        return config.get("include", [])

    def get_default_paths(self) -> List[str]:
        """Get default paths to analyze."""
        config = self._load_config()
        paths = config.get("paths", [])
        
        # If no paths configured, use current directory
        if not paths:
            return ["."]
        
        return paths

    def merge_with_cli_options(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Merge configuration with CLI options, CLI takes precedence."""
        config = {
            "max_complexity": max_complexity or self.get_max_complexity(),
            "max_cognitive": max_cognitive or self.get_max_cognitive(),
            "exclude": list(exclude) if exclude else self.get_exclude_patterns(),
            "include": list(include) if include else self.get_include_patterns(),
            "paths": list(paths) if paths else self.get_default_paths(),
        }
        
        return config