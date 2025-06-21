"""Tests for the config module."""

import tempfile
from pathlib import Path

from cccy.config import CccyConfig


class TestCccyConfig:
    """Test cases for ConfigManager."""

    def test_init_without_config_file(self) -> None:
        """Test initialization without config file."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            config_manager = CccyConfig(Path(tmpdir) / "nonexistent.toml")

            # Assert - Should use defaults
            assert config_manager.get_max_complexity() is None, (
                f"Expected None for max_complexity, got {config_manager.get_max_complexity()}"
            )
            assert config_manager.get_max_cognitive() is None, (
                f"Expected None for max_cognitive, got {config_manager.get_max_cognitive()}"
            )
            assert config_manager.get_exclude_patterns() == [], (
                f"Expected empty exclude patterns, got {config_manager.get_exclude_patterns()}"
            )
            assert config_manager.get_include_patterns() == [], (
                f"Expected empty include patterns, got {config_manager.get_include_patterns()}"
            )

    def test_init_with_config_file(self) -> None:
        """Test initialization with config file."""
        # Arrange
        config_content = """
[tool.cccy]
max-complexity = 8
max-cognitive = 6
exclude = ["*/tests/*", "*/migrations/*"]
include = ["*.py"]
paths = ["src/", "lib/"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()

            # Act
            config_manager = CccyConfig(Path(f.name))

            # Assert
            assert config_manager.get_max_complexity() == 8
            assert config_manager.get_max_cognitive() == 6
            assert config_manager.get_exclude_patterns() == [
                "*/tests/*",
                "*/migrations/*",
            ]
            assert config_manager.get_include_patterns() == ["*.py"]
            assert config_manager.get_default_paths() == ["src/", "lib/"]

    def test_get_status_thresholds_default(self) -> None:
        """Test getting default status thresholds."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = CccyConfig(Path(tmpdir) / "nonexistent.toml")

            # Act
            thresholds = config_manager.get_status_thresholds()

            # Assert
            expected = {
                "medium": {"cyclomatic": 5, "cognitive": 4},
                "high": {"cyclomatic": 10, "cognitive": 7},
            }
            assert thresholds == expected

    def test_get_status_thresholds_custom(self) -> None:
        """Test getting custom status thresholds."""
        config_content = """
[tool.cccy]
status-thresholds = { medium = { cyclomatic = 3, cognitive = 2 }, high = { cyclomatic = 8, cognitive = 5 } }
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()

            config_manager = CccyConfig(Path(f.name))
            thresholds = config_manager.get_status_thresholds()

            expected = {
                "medium": {"cyclomatic": 3, "cognitive": 2},
                "high": {"cyclomatic": 8, "cognitive": 5},
            }
            assert thresholds == expected

    def test_merge_with_cli_options_all_none(self) -> None:
        """Test merging when all CLI options are None."""
        config_content = """
[tool.cccy]
max-complexity = 8
exclude = ["*/tests/*"]
paths = ["src/"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()

            config_manager = CccyConfig(Path(f.name))
            merged = config_manager.merge_with_cli_options(
                max_complexity=None,
                max_cognitive=None,
                exclude=None,
                include=None,
                paths=None,
            )

            assert merged["max_complexity"] == 8
            assert merged["exclude"] == ["*/tests/*"]
            assert merged["paths"] == ["src/"]

    def test_merge_with_cli_options_cli_override(self) -> None:
        """Test CLI options overriding config file values."""
        config_content = """
[tool.cccy]
max-complexity = 8
exclude = ["*/tests/*"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()

            config_manager = CccyConfig(Path(f.name))
            merged = config_manager.merge_with_cli_options(
                max_complexity=12,
                max_cognitive=None,
                exclude=["*/migrations/*"],
                include=None,
                paths=["lib/"],
            )

            assert merged["max_complexity"] == 12  # CLI override
            assert merged["exclude"] == ["*/migrations/*"]  # CLI override
            assert merged["paths"] == ["lib/"]  # CLI override

    def test_config_with_partial_status_thresholds(self) -> None:
        """Test config with only partial status threshold definitions."""
        config_content = """
[tool.cccy]
status-thresholds = { medium = { cyclomatic = 3 } }
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()

            config_manager = CccyConfig(Path(f.name))
            thresholds = config_manager.get_status_thresholds()

            # Should merge with defaults
            expected = {
                "medium": {
                    "cyclomatic": 3,
                    "cognitive": 4,
                },  # cyclomatic from config, cognitive from default
                "high": {"cyclomatic": 10, "cognitive": 7},  # all from defaults
            }
            assert thresholds == expected

    def test_config_file_found_directly(self) -> None:
        """Test finding config file when specified directly."""
        config_content = """
[tool.cccy]
max-complexity = 15
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()

            # Initialize with explicit path - should find it
            config_manager = CccyConfig(Path(f.name))
            assert config_manager.get_max_complexity() == 15

    def test_invalid_toml_file(self) -> None:
        """Test handling invalid TOML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid toml content [[[")
            f.flush()

            # Should not raise exception, should use defaults
            config_manager = CccyConfig(Path(f.name))
            assert config_manager.get_max_complexity() is None

    def test_get_default_paths_with_current_dir(self) -> None:
        """Test getting default paths when none specified in config."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = CccyConfig(Path(tmpdir) / "nonexistent.toml")

            # Act
            paths = config_manager.get_default_paths()

            # Assert
            assert paths == ["."]  # Should default to current directory
