"""Tests for the services module."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from pycomplex.analyzer import ComplexityAnalyzer
from pycomplex.models import ComplexityResult, FileComplexityResult
from pycomplex.services import AnalyzerService


class TestAnalyzerService:
    """Test cases for AnalysisService."""

    def test_init(self) -> None:
        """Test service initialization."""
        # Arrange
        analyzer = ComplexityAnalyzer(max_complexity=10)

        # Act
        service = AnalyzerService(analyzer)

        # Assert
        assert service.analyzer == analyzer, (
            f"Expected analyzer to be stored in service, got {service.analyzer}"
        )

    def test_analyze_paths_single_file(self) -> None:
        """Test analyzing a single file."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        results = service.analyze_paths((str(fixture_path),), True, [], [], False)

        # Assert
        assert len(results) >= 1, f"Expected at least 1 result, got {len(results)}"
        assert any("simple.py" in result.file_path for result in results), (
            f"Expected 'simple.py' in results, got: {[r.file_path for r in results]}"
        )

    def test_analyze_paths_directory(self) -> None:
        """Test analyzing a directory."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)
        fixtures_dir = Path(__file__).parent / "fixtures"

        # Act
        results = service.analyze_paths((str(fixtures_dir),), True, [], [], False)

        # Assert
        assert len(results) >= 1
        assert any("simple.py" in result.file_path for result in results)

    def test_analyze_paths_nonexistent(self) -> None:
        """Test analyzing nonexistent path."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        # Act
        results = service.analyze_paths(("nonexistent.py",), True, [], [], False)

        # Assert
        assert len(results) == 0

    def test_analyze_paths_with_exclude(self) -> None:
        """Test analyzing with exclude patterns."""
        # Arrange
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "include.py").write_text("def test(): pass")
            (tmpdir_path / "exclude.py").write_text("def test(): pass")

            # Act
            results = service.analyze_paths(
                (str(tmpdir_path),), True, ["exclude.py"], [], False
            )

            # Assert
            assert len(results) == 1
            assert "include.py" in results[0].file_path
            assert not any("exclude.py" in result.file_path for result in results)

    def test_analyze_paths_with_include(self) -> None:
        """Test analyzing with include patterns."""
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test files
            (tmpdir_path / "target.py").write_text("def test(): pass")
            (tmpdir_path / "other.py").write_text("def test(): pass")

            results = service.analyze_paths(
                (str(tmpdir_path),), True, [], ["target.py"], False
            )

            # Should only include the included file
            assert len(results) == 1
            assert "target.py" in results[0].file_path

    def test_analyze_paths_verbose(self, capsys: Any) -> None:
        """Test analyzing with verbose output."""
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"
        results = service.analyze_paths((str(fixture_path),), True, [], [], True)

        assert len(results) >= 1
        # Verbose output goes to stderr
        captured = capsys.readouterr()
        assert "Analyzing:" in captured.err

    @patch("pycomplex.services.Path.exists")
    def test_handle_permission_error(self, mock_exists: MagicMock, capsys: Any) -> None:
        """Test handling permission errors."""
        mock_exists.return_value = True

        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        # Mock a path that raises PermissionError
        with patch.object(
            service, "_process_path", side_effect=PermissionError("Access denied")
        ):
            results = service.analyze_paths(("restricted_file.py",), True, [], [], True)

            assert len(results) == 0
            captured = capsys.readouterr()
            assert "Error: Permission denied" in captured.err

    @patch("pycomplex.services.Path.exists")
    def test_handle_general_error(self, mock_exists: MagicMock, capsys: Any) -> None:
        """Test handling general errors."""
        mock_exists.return_value = True

        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        # Mock a path that raises general exception
        with patch.object(
            service, "_process_path", side_effect=Exception("General error")
        ):
            results = service.analyze_paths(("error_file.py",), True, [], [], True)

            assert len(results) == 0
            captured = capsys.readouterr()
            assert "Error analyzing" in captured.err

    def test_filter_failed_results(self) -> None:
        """Test filtering results that exceed thresholds."""
        # Arrange
        low_complexity_func = ComplexityResult(
            name="simple_func",
            cyclomatic_complexity=2,
            cognitive_complexity=1,
            lineno=10,
            col_offset=0,
        )
        high_complexity_func = ComplexityResult(
            name="complex_func",
            cyclomatic_complexity=12,
            cognitive_complexity=8,
            lineno=20,
            col_offset=0,
        )
        low_result = FileComplexityResult(
            file_path="simple.py",
            functions=[low_complexity_func],
            total_cyclomatic=2,
            total_cognitive=1,
            max_cyclomatic=2,
            max_cognitive=1,
        )
        high_result = FileComplexityResult(
            file_path="complex.py",
            functions=[high_complexity_func],
            total_cyclomatic=12,
            total_cognitive=8,
            max_cyclomatic=12,
            max_cognitive=8,
        )
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)
        all_results = [low_result, high_result]

        # Act & Assert - Test with cyclomatic threshold only
        failed_results = service.filter_failed_results(all_results, 10, None)
        assert len(failed_results) == 1
        assert failed_results[0].file_path == "complex.py"

        # Act & Assert - Test with both thresholds
        failed_results = service.filter_failed_results(all_results, 10, 5)
        assert len(failed_results) == 1
        assert failed_results[0].file_path == "complex.py"

        # Act & Assert - Test with high thresholds (no failures)
        failed_results = service.filter_failed_results(all_results, 20, 15)
        assert len(failed_results) == 0

    def test_filter_failed_results_cognitive_only(self) -> None:
        """Test filtering with cognitive complexity threshold only."""
        # Arrange
        func = ComplexityResult(
            name="cognitive_complex_func",
            cyclomatic_complexity=3,  # Low cyclomatic
            cognitive_complexity=8,  # High cognitive
            lineno=10,
            col_offset=0,
        )
        result = FileComplexityResult(
            file_path="cognitive_complex.py",
            functions=[func],
            total_cyclomatic=3,
            total_cognitive=8,
            max_cyclomatic=3,
            max_cognitive=8,
        )
        analyzer = ComplexityAnalyzer()
        service = AnalyzerService(analyzer)

        # Act
        failed_results = service.filter_failed_results([result], 10, 5)

        # Assert - Should fail on cognitive complexity
        assert len(failed_results) == 1
        assert failed_results[0].file_path == "cognitive_complex.py"
