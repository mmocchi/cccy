"""Tests for the complexity analyzer module."""

import tempfile
from pathlib import Path

from cccy.domain.entities.complexity import ComplexityResult, FileComplexityResult
from cccy.domain.services.complexity_analyzer import ComplexityAnalyzer


class TestComplexityAnalyzer:
    """Test cases for ComplexityAnalyzer."""

    def test_analyze_simple_file(self) -> None:
        """Test analyzing a simple Python file."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = analyzer.analyze_file(fixture_path)

        # Assert
        assert result is not None, f"Failed to analyze file {fixture_path}"
        assert isinstance(result, FileComplexityResult), (
            f"Expected FileComplexityResult, got {type(result)}"
        )
        assert result.file_path == str(fixture_path), (
            f"Expected file path {fixture_path}, got {result.file_path}"
        )
        assert len(result.functions) > 0, (
            f"Expected to find functions in {fixture_path}, found none"
        )
        function_names = [f.name for f in result.functions]
        assert "simple_function" in function_names, (
            f"Expected 'simple_function' in {function_names}"
        )
        assert "function_with_if" in function_names, (
            f"Expected 'function_with_if' in {function_names}"
        )
        assert "complex_function" in function_names, (
            f"Expected 'complex_function' in {function_names}"
        )
        assert "async_function" in function_names, (
            f"Expected 'async_function' in {function_names}"
        )

    def test_analyze_nonexistent_file(self) -> None:
        """Test analyzing a file that doesn't exist."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        # Act
        result = analyzer.analyze_file("nonexistent.py")

        # Assert
        assert result is None, "Expected None for nonexistent file, but got a result"

    def test_analyze_non_python_file(self) -> None:
        """Test analyzing a non-Python file."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("This is not Python code")
            f.flush()

            # Act
            result = analyzer.analyze_file(f.name)

        # Assert
        assert result is None

    def test_analyze_directory(self) -> None:
        """Test analyzing a directory."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        fixtures_dir = Path(__file__).parent / "fixtures"

        # Act
        results = analyzer.analyze_directory(fixtures_dir, recursive=False)

        # Assert
        assert len(results) >= 1
        assert all(isinstance(r, FileComplexityResult) for r in results)
        file_paths = [r.file_path for r in results]
        assert any("simple.py" in path for path in file_paths)

    def test_analyze_directory_with_exclusions(self) -> None:
        """Test analyzing a directory with exclusion patterns."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "include.py").write_text("def test(): pass")
            (tmpdir_path / "exclude.py").write_text("def test(): pass")

            # Act
            results = analyzer.analyze_directory(
                tmpdir_path, recursive=False, exclude_patterns=["exclude.py"]
            )

            # Assert
            file_paths = [Path(r.file_path).name for r in results]
            assert "include.py" in file_paths
            assert "exclude.py" not in file_paths

    def test_complexity_calculation(self) -> None:
        """Test that complexity calculations return reasonable values."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = analyzer.analyze_file(fixture_path)

        # Assert
        assert result is not None
        simple_func = next(f for f in result.functions if f.name == "simple_function")
        assert simple_func.cyclomatic_complexity >= 1
        assert simple_func.cognitive_complexity >= 0
        complex_func = next(f for f in result.functions if f.name == "complex_function")
        assert complex_func.cyclomatic_complexity > simple_func.cyclomatic_complexity
        assert complex_func.cognitive_complexity > simple_func.cognitive_complexity

    def test_status_calculation(self) -> None:
        """Test that status is calculated correctly."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = analyzer.analyze_file(fixture_path)

        # Assert
        assert result is not None
        assert result.status in ["OK", "MEDIUM", "HIGH"]

    def test_max_complexity_threshold(self) -> None:
        """Test analyzer with complexity threshold."""
        # Arrange
        analyzer = ComplexityAnalyzer(max_complexity=1)
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = analyzer.analyze_file(fixture_path)
        results = [result] if result is not None else []
        should_fail = analyzer.should_fail(results)

        # Assert
        assert result is not None
        assert should_fail is True

    def test_analyze_source_with_syntax_error(self) -> None:
        """Test analyzing source code with syntax errors."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        invalid_code = "def invalid_function(\n    pass"

        # Act
        result = analyzer._analyze_source("test.py", invalid_code)

        # Assert
        assert result is None

    def test_analyze_source_with_valid_code(self) -> None:
        """Test analyzing valid source code."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        valid_code = """
def simple_function():
    return 42

def function_with_condition(x):
    if x > 0:
        return x
    return 0
"""

        # Act
        result = analyzer._analyze_source("test.py", valid_code)

        # Assert
        assert result is not None
        assert len(result.functions) == 2
        assert result.functions[0].name == "simple_function"
        assert result.functions[1].name == "function_with_condition"

    def test_complexity_result_properties(self) -> None:
        """Test ComplexityResult named tuple properties."""
        # Arrange & Act
        result = ComplexityResult(
            name="test_func",
            cyclomatic_complexity=5,
            cognitive_complexity=3,
            lineno=10,
            col_offset=0,
            end_lineno=15,
            end_col_offset=10,
        )

        # Assert
        assert result.name == "test_func"
        assert result.cyclomatic_complexity == 5
        assert result.cognitive_complexity == 3
        assert result.lineno == 10
        assert result.col_offset == 0
        assert result.end_lineno == 15
        assert result.end_col_offset == 10

    def test_file_complexity_result_status_property(self) -> None:
        """Test FileComplexityResult status property."""
        # Arrange & Act - Create results with different complexity levels
        result_ok = FileComplexityResult(
            file_path="test.py",
            functions=[],
            total_cyclomatic=2,
            total_cognitive=1,
            max_cyclomatic=2,
            max_cognitive=1,
        )
        result_medium = FileComplexityResult(
            file_path="test.py",
            functions=[],
            total_cyclomatic=8,
            total_cognitive=5,
            max_cyclomatic=8,
            max_cognitive=5,
        )
        result_high = FileComplexityResult(
            file_path="test.py",
            functions=[],
            total_cyclomatic=15,
            total_cognitive=10,
            max_cyclomatic=15,
            max_cognitive=10,
        )

        # Assert
        assert result_ok.status == "OK"
        assert result_medium.status == "MEDIUM"
        assert result_high.status == "HIGH"

    def test_analyze_file_with_syntax_error(self) -> None:
        """Test analyzing a file with syntax errors."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("def broken_function(\n    # Missing closing parenthesis")
            f.flush()

            # Act
            result = analyzer.analyze_file(f.name)

            # Assert
            assert result is None

    def test_analyzer_with_max_complexity_threshold(self) -> None:
        """Test analyzer with complexity threshold for should_fail."""
        # Arrange
        analyzer = ComplexityAnalyzer(max_complexity=5)
        high_complexity_func = ComplexityResult(
            name="complex_func",
            cyclomatic_complexity=10,  # Exceeds threshold of 5
            cognitive_complexity=3,
            lineno=1,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="test.py",
            functions=[high_complexity_func],
            total_cyclomatic=10,
            total_cognitive=3,
            max_cyclomatic=10,
            max_cognitive=3,
        )

        # Act
        should_fail = analyzer.should_fail([result])

        # Assert
        assert should_fail is True, (
            f"Expected should_fail=True for complexity {result.max_cyclomatic} > threshold {analyzer.max_complexity}"
        )

    def test_analyzer_should_fail_no_threshold(self) -> None:
        """Test should_fail when no threshold is set."""
        # Arrange
        analyzer = ComplexityAnalyzer()  # No max_complexity set
        high_complexity_func = ComplexityResult(
            name="complex_func",
            cyclomatic_complexity=20,
            cognitive_complexity=15,
            lineno=1,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="test.py",
            functions=[high_complexity_func],
            total_cyclomatic=20,
            total_cognitive=15,
            max_cyclomatic=20,
            max_cognitive=15,
        )

        # Act
        should_fail = analyzer.should_fail([result])

        # Assert - Should not fail when no threshold is set
        assert should_fail is False

    def test_analyze_empty_python_file(self) -> None:
        """Test analyzing an empty Python file."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("")  # Empty file
            f.flush()

            # Act
            result = analyzer.analyze_file(f.name)

            # Assert
            assert result is not None
            assert len(result.functions) == 0
            assert result.total_cyclomatic == 0
            assert result.total_cognitive == 0
            assert result.max_cyclomatic == 0
            assert result.max_cognitive == 0

    def test_analyze_file_with_only_comments(self) -> None:
        """Test analyzing a file with only comments."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("# This is just a comment\n# Another comment\n")
            f.flush()

            # Act
            result = analyzer.analyze_file(f.name)

            # Assert
            assert result is not None
            assert len(result.functions) == 0

    def test_analyze_directory_nonexistent(self) -> None:
        """Test analyzing a directory that doesn't exist."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        # Act
        results = analyzer.analyze_directory("nonexistent_directory")

        # Assert
        assert len(results) == 0

    def test_analyze_directory_is_file(self) -> None:
        """Test analyzing a directory path that is actually a file."""
        # Arrange
        analyzer = ComplexityAnalyzer()

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("def test(): pass")
            f.flush()

            # Act - Try to analyze file as if it's a directory
            results = analyzer.analyze_directory(f.name)

            # Assert
            assert len(results) == 0
