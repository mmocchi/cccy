"""Tests for the output formatters module."""

import json

import pytest

from pycomplex.analyzer import ComplexityResult, FileComplexityResult
from pycomplex.formatters import OutputFormatter


@pytest.fixture
def sample_results():
    """Create sample complexity results for testing."""
    function1 = ComplexityResult(
        name="simple_func",
        cyclomatic_complexity=1,
        cognitive_complexity=0,
        lineno=10,
        col_offset=0,
    )

    function2 = ComplexityResult(
        name="complex_func",
        cyclomatic_complexity=8,
        cognitive_complexity=5,
        lineno=20,
        col_offset=0,
    )

    result1 = FileComplexityResult(
        file_path="simple.py",
        functions=[function1],
        total_cyclomatic=1,
        total_cognitive=0,
        max_cyclomatic=1,
        max_cognitive=0,
    )

    result2 = FileComplexityResult(
        file_path="complex.py",
        functions=[function2],
        total_cyclomatic=8,
        total_cognitive=5,
        max_cyclomatic=8,
        max_cognitive=5,
    )

    return [result1, result2]


class TestOutputFormatter:
    """Test cases for OutputFormatter."""

    def test_format_table_empty(self):
        """Test formatting empty results as table."""
        formatter = OutputFormatter()
        result = formatter.format_table([])

        assert result == "No Python files analyzed."

    def test_format_table_with_results(self, sample_results):
        """Test formatting results as table."""
        formatter = OutputFormatter()
        result = formatter.format_table(sample_results)

        assert "File" in result
        assert "Cyclomatic" in result
        assert "Cognitive" in result
        assert "Status" in result
        assert "simple.py" in result
        assert "complex.py" in result
        assert "OK" in result
        assert "MEDIUM" in result

    def test_format_detailed_table_empty(self):
        """Test formatting empty results as detailed table."""
        formatter = OutputFormatter()
        result = formatter.format_detailed_table([])

        assert result == "No Python files analyzed."

    def test_format_detailed_table_with_results(self, sample_results):
        """Test formatting results as detailed table."""
        formatter = OutputFormatter()
        result = formatter.format_detailed_table(sample_results)

        assert "simple.py" in result
        assert "complex.py" in result
        assert "simple_func" in result
        assert "complex_func" in result
        assert "Function" in result
        assert "Line" in result
        assert "File totals" in result

    def test_format_detailed_table_no_functions(self):
        """Test formatting file with no functions as detailed table."""
        result_no_funcs = FileComplexityResult(
            file_path="empty.py",
            functions=[],
            total_cyclomatic=0,
            total_cognitive=0,
            max_cyclomatic=0,
            max_cognitive=0,
        )

        formatter = OutputFormatter()
        result = formatter.format_detailed_table([result_no_funcs])

        assert "empty.py" in result
        assert "No functions found." in result

    def test_format_json_empty(self):
        """Test formatting empty results as JSON."""
        formatter = OutputFormatter()
        result = formatter.format_json([])

        parsed = json.loads(result)
        assert parsed == []

    def test_format_json_with_results(self, sample_results):
        """Test formatting results as JSON."""
        formatter = OutputFormatter()
        result = formatter.format_json(sample_results)

        parsed = json.loads(result)

        assert len(parsed) == 2
        assert parsed[0]["file_path"] == "simple.py"
        assert parsed[1]["file_path"] == "complex.py"

        # Check first file structure
        first_file = parsed[0]
        assert "functions" in first_file
        assert "totals" in first_file
        assert "max_complexity" in first_file
        assert "status" in first_file

        # Check function structure
        first_function = first_file["functions"][0]
        assert first_function["name"] == "simple_func"
        assert first_function["line"] == 10
        assert first_function["cyclomatic_complexity"] == 1
        assert first_function["cognitive_complexity"] == 0

    def test_format_csv_empty(self):
        """Test formatting empty results as CSV."""
        formatter = OutputFormatter()
        result = formatter.format_csv([])

        lines = result.strip().split("\n")
        # Should only have header
        assert len(lines) == 1
        assert "file_path" in lines[0]
        assert "function_name" in lines[0]

    def test_format_csv_with_results(self, sample_results):
        """Test formatting results as CSV."""
        formatter = OutputFormatter()
        result = formatter.format_csv(sample_results)

        lines = result.strip().split("\n")

        # Header + 2 data rows
        assert len(lines) == 3

        # Check header
        header = lines[0]
        assert "file_path" in header
        assert "function_name" in header
        assert "cyclomatic_complexity" in header

        # Check data rows
        assert "simple.py" in lines[1]
        assert "simple_func" in lines[1]
        assert "complex.py" in lines[2]
        assert "complex_func" in lines[2]

    def test_format_csv_no_functions(self):
        """Test formatting file with no functions as CSV."""
        result_no_funcs = FileComplexityResult(
            file_path="empty.py",
            functions=[],
            total_cyclomatic=0,
            total_cognitive=0,
            max_cyclomatic=0,
            max_cognitive=0,
        )

        formatter = OutputFormatter()
        result = formatter.format_csv([result_no_funcs])

        lines = result.strip().split("\n")

        # Header + 1 data row (empty function data)
        assert len(lines) == 2
        assert "empty.py" in lines[1]
        # Should have empty function name
        values = lines[1].split(",")
        assert values[1] == ""  # empty function name

    def test_format_summary_empty(self):
        """Test formatting empty results as summary."""
        formatter = OutputFormatter()
        result = formatter.format_summary([])

        assert result == "No Python files analyzed."

    def test_format_summary_with_results(self, sample_results):
        """Test formatting results as summary."""
        formatter = OutputFormatter()
        result = formatter.format_summary(sample_results)

        assert "Analyzed 2 files" in result
        assert "functions" in result
        assert "Status distribution" in result
        assert "OK: 1" in result
        assert "MEDIUM: 1" in result
        assert "HIGH: 0" in result

    def test_format_summary_with_high_complexity(self):
        """Test formatting summary with high complexity files."""
        high_complexity_func = ComplexityResult(
            name="very_complex_func",
            cyclomatic_complexity=15,
            cognitive_complexity=12,
            lineno=30,
            col_offset=0,
        )

        high_complexity_result = FileComplexityResult(
            file_path="very_complex.py",
            functions=[high_complexity_func],
            total_cyclomatic=15,
            total_cognitive=12,
            max_cyclomatic=15,
            max_cognitive=12,
        )

        formatter = OutputFormatter()
        result = formatter.format_summary([high_complexity_result])

        assert "HIGH: 1" in result
        assert "High complexity files:" in result
        assert "very_complex.py" in result
        assert "max cyclomatic: 15" in result
        assert "max cognitive: 12" in result
