"""Tests for the CLI helpers module."""

from typing import Any

import pytest

from pycomplex.cli_helpers import (
    format_and_display_output,
    validate_required_config,
)
from pycomplex.formatters import OutputFormatter
from pycomplex.models import ComplexityResult, FileComplexityResult


class TestCliHelpers:
    """Test cases for CLI helper functions."""

    def test_validate_required_config_valid(self) -> None:
        """Test validate_required_config with valid config."""
        config = {
            "max_complexity": 10,
            "max_cognitive": None,
            "exclude": [],
            "include": [],
            "paths": ["src/"],
        }

        # Should not raise any exception
        validate_required_config(config)

    def test_validate_required_config_missing_max_complexity(self) -> None:
        """Test validate_required_config with missing max_complexity."""
        config = {
            "max_complexity": None,
            "max_cognitive": None,
            "exclude": [],
            "include": [],
            "paths": ["src/"],
        }

        with pytest.raises(SystemExit) as exc_info:
            validate_required_config(config)

        assert exc_info.value.code == 1, (
            f"Expected SystemExit with code 1, got {exc_info.value.code}"
        )

    def test_format_and_display_output_table(self, capsys: Any) -> None:
        """Test format_and_display_output with table format."""
        # Create sample results
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

        format_and_display_output([result], "table", formatter)

        captured = capsys.readouterr()
        assert "test.py" in captured.out, (
            f"Expected 'test.py' in table output, got: {captured.out}"
        )
        assert "Cyclomatic" in captured.out, (
            f"Expected 'Cyclomatic' header in table output, got: {captured.out}"
        )

    def test_format_and_display_output_json(self, capsys: Any) -> None:
        """Test format_and_display_output with JSON format."""
        # Create sample results
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

        format_and_display_output([result], "json", formatter)

        captured = capsys.readouterr()
        assert "test.py" in captured.out
        assert '"file_path"' in captured.out

    def test_format_and_display_output_csv(self, capsys: Any) -> None:
        """Test format_and_display_output with CSV format."""
        # Create sample results
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

        format_and_display_output([result], "csv", formatter)

        captured = capsys.readouterr()
        assert "test.py" in captured.out
        assert "file_path" in captured.out

    def test_format_and_display_output_detailed(self, capsys: Any) -> None:
        """Test format_and_display_output with detailed format."""
        # Create sample results
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

        format_and_display_output([result], "detailed", formatter)

        captured = capsys.readouterr()
        assert "test.py" in captured.out
        assert "test_func" in captured.out
        assert "File totals" in captured.out
