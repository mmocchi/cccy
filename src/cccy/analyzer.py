"""Complexity analysis module for Python source code."""

import ast
from pathlib import Path
from typing import Optional, Union

from .complexity_calculators import (
    CognitiveComplexityCalculator,
    CyclomaticComplexityCalculator,
)
from .models import ComplexityResult, FileComplexityResult


class ComplexityAnalyzer:
    """Analyzes Python source code for complexity metrics."""

    def __init__(self, max_complexity: Optional[int] = None) -> None:
        """Initialize analyzer with optional complexity threshold.

        Args:
            max_complexity: Maximum allowed cyclomatic complexity

        """
        self.max_complexity = max_complexity
        self.cyclomatic_calculator = CyclomaticComplexityCalculator()
        self.cognitive_calculator = CognitiveComplexityCalculator()

    def analyze_file(
        self, file_path: Union[str, Path]
    ) -> Optional[FileComplexityResult]:
        """Analyze a single Python file for complexity.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            FileComplexityResult or None if file cannot be analyzed

        """
        file_path = Path(file_path)

        if not file_path.exists() or not file_path.is_file():
            return None

        if file_path.suffix != ".py":
            return None

        try:
            with file_path.open(encoding="utf-8") as f:
                source_code = f.read()

            return self._analyze_source(str(file_path), source_code)
        except (OSError, UnicodeDecodeError, SyntaxError):
            return None

    def analyze_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        exclude_patterns: Optional[list[str]] = None,
        include_patterns: Optional[list[str]] = None,
    ) -> list[FileComplexityResult]:
        """Analyze all Python files in a directory.

        Args:
            directory: Directory to analyze
            recursive: Whether to analyze subdirectories
            exclude_patterns: List of glob patterns to exclude
            include_patterns: List of glob patterns to include (if specified, only these will be analyzed)

        Returns:
            List of FileComplexityResult objects

        """
        directory = Path(directory)
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or []

        if not directory.exists() or not directory.is_dir():
            return []

        files_to_analyze = self._get_python_files(
            directory, recursive, exclude_patterns, include_patterns
        )
        return self._analyze_files(files_to_analyze)

    def _get_python_files(
        self,
        directory: Path,
        recursive: bool,
        exclude_patterns: list[str],
        include_patterns: list[str],
    ) -> list[Path]:
        """Get list of Python files to analyze from directory.

        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            exclude_patterns: Patterns to exclude
            include_patterns: Patterns to include (if specified, only these)

        Returns:
            List of Python file paths to analyze

        """
        pattern = "**/*.py" if recursive else "*.py"
        all_files = list(directory.glob(pattern))

        return [
            file_path
            for file_path in all_files
            if self._should_include_file(file_path, exclude_patterns, include_patterns)
        ]

    def _should_include_file(
        self, file_path: Path, exclude_patterns: list[str], include_patterns: list[str]
    ) -> bool:
        """Determine if a file should be included in analysis.

        Args:
            file_path: Path to the file
            exclude_patterns: Patterns to exclude
            include_patterns: Patterns to include (if specified, only these)

        Returns:
            True if file should be included

        """
        # Skip excluded files
        if any(file_path.match(pattern) for pattern in exclude_patterns):
            return False

        # If include patterns are specified, only include matching files
        if include_patterns:
            return any(file_path.match(pattern) for pattern in include_patterns)

        return True

    def _analyze_files(self, files: list[Path]) -> list[FileComplexityResult]:
        """Analyze a list of files.

        Args:
            files: List of file paths to analyze

        Returns:
            List of analysis results

        """
        results = []
        for file_path in files:
            result = self.analyze_file(file_path)
            if result:
                results.append(result)
        return results

    def _analyze_source(
        self, file_path: str, source_code: str
    ) -> Optional[FileComplexityResult]:
        """Analyze source code for complexity metrics.

        Args:
            file_path: Path to the source file
            source_code: Python source code to analyze

        Returns:
            FileComplexityResult or None if analysis fails

        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return None

        functions = []
        total_cyclomatic = 0
        total_cognitive = 0
        max_cyclomatic = 0
        max_cognitive = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate cyclomatic complexity using calculator
                cyclomatic = self.cyclomatic_calculator.calculate(node)

                # Calculate cognitive complexity using calculator
                cognitive = self.cognitive_calculator.calculate(node)

                result = ComplexityResult(
                    name=node.name,
                    cyclomatic_complexity=cyclomatic,
                    cognitive_complexity=cognitive,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    end_lineno=getattr(node, "end_lineno", None),
                    end_col_offset=getattr(node, "end_col_offset", None),
                )

                functions.append(result)
                total_cyclomatic += cyclomatic
                total_cognitive += cognitive
                max_cyclomatic = max(max_cyclomatic, cyclomatic)
                max_cognitive = max(max_cognitive, cognitive)

        return FileComplexityResult(
            file_path=file_path,
            functions=functions,
            total_cyclomatic=total_cyclomatic,
            total_cognitive=total_cognitive,
            max_cyclomatic=max_cyclomatic,
            max_cognitive=max_cognitive,
        )

    def should_fail(self, results: list[FileComplexityResult]) -> bool:
        """Determine if analysis should fail based on complexity thresholds.

        Args:
            results: List of file analysis results

        Returns:
            True if any file exceeds complexity threshold

        """
        if not self.max_complexity:
            return False

        return any(result.max_cyclomatic > self.max_complexity for result in results)
