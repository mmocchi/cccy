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
    click.echo("❌ Complexity check failed!")
    click.echo("\nFiles exceeding complexity thresholds:")

    for result in failed_results:
        click.echo(f"\n📁 {result.file_path}")
        click.echo(
            f"   Max Cyclomatic: {result.max_cyclomatic} (limit: {max_complexity})"
        )
        if max_cognitive:
            click.echo(
                f"   Max Cognitive: {result.max_cognitive} (limit: {max_cognitive})"
            )
        click.echo(f"   Status: {result.status}")

        # Show functions that exceed limits
        problem_functions = []
        for func in result.functions:
            if func.cyclomatic_complexity > max_complexity:
                problem_functions.append(
                    f"   - {func.name}() line {func.lineno}: cyclomatic={func.cyclomatic_complexity}"
                )
            elif max_cognitive and func.cognitive_complexity > max_cognitive:
                problem_functions.append(
                    f"   - {func.name}() line {func.lineno}: cognitive={func.cognitive_complexity}"
                )

        if problem_functions:
            click.echo("   Problem functions:")
            for func_info in problem_functions:
                click.echo(func_info)

    click.echo(
        f"\n❌ {len(failed_results)} out of {total_results_count} files failed complexity check"
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
