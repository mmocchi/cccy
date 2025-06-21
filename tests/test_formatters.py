"""Tests for the output formatters module."""

import json

import pytest

from cccy.formatters import OutputFormatter
from cccy.models import ComplexityResult, FileComplexityResult


@pytest.fixture
def sample_results() -> list[FileComplexityResult]:
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

    def test_format_table_empty(self) -> None:
        """Test formatting empty results as table."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_table([])

        # Assert
        assert result == "No Python files analyzed.", (
            f"Expected empty message, got: {result}"
        )

    def test_format_table_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as table."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_table(sample_results)

        # Assert
        assert "File" in result, "Table header 'File' not found in output"
        assert "Cyclomatic" in result, "Table header 'Cyclomatic' not found in output"
        assert "Cognitive" in result, "Table header 'Cognitive' not found in output"
        assert "Status" in result, "Table header 'Status' not found in output"
        assert "simple.py" in result, "Expected filename 'simple.py' not found in table"
        assert "complex.py" in result, (
            "Expected filename 'complex.py' not found in table"
        )
        assert "OK" in result, "Expected status 'OK' not found in table"
        assert "MEDIUM" in result, "Expected status 'MEDIUM' not found in table"

    def test_format_detailed_table_empty(self) -> None:
        """Test formatting empty results as detailed table."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_detailed_table([])

        # Assert
        assert result == "No Python files analyzed."

    def test_format_detailed_table_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as detailed table."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_detailed_table(sample_results)

        # Assert
        assert "simple.py" in result
        assert "complex.py" in result
        assert "simple_func" in result
        assert "complex_func" in result
        assert "Function" in result
        assert "Line" in result
        assert "File totals" in result

    def test_format_detailed_table_no_functions(self) -> None:
        """Test formatting file with no functions as detailed table."""
        # Arrange
        result_no_funcs = FileComplexityResult(
            file_path="empty.py",
            functions=[],
            total_cyclomatic=0,
            total_cognitive=0,
            max_cyclomatic=0,
            max_cognitive=0,
        )
        formatter = OutputFormatter()

        # Act
        result = formatter.format_detailed_table([result_no_funcs])

        # Assert
        assert "empty.py" in result
        assert "No functions found." in result

    def test_format_json_empty(self) -> None:
        """Test formatting empty results as JSON."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_json([])

        # Assert
        parsed = json.loads(result)
        assert parsed == []

    def test_format_json_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as JSON."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_json(sample_results)

        # Assert
        parsed = json.loads(result)
        assert len(parsed) == 2, f"Expected 2 files in JSON output, got {len(parsed)}"
        assert parsed[0]["file_path"] == "simple.py", (
            f"Expected first file to be 'simple.py', got {parsed[0]['file_path']}"
        )
        assert parsed[1]["file_path"] == "complex.py", (
            f"Expected second file to be 'complex.py', got {parsed[1]['file_path']}"
        )

        first_file = parsed[0]
        assert "functions" in first_file, "Missing 'functions' key in JSON file output"
        assert "totals" in first_file, "Missing 'totals' key in JSON file output"
        assert "max_complexity" in first_file, (
            "Missing 'max_complexity' key in JSON file output"
        )
        assert "status" in first_file, "Missing 'status' key in JSON file output"

        first_function = first_file["functions"][0]
        assert first_function["name"] == "simple_func", (
            f"Expected function name 'simple_func', got {first_function['name']}"
        )
        assert first_function["line"] == 10, (
            f"Expected line number 10, got {first_function['line']}"
        )
        assert first_function["cyclomatic_complexity"] == 1, (
            f"Expected cyclomatic complexity 1, got {first_function['cyclomatic_complexity']}"
        )
        assert first_function["cognitive_complexity"] == 0, (
            f"Expected cognitive complexity 0, got {first_function['cognitive_complexity']}"
        )

    def test_format_csv_empty(self) -> None:
        """Test formatting empty results as CSV."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_csv([])

        # Assert
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert "file_path" in lines[0]
        assert "function_name" in lines[0]

    def test_format_csv_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as CSV."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_csv(sample_results)

        # Assert
        lines = result.strip().split("\n")
        assert len(lines) == 3
        header = lines[0]
        assert "file_path" in header
        assert "function_name" in header
        assert "cyclomatic_complexity" in header
        assert "simple.py" in lines[1]
        assert "simple_func" in lines[1]
        assert "complex.py" in lines[2]
        assert "complex_func" in lines[2]

    def test_format_csv_no_functions(self) -> None:
        """Test formatting file with no functions as CSV."""
        # Arrange
        result_no_funcs = FileComplexityResult(
            file_path="empty.py",
            functions=[],
            total_cyclomatic=0,
            total_cognitive=0,
            max_cyclomatic=0,
            max_cognitive=0,
        )
        formatter = OutputFormatter()

        # Act
        result = formatter.format_csv([result_no_funcs])

        # Assert
        lines = result.strip().split("\n")
        assert len(lines) == 2
        assert "empty.py" in lines[1]
        values = lines[1].split(",")
        assert values[1] == ""  # empty function name

    def test_format_summary_empty(self) -> None:
        """Test formatting empty results as summary."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_summary([])

        # Assert
        assert result == "No Python files analyzed."

    def test_format_summary_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as summary."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_summary(sample_results)

        # Assert
        assert "Analyzed 2 files" in result
        assert "functions" in result
        assert "Status distribution" in result
        assert "OK: 1" in result
        assert "MEDIUM: 1" in result
        assert "HIGH: 0" in result

    def test_format_summary_with_high_complexity(self) -> None:
        """Test formatting summary with high complexity files."""
        # Arrange
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

        # Act
        result = formatter.format_summary([high_complexity_result])

        # Assert
        assert "HIGH: 1" in result
        assert "High complexity files:" in result
        assert "very_complex.py" in result
        assert "max cyclomatic: 15" in result
        assert "max cognitive: 12" in result

    def test_format_functions_json_empty(self) -> None:
        """Test formatting empty results as functions JSON."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_functions_json([])

        # Assert
        parsed = json.loads(result)
        assert parsed == []

    def test_format_functions_json_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as functions JSON."""
        formatter = OutputFormatter()
        result = formatter.format_functions_json(sample_results)

        parsed = json.loads(result)

        # Should have 2 functions (one from each file)
        assert len(parsed) == 2, (
            f"Expected 2 functions in JSON output, got {len(parsed)}"
        )

        # Check first function
        first_func = parsed[0]
        assert first_func["file_path"] == "simple.py", (
            f"Expected first function from 'simple.py', got {first_func['file_path']}"
        )
        assert first_func["function_name"] == "simple_func", (
            f"Expected function name 'simple_func', got {first_func['function_name']}"
        )
        assert first_func["line_number"] == 10, (
            f"Expected line number 10, got {first_func['line_number']}"
        )
        assert first_func["cyclomatic_complexity"] == 1, (
            f"Expected cyclomatic complexity 1, got {first_func['cyclomatic_complexity']}"
        )
        assert first_func["cognitive_complexity"] == 0, (
            f"Expected cognitive complexity 0, got {first_func['cognitive_complexity']}"
        )
        assert first_func["file_status"] == "OK", (
            f"Expected file status 'OK', got {first_func['file_status']}"
        )

        # Check second function
        second_func = parsed[1]
        assert second_func["file_path"] == "complex.py", (
            f"Expected second function from 'complex.py', got {second_func['file_path']}"
        )
        assert second_func["function_name"] == "complex_func", (
            f"Expected function name 'complex_func', got {second_func['function_name']}"
        )
        assert second_func["line_number"] == 20, (
            f"Expected line number 20, got {second_func['line_number']}"
        )
        assert second_func["cyclomatic_complexity"] == 8, (
            f"Expected cyclomatic complexity 8, got {second_func['cyclomatic_complexity']}"
        )
        assert second_func["cognitive_complexity"] == 5, (
            f"Expected cognitive complexity 5, got {second_func['cognitive_complexity']}"
        )
        assert second_func["file_status"] == "MEDIUM", (
            f"Expected file status 'MEDIUM', got {second_func['file_status']}"
        )

    def test_format_functions_json_no_functions(self) -> None:
        """Test formatting file with no functions as functions JSON."""
        result_no_funcs = FileComplexityResult(
            file_path="empty.py",
            functions=[],
            total_cyclomatic=0,
            total_cognitive=0,
            max_cyclomatic=0,
            max_cognitive=0,
        )

        formatter = OutputFormatter()
        result = formatter.format_functions_json([result_no_funcs])

        parsed = json.loads(result)
        assert parsed == []  # No functions means empty array

    def test_format_functions_csv_empty(self) -> None:
        """Test formatting empty results as functions CSV."""
        # Arrange
        formatter = OutputFormatter()

        # Act
        result = formatter.format_functions_csv([])

        # Assert
        lines = result.strip().split("\n")
        assert len(lines) == 1
        header = lines[0]
        assert "file_path" in header
        assert "function_name" in header
        assert "line_number" in header
        assert "cyclomatic_complexity" in header
        assert "cognitive_complexity" in header

    def test_format_functions_csv_with_results(
        self, sample_results: list[FileComplexityResult]
    ) -> None:
        """Test formatting results as functions CSV."""
        formatter = OutputFormatter()
        result = formatter.format_functions_csv(sample_results)

        lines = result.strip().split("\n")

        # Header + 2 data rows (one function per file)
        assert len(lines) == 3

        # Check header
        header = lines[0]
        assert "file_path" in header
        assert "function_name" in header
        assert "line_number" in header

        # Check first function data
        first_row = lines[1].split(",")
        assert "simple.py" in first_row[0]
        assert "simple_func" in first_row[1]
        assert "10" in first_row[2]  # line number
        assert "1" in first_row[4]  # cyclomatic complexity
        assert "0" in first_row[5]  # cognitive complexity

        # Check second function data
        second_row = lines[2].split(",")
        assert "complex.py" in second_row[0]
        assert "complex_func" in second_row[1]
        assert "20" in second_row[2]  # line number
        assert "8" in second_row[4]  # cyclomatic complexity
        assert "5" in second_row[5]  # cognitive complexity

    def test_format_functions_csv_no_functions(self) -> None:
        """Test formatting file with no functions as functions CSV."""
        result_no_funcs = FileComplexityResult(
            file_path="empty.py",
            functions=[],
            total_cyclomatic=0,
            total_cognitive=0,
            max_cyclomatic=0,
            max_cognitive=0,
        )

        formatter = OutputFormatter()
        result = formatter.format_functions_csv([result_no_funcs])

        lines = result.strip().split("\n")

        # Should only have header, no data rows since no functions
        assert len(lines) == 1
        assert "file_path" in lines[0]

    def test_format_functions_csv_multiple_functions_per_file(self) -> None:
        """Test formatting file with multiple functions as functions CSV."""
        function1 = ComplexityResult(
            name="func1",
            cyclomatic_complexity=2,
            cognitive_complexity=1,
            lineno=10,
            col_offset=0,
            end_lineno=15,
        )

        function2 = ComplexityResult(
            name="func2",
            cyclomatic_complexity=3,
            cognitive_complexity=2,
            lineno=20,
            col_offset=0,
            end_lineno=25,
        )

        file_result = FileComplexityResult(
            file_path="multi.py",
            functions=[function1, function2],
            total_cyclomatic=5,
            total_cognitive=3,
            max_cyclomatic=3,
            max_cognitive=2,
        )

        formatter = OutputFormatter()
        result = formatter.format_functions_csv([file_result])

        lines = result.strip().split("\n")

        # Header + 2 data rows
        assert len(lines) == 3

        # Both functions should be from the same file
        assert "multi.py" in lines[1]
        assert "multi.py" in lines[2]

        # Check function names are different
        assert "func1" in lines[1]
        assert "func2" in lines[2]
