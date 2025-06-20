"""Tests for the CLI module."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from pycomplex.cli import main


class TestCLI:
    """Test cases for the CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Analyze Python code complexity" in result.output
        assert "--format" in result.output
        assert "--max-complexity" in result.output
        assert "--recursive" in result.output

    def test_cli_version(self):
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0

    def test_cli_analyze_file(self):
        """Test analyzing a single file."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, [str(fixture_path)])

        assert result.exit_code == 0
        assert "simple.py" in result.output
        assert "Cyclomatic" in result.output
        assert "Cognitive" in result.output
        assert "Status" in result.output

    def test_cli_analyze_directory(self):
        """Test analyzing a directory."""
        runner = CliRunner()
        fixtures_dir = Path(__file__).parent / "fixtures"

        result = runner.invoke(main, [str(fixtures_dir)])

        assert result.exit_code == 0
        assert "simple.py" in result.output

    def test_cli_json_format(self):
        """Test JSON output format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["--format", "json", str(fixture_path)])

        assert result.exit_code == 0
        # Should be valid JSON
        import json

        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_cli_csv_format(self):
        """Test CSV output format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["--format", "csv", str(fixture_path)])

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        # Should have header + data rows
        assert len(lines) >= 2
        assert "file_path" in lines[0]
        assert "function_name" in lines[0]

    def test_cli_detailed_format(self):
        """Test detailed table format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["--format", "detailed", str(fixture_path)])

        assert result.exit_code == 0
        assert "simple.py" in result.output
        assert "Function" in result.output
        assert "Line" in result.output
        assert "File totals" in result.output

    def test_cli_with_max_complexity(self):
        """Test CLI with max complexity threshold."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Set very low threshold to trigger failure
        result = runner.invoke(main, ["--max-complexity", "1", str(fixture_path)])

        # Should exit with error code due to complex functions
        assert result.exit_code == 1

    def test_cli_with_high_max_complexity(self):
        """Test CLI with high max complexity threshold."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Set high threshold that shouldn't trigger failure
        result = runner.invoke(main, ["--max-complexity", "100", str(fixture_path)])

        assert result.exit_code == 0

    def test_cli_verbose_output(self):
        """Test verbose output."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["--verbose", str(fixture_path)])

        assert result.exit_code == 0
        # Verbose messages go to stderr
        assert "Analyzing:" in result.stderr or "Analyzing:" in result.output

    def test_cli_summary_output(self):
        """Test summary output."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["--summary", str(fixture_path)])

        assert result.exit_code == 0
        assert "SUMMARY" in result.output
        assert "Analyzed" in result.output
        assert "files" in result.output

    def test_cli_exclude_patterns(self):
        """Test exclude patterns."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test files
            (tmpdir_path / "include.py").write_text("def test(): pass")
            (tmpdir_path / "exclude.py").write_text("def test(): pass")

            result = runner.invoke(main, ["--exclude", "exclude.py", str(tmpdir_path)])

            assert result.exit_code == 0
            assert "include.py" in result.output
            assert "exclude.py" not in result.output

    def test_cli_no_recursive(self):
        """Test non-recursive directory analysis."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()

            # Create files in different levels
            (tmpdir_path / "root.py").write_text("def root(): pass")
            (subdir / "sub.py").write_text("def sub(): pass")

            result = runner.invoke(main, ["--no-recursive", str(tmpdir_path)])

            assert result.exit_code == 0
            assert "root.py" in result.output
            # Should not include subdirectory files
            assert "sub.py" not in result.output

    def test_cli_nonexistent_file(self):
        """Test CLI with nonexistent file."""
        runner = CliRunner()

        result = runner.invoke(main, ["nonexistent.py"])

        # Should fail because file doesn't exist
        assert result.exit_code != 0

    def test_cli_multiple_paths(self):
        """Test CLI with multiple paths."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        # Same file twice
        result = runner.invoke(main, [str(fixture_path), str(fixture_path)])

        assert result.exit_code == 0
        # Should appear twice in output
        output_lines = result.output.split("\n")
        simple_py_lines = [line for line in output_lines if "simple.py" in line]
        assert len(simple_py_lines) >= 2

    def test_cli_empty_directory(self):
        """Test CLI with empty directory."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(main, [tmpdir])

            assert result.exit_code == 1
            assert "No Python files found" in result.output

    def test_cli_invalid_format(self):
        """Test CLI with invalid format."""
        runner = CliRunner()
        fixture_path = Path(__file__).parent / "fixtures" / "simple.py"

        result = runner.invoke(main, ["--format", "invalid", str(fixture_path)])

        assert result.exit_code != 0
        assert "Invalid value" in result.output or "Choose from" in result.output
