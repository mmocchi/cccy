"""Service layer for complexity analysis operations."""

import logging
from pathlib import Path
from typing import List, Optional

import click

from .analyzer import ComplexityAnalyzer, FileComplexityResult

logger = logging.getLogger(__name__)


class AnalyzerService:
    """Service for handling complexity analysis operations."""

    def __init__(self, analyzer: ComplexityAnalyzer) -> None:
        """Initialize the service with an analyzer instance.

        Args:
            analyzer: ComplexityAnalyzer instance to use

        """
        self.analyzer = analyzer

    def analyze_paths(
        self,
        paths: tuple,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        verbose: bool = False,
    ) -> List[FileComplexityResult]:
        """Analyze given paths and return complexity results.

        Args:
            paths: Tuple of paths to analyze
            recursive: Whether to analyze directories recursively
            exclude_patterns: List of glob patterns to exclude
            include_patterns: List of glob patterns to include
            verbose: Enable verbose output

        Returns:
            List of FileComplexityResult objects

        Raises:
            FileNotFoundError: If a specified path doesn't exist
            PermissionError: If unable to read files

        """
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or []
        all_results = []

        for path_str in paths:
            path = Path(path_str)

            if verbose:
                click.echo(f"Analyzing: {path}", err=True)

            try:
                if path.is_file():
                    result = self._analyze_single_file(path, verbose)
                    if result:
                        all_results.append(result)

                elif path.is_dir():
                    results = self._analyze_directory(
                        path, recursive, exclude_patterns, include_patterns, verbose
                    )
                    all_results.extend(results)

                else:
                    raise FileNotFoundError(f"Path {path} is not a file or directory")

            except PermissionError as e:
                logger.error(f"Permission denied accessing {path}: {e}")
                if verbose:
                    click.echo(f"Error: Permission denied accessing {path}", err=True)
                continue
            except Exception as e:
                logger.error(f"Error analyzing {path}: {e}")
                if verbose:
                    click.echo(f"Error analyzing {path}: {e}", err=True)
                continue

        return all_results

    def _analyze_single_file(
        self, file_path: Path, verbose: bool = False
    ) -> Optional[FileComplexityResult]:
        """Analyze a single file.

        Args:
            file_path: Path to the file to analyze
            verbose: Enable verbose output

        Returns:
            FileComplexityResult or None if analysis failed

        """
        try:
            result = self.analyzer.analyze_file(file_path)
            if result:
                return result
            if verbose:
                click.echo(
                    f"Skipped: {file_path} (not a Python file or parse error)", err=True
                )
            return None
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            if verbose:
                click.echo(f"Error analyzing file {file_path}: {e}", err=True)
            return None

    def _analyze_directory(
        self,
        directory: Path,
        recursive: bool,
        exclude_patterns: List[str],
        include_patterns: List[str],
        verbose: bool = False,
    ) -> List[FileComplexityResult]:
        """Analyze a directory.

        Args:
            directory: Directory to analyze
            recursive: Whether to analyze recursively
            exclude_patterns: List of glob patterns to exclude
            include_patterns: List of glob patterns to include
            verbose: Enable verbose output

        Returns:
            List of FileComplexityResult objects

        """
        try:
            results = self.analyzer.analyze_directory(
                directory,
                recursive=recursive,
                exclude_patterns=exclude_patterns,
                include_patterns=include_patterns,
            )

            if verbose:
                click.echo(
                    f"Found {len(results)} Python files in {directory}", err=True
                )

            return results
        except Exception as e:
            logger.error(f"Error analyzing directory {directory}: {e}")
            if verbose:
                click.echo(f"Error analyzing directory {directory}: {e}", err=True)
            return []

    def filter_failed_results(
        self,
        results: List[FileComplexityResult],
        max_complexity: int,
        max_cognitive: Optional[int] = None,
    ) -> List[FileComplexityResult]:
        """Filter results that exceed complexity thresholds.

        Args:
            results: List of analysis results
            max_complexity: Maximum allowed cyclomatic complexity
            max_cognitive: Maximum allowed cognitive complexity (optional)

        Returns:
            List of results that exceed thresholds

        """
        failed_results = []

        for result in results:
            exceeds_cyclomatic = result.max_cyclomatic > max_complexity
            exceeds_cognitive = (
                max_cognitive is not None and result.max_cognitive > max_cognitive
            )

            if exceeds_cyclomatic or exceeds_cognitive:
                failed_results.append(result)

        return failed_results
