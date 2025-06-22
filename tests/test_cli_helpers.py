"""Tests for the CLI helpers module."""

from typing import Any, Union, cast

import pytest

from cccy.domain.entities.complexity import ComplexityResult, FileComplexityResult
from cccy.infrastructure.formatters.output import OutputFormatter
from cccy.presentation.cli.helpers import (
    format_and_display_output,
    validate_required_config,
)


class TestCliHelpers:
    """Test cases for CLI helper functions."""

    def test_validate_required_config_valid(self) -> None:
        """Test validate_required_config with valid config."""
        # Arrange
        config = {
            "max_complexity": 10,
            "max_cognitive": None,
            "exclude": [],
            "include": [],
            "paths": ["src/"],
        }

        # Act & Assert - Should not raise any exception
        validate_required_config(
            cast("dict[str, Union[str, int, list[str], None]]", config)
        )

    def test_validate_required_config_missing_max_complexity(self) -> None:
        """Test validate_required_config with missing max_complexity."""
        # Arrange
        config = {
            "max_complexity": None,
            "max_cognitive": None,
            "exclude": [],
            "include": [],
            "paths": ["src/"],
        }

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            validate_required_config(
                cast("dict[str, Union[str, int, list[str], None]]", config)
            )

        assert exc_info.value.code == 1, (
            f"Expected SystemExit with code 1, got {exc_info.value.code}"
        )

    def test_format_and_display_output_table(self, capsys: Any) -> None:
        """Test format_and_display_output with table format."""
        # Arrange
        function = ComplexityResult(
            name="test_func",
            cyclomatic_complexity=3,
            cognitive_complexity=2,
            lineno=10,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="test.py",
            functions=[function],
            total_cyclomatic=3,
            total_cognitive=2,
            max_cyclomatic=3,
            max_cognitive=2,
        )
        formatter = OutputFormatter()

        # Act
        format_and_display_output([result], "table", formatter)

        # Assert
        captured = capsys.readouterr()
        assert "test.py" in captured.out, (
            f"Expected 'test.py' in table output, got: {captured.out}"
        )
        assert "Cyclomatic" in captured.out, (
            f"Expected 'Cyclomatic' header in table output, got: {captured.out}"
        )

    def test_format_and_display_output_json(self, capsys: Any) -> None:
        """Test format_and_display_output with JSON format."""
        # Arrange
        function = ComplexityResult(
            name="test_func",
            cyclomatic_complexity=3,
            cognitive_complexity=2,
            lineno=10,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="test.py",
            functions=[function],
            total_cyclomatic=3,
            total_cognitive=2,
            max_cyclomatic=3,
            max_cognitive=2,
        )
        formatter = OutputFormatter()

        # Act
        format_and_display_output([result], "json", formatter)

        # Assert
        captured = capsys.readouterr()
        assert "test.py" in captured.out
        assert '"file_path"' in captured.out

    def test_format_and_display_output_csv(self, capsys: Any) -> None:
        """Test format_and_display_output with CSV format."""
        # Arrange
        function = ComplexityResult(
            name="test_func",
            cyclomatic_complexity=3,
            cognitive_complexity=2,
            lineno=10,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="test.py",
            functions=[function],
            total_cyclomatic=3,
            total_cognitive=2,
            max_cyclomatic=3,
            max_cognitive=2,
        )
        formatter = OutputFormatter()

        # Act
        format_and_display_output([result], "csv", formatter)

        # Assert
        captured = capsys.readouterr()
        assert "test.py" in captured.out
        assert "file_path" in captured.out

    def test_format_and_display_output_detailed(self, capsys: Any) -> None:
        """Test format_and_display_output with detailed format."""
        # Arrange
        function = ComplexityResult(
            name="test_func",
            cyclomatic_complexity=3,
            cognitive_complexity=2,
            lineno=10,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="test.py",
            functions=[function],
            total_cyclomatic=3,
            total_cognitive=2,
            max_cyclomatic=3,
            max_cognitive=2,
        )
        formatter = OutputFormatter()

        # Act
        format_and_display_output([result], "detailed", formatter)

        # Assert
        captured = capsys.readouterr()
        assert "test.py" in captured.out
        assert "test_func" in captured.out
        assert "File totals" in captured.out
