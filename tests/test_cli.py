"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from pycomplex.cli import main


class TestCLI:
    """Test cases for the CLI interface."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(main, ["--help"])

        # Assert
        assert result.exit_code == 0, (
            f"CLI help command failed with exit code {result.exit_code}"
        )
        assert (
            "Analyze Python code for Cyclomatic and Cognitive complexity"
            in result.output
        ), "Main description not found in help output"
        assert "check" in result.output, "'check' command not found in help output"
        assert "show-list" in result.output, (
            "'show-list' command not found in help output"
        )
        assert "show-summary" in result.output, (
            "'show-summary' command not found in help output"
        )

    def test_cli_version(self) -> None:
        """Test CLI version output."""
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(main, ["--version"])

        # Assert
        assert result.exit_code == 0, (
            f"CLI version command failed with exit code {result.exit_code}"
        )

    def test_cli_analyze_file(self) -> None:
        """Test analyzing a single file."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(main, ["show-list", str(fixture_path)])

        # Assert
        assert result.exit_code == 0, (
            f"show-list command failed with exit code {result.exit_code}"
        )
        assert "simple.py" in result.output, (
            "Expected filename 'simple.py' not found in output"
        )
        assert "Cyclomatic" in result.output, (
            "'Cyclomatic' header not found in table output"
        )
        assert "Cognitive" in result.output, (
            "'Cognitive' header not found in table output"
        )
        assert "Status" in result.output, "'Status' header not found in table output"

    def test_cli_analyze_directory(self) -> None:
        """Test analyzing a directory."""
        # Arrange
        runner = CliRunner()
        fixtures_dir = Path(__file__).parent / "fixtures"

        # Act
        result = runner.invoke(main, ["show-list", str(fixtures_dir)])

        # Assert
        assert result.exit_code == 0
        assert "simple.py" in result.output

    def test_cli_json_format(self) -> None:
        """Test JSON output format."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(
            main, ["show-list", "--format", "json", str(fixture_path)]
        )

        # Assert
        assert result.exit_code == 0, (
            f"JSON format command failed with exit code {result.exit_code}"
        )
        data = json.loads(result.output)
        assert isinstance(data, list), f"Expected JSON array, got {type(data)}"
        assert len(data) >= 1, f"Expected at least 1 file result, got {len(data)}"

    def test_cli_csv_format(self) -> None:
        """Test CSV output format."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(
            main, ["show-list", "--format", "csv", str(fixture_path)]
        )

        # Assert
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert len(lines) >= 2
        assert "file_path" in lines[0]
        assert "function_name" in lines[0]

    def test_cli_detailed_format(self) -> None:
        """Test detailed table format."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(
            main, ["show-list", "--format", "detailed", str(fixture_path)]
        )

        # Assert
        assert result.exit_code == 0
        assert "simple.py" in result.output
        assert "Function" in result.output
        assert "Line" in result.output
        assert "File totals" in result.output

    def test_cli_with_max_complexity(self) -> None:
        """Test CLI with max complexity threshold."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act - Set very low threshold to trigger failure
        result = runner.invoke(
            main, ["check", "--max-complexity", "1", str(fixture_path)]
        )

        # Assert - Should exit with error code due to complex functions
        assert result.exit_code == 1

    def test_cli_with_high_max_complexity(self) -> None:
        """Test CLI with high max complexity threshold."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act - Set high threshold that shouldn't trigger failure
        result = runner.invoke(
            main,
            [
                "check",
                "--max-complexity",
                "100",
                "--max-cognitive",
                "100",
                str(fixture_path),
            ],
        )

        # Assert
        assert result.exit_code == 0

    def test_cli_verbose_output(self) -> None:
        """Test verbose output."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(main, ["show-list", "--verbose", str(fixture_path)])

        # Assert
        assert result.exit_code == 0
        assert "Analyzing:" in result.stderr or "Analyzing:" in result.output

    def test_cli_summary_output(self) -> None:
        """Test summary output."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(main, ["show-summary", str(fixture_path)])

        # Assert
        assert result.exit_code == 0
        assert "Analyzed" in result.output
        assert "files" in result.output
        assert "functions" in result.output

    def test_cli_exclude_patterns(self) -> None:
        """Test exclude patterns."""
        # Arrange
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "include.py").write_text("def test(): pass")
            (tmpdir_path / "exclude.py").write_text("def test(): pass")

            # Act
            result = runner.invoke(
                main, ["show-list", "--exclude", "exclude.py", str(tmpdir_path)]
            )

            # Assert
            assert result.exit_code == 0
            assert "include.py" in result.output
            assert "exclude.py" not in result.output

    def test_cli_no_recursive(self) -> None:
        """Test non-recursive directory analysis."""
        # Arrange
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()
            (tmpdir_path / "root.py").write_text("def root(): pass")
            (subdir / "sub.py").write_text("def sub(): pass")

            # Act
            result = runner.invoke(
                main, ["show-list", "--no-recursive", str(tmpdir_path)]
            )

            # Assert
            assert result.exit_code == 0
            assert "root.py" in result.output
            assert "sub.py" not in result.output

    def test_cli_nonexistent_file(self) -> None:
        """Test CLI with nonexistent file."""
        runner = CliRunner()

        result = runner.invoke(main, ["show-list", "nonexistent.py"])

        # Should fail because file doesn't exist
        assert result.exit_code != 0

    def test_cli_multiple_paths(self) -> None:
        """Test CLI with multiple paths."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Same file twice
        result = runner.invoke(
            main, ["show-list", str(fixture_path), str(fixture_path)]
        )

        assert result.exit_code == 0
        # Should appear twice in output
        output_lines = result.output.split("\n")
        simple_py_lines = [line for line in output_lines if "simple.py" in line]
        assert len(simple_py_lines) >= 2

    def test_cli_empty_directory(self) -> None:
        """Test CLI with empty directory."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(main, ["show-list", tmpdir])

            assert result.exit_code == 1
            assert "No Python files found" in result.output

    def test_cli_invalid_format(self) -> None:
        """Test CLI with invalid format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(
            main, ["show-list", "--format", "invalid", str(fixture_path)]
        )

        assert result.exit_code != 0
        assert "Invalid value" in result.output or "Choose from" in result.output

    def test_cli_show_functions_help(self) -> None:
        """Test show-functions help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["show-functions", "--help"])

        assert result.exit_code == 0, (
            f"show-functions help command failed with exit code {result.exit_code}"
        )
        assert "Show function-level complexity metrics" in result.output, (
            "Function-level help description not found"
        )
        assert "table" in result.output, "'table' format option not found in help"
        assert "json" in result.output, "'json' format option not found in help"
        assert "csv" in result.output, "'csv' format option not found in help"

    def test_cli_show_functions_table(self) -> None:
        """Test show-functions with table format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["show-functions", str(fixture_path)])

        assert result.exit_code == 0
        assert "simple.py" in result.output
        assert "Function" in result.output
        assert "Line" in result.output
        assert "Cyclomatic" in result.output
        assert "Cognitive" in result.output
        assert "File totals" in result.output

    def test_cli_show_functions_json(self) -> None:
        """Test show-functions with JSON format."""
        # Arrange
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Act
        result = runner.invoke(
            main, ["show-functions", "--format", "json", str(fixture_path)]
        )

        # Assert
        assert result.exit_code == 0, (
            f"show-functions JSON command failed with exit code {result.exit_code}"
        )
        data = json.loads(result.output)
        assert isinstance(data, list), (
            f"Expected JSON array for functions, got {type(data)}"
        )
        if data:
            function_item = data[0]
            assert "file_path" in function_item, (
                "Missing 'file_path' in function JSON output"
            )
            assert "function_name" in function_item, (
                "Missing 'function_name' in function JSON output"
            )
            assert "line_number" in function_item, (
                "Missing 'line_number' in function JSON output"
            )
            assert "cyclomatic_complexity" in function_item, (
                "Missing 'cyclomatic_complexity' in function JSON output"
            )
            assert "cognitive_complexity" in function_item, (
                "Missing 'cognitive_complexity' in function JSON output"
            )

    def test_cli_show_functions_csv(self) -> None:
        """Test show-functions with CSV format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(
            main, ["show-functions", "--format", "csv", str(fixture_path)]
        )

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        # Should have header
        assert len(lines) >= 1
        header = lines[0]
        assert "file_path" in header
        assert "function_name" in header
        assert "line_number" in header
        assert "cyclomatic_complexity" in header
        assert "cognitive_complexity" in header

    def test_cli_show_functions_directory(self) -> None:
        """Test show-functions with directory."""
        runner = CliRunner()
        fixtures_dir = Path(__file__).parent / "fixtures"

        result = runner.invoke(main, ["show-functions", str(fixtures_dir)])

        assert result.exit_code == 0
        assert "simple.py" in result.output

    def test_cli_show_functions_with_options(self) -> None:
        """Test show-functions with various options."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(
            main, ["show-functions", "--verbose", "--recursive", str(fixture_path)]
        )

        assert result.exit_code == 0

    def test_cli_show_functions_empty_directory(self) -> None:
        """Test show-functions with empty directory."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(main, ["show-functions", tmpdir])

            assert result.exit_code == 1
            assert "No Python files found" in result.output

    def test_cli_main_without_subcommand(self) -> None:
        """Test main command without subcommand shows help."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code == 0
        assert "Python Code Complexity Analyzer" in result.output
        assert "COMMANDS:" in result.output
