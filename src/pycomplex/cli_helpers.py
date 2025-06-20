"""Helper functions for CLI operations."""

import sys
from typing import Any, Dict, List, Optional, Tuple

import click

from .analyzer import ComplexityAnalyzer
from .config import PyComplexConfig
from .formatters import OutputFormatter
from .services import AnalyzerService


def load_and_merge_config(
    max_complexity: Optional[int] = None,
    max_cognitive: Optional[int] = None,
    exclude: Optional[Tuple[str, ...]] = None,
    include: Optional[Tuple[str, ...]] = None,
    paths: Optional[Tuple[str, ...]] = None,
) -> Dict[str, Any]:
    """Load configuration and merge with CLI options.

    Args:
        max_complexity: CLI max complexity option
        max_cognitive: CLI max cognitive option
        exclude: CLI exclude patterns
        include: CLI include patterns
        paths: CLI paths

    Returns:
        Merged configuration dictionary

    """
    config = PyComplexConfig()
    return config.merge_with_cli_options(
        max_complexity=max_complexity,
        max_cognitive=max_cognitive,
        exclude=list(exclude) if exclude else None,
        include=list(include) if include else None,
        paths=list(paths) if paths else None,
    )


def create_analyzer_service(
    max_complexity: Optional[int] = None,
) -> Tuple[ComplexityAnalyzer, AnalyzerService]:
    """Create analyzer and service instances.

    Args:
        max_complexity: Maximum complexity threshold for analyzer

    Returns:
        Tuple of (ComplexityAnalyzer, AnalyzerService)

    """
    analyzer = ComplexityAnalyzer(max_complexity=max_complexity)
    service = AnalyzerService(analyzer)
    return analyzer, service


def handle_no_results() -> None:
    """Handle case when no Python files are found."""
    click.echo("No Python files found to analyze.")
    sys.exit(1)


def display_failed_results(
    failed_results: List,
    total_results_count: int,
    max_complexity: int,
    max_cognitive: Optional[int] = None,
) -> None:
    """Display results that failed complexity checks.

    Args:
        failed_results: List of results that failed checks
        total_results_count: Total number of files analyzed
        max_complexity: Maximum cyclomatic complexity threshold
        max_cognitive: Maximum cognitive complexity threshold (optional)

    """
    _display_failure_header()

    for result in failed_results:
        _display_single_failed_result(result, max_complexity, max_cognitive)

    _display_failure_summary(len(failed_results), total_results_count)


def _display_failure_header() -> None:
    """Display the header for failed complexity checks."""
    click.echo("❌ Complexity check failed!")
    click.echo("\nFiles exceeding complexity thresholds:")


def _display_single_failed_result(
    result: Any, max_complexity: int, max_cognitive: Optional[int]
) -> None:
    """Display details for a single failed result.

    Args:
        result: File complexity result that failed
        max_complexity: Maximum cyclomatic complexity threshold
        max_cognitive: Maximum cognitive complexity threshold (optional)

    """
    click.echo(f"\n📁 {result.file_path}")
    click.echo(f"   Max Cyclomatic: {result.max_cyclomatic} (limit: {max_complexity})")
    if max_cognitive:
        click.echo(f"   Max Cognitive: {result.max_cognitive} (limit: {max_cognitive})")
    click.echo(f"   Status: {result.status}")

    problem_functions = _get_problem_functions(
        result.functions, max_complexity, max_cognitive
    )
    if problem_functions:
        click.echo("   Problem functions:")
        for func_info in problem_functions:
            click.echo(func_info)


def _get_problem_functions(
    functions: Any, max_complexity: int, max_cognitive: Optional[int]
) -> List[str]:
    """Get list of functions that exceed complexity thresholds.

    Args:
        functions: List of function complexity results
        max_complexity: Maximum cyclomatic complexity threshold
        max_cognitive: Maximum cognitive complexity threshold (optional)

    Returns:
        List of formatted problem function descriptions

    """
    problem_functions = []

    for func in functions:
        if func.cyclomatic_complexity > max_complexity:
            problem_functions.append(
                f"   - {func.name}() line {func.lineno}: cyclomatic={func.cyclomatic_complexity}"
            )
        elif max_cognitive and func.cognitive_complexity > max_cognitive:
            problem_functions.append(
                f"   - {func.name}() line {func.lineno}: cognitive={func.cognitive_complexity}"
            )

    return problem_functions


def _display_failure_summary(failed_count: int, total_count: int) -> None:
    """Display summary of failed complexity checks.

    Args:
        failed_count: Number of files that failed
        total_count: Total number of files analyzed

    """
    click.echo(
        f"\n❌ {failed_count} out of {total_count} files failed complexity check"
    )


def display_success_results(total_results_count: int) -> None:
    """Display success message for complexity checks.

    Args:
        total_results_count: Total number of files that passed

    """
    click.echo(f"✅ All {total_results_count} files passed complexity check!")


def validate_required_config(merged_config: Dict[str, Any]) -> None:
    """Validate that required configuration is present.

    Args:
        merged_config: Merged configuration dictionary

    Raises:
        SystemExit: If required configuration is missing

    """
    if merged_config["max_complexity"] is None:
        click.echo(
            "Error: --max-complexity is required or must be set in pyproject.toml [tool.pycomplex] section",
            err=True,
        )
        sys.exit(1)


def format_and_display_output(
    results: List,
    output_format: str,
    formatter: OutputFormatter,
) -> None:
    """Format and display output based on specified format.

    Args:
        results: List of analysis results
        output_format: Desired output format
        formatter: OutputFormatter instance

    Raises:
        SystemExit: If unknown format is specified

    """
    # Sort results by file path for consistent output
    results.sort(key=lambda x: x.file_path)

    # Generate output
    if output_format.lower() == "table":
        output = formatter.format_table(results)
    elif output_format.lower() == "detailed":
        output = formatter.format_detailed_table(results)
    elif output_format.lower() == "json":
        output = formatter.format_json(results)
    elif output_format.lower() == "csv":
        output = formatter.format_csv(results)
    else:
        click.echo(f"Error: Unknown format '{output_format}'", err=True)
        sys.exit(1)

    click.echo(output)
