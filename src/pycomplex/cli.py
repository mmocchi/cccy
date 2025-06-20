"""Command line interface for pycomplex."""

import sys
from pathlib import Path
from typing import Optional

import click

from .analyzer import ComplexityAnalyzer
from .formatters import OutputFormatter


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def main(ctx: click.Context) -> None:
    """Python complexity measurement tool.

    Analyze Python code for Cyclomatic and Cognitive complexity.

    Examples:
        pycomplex show-list src/
        pycomplex check --max-complexity 10 src/
        pycomplex show-summary src/
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--max-complexity",
    type=int,
    required=True,
    help="Maximum allowed cyclomatic complexity",
)
@click.option(
    "--max-cognitive",
    type=int,
    help="Maximum allowed cognitive complexity (optional)",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively analyze directories (default: True)",
)
@click.option(
    "--exclude", multiple=True, help="Exclude files matching these glob patterns"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def check(
    paths: tuple,
    max_complexity: int,
    max_cognitive: Optional[int],
    recursive: bool,
    exclude: tuple,
    verbose: bool,
) -> None:
    """Check if complexity exceeds thresholds.

    Returns exit code 1 if any file exceeds the complexity thresholds.
    Only shows files that exceed the limits.

    Examples:
        pycomplex check --max-complexity 10 src/
        pycomplex check --max-complexity 10 --max-cognitive 7 src/
    """
    analyzer = ComplexityAnalyzer(max_complexity=max_complexity)

    all_results = _analyze_paths(paths, analyzer, recursive, exclude, verbose)

    if not all_results:
        click.echo("No Python files found to analyze.")
        sys.exit(1)

    # Filter files that exceed thresholds
    failed_results = []
    for result in all_results:
        exceeds_cyclomatic = result.max_cyclomatic > max_complexity
        exceeds_cognitive = max_cognitive and result.max_cognitive > max_cognitive

        if exceeds_cyclomatic or exceeds_cognitive:
            failed_results.append(result)

    if failed_results:
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
            f"\n❌ {len(failed_results)} out of {len(all_results)} files failed complexity check"
        )
        sys.exit(1)
    else:
        click.echo(f"✅ All {len(all_results)} files passed complexity check!")


@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv", "detailed"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively analyze directories (default: True)",
)
@click.option(
    "--exclude", multiple=True, help="Exclude files matching these glob patterns"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def show_list(
    paths: tuple,
    output_format: str,
    recursive: bool,
    exclude: tuple,
    verbose: bool,
) -> None:
    """Show list of files with their complexity metrics.

    Display all analyzed files with their complexity values in various formats.

    Examples:
        pycomplex show-list src/
        pycomplex show-list --format json src/
        pycomplex show-list --format detailed file.py
    """
    analyzer = ComplexityAnalyzer()
    formatter = OutputFormatter()

    all_results = _analyze_paths(paths, analyzer, recursive, exclude, verbose)

    if not all_results:
        click.echo("No Python files found to analyze.")
        sys.exit(1)

    # Sort results by file path for consistent output
    all_results.sort(key=lambda x: x.file_path)

    # Generate output
    if output_format.lower() == "table":
        output = formatter.format_table(all_results)
    elif output_format.lower() == "detailed":
        output = formatter.format_detailed_table(all_results)
    elif output_format.lower() == "json":
        output = formatter.format_json(all_results)
    elif output_format.lower() == "csv":
        output = formatter.format_csv(all_results)
    else:
        click.echo(f"Error: Unknown format '{output_format}'", err=True)
        sys.exit(1)

    click.echo(output)


@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively analyze directories (default: True)",
)
@click.option(
    "--exclude", multiple=True, help="Exclude files matching these glob patterns"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def show_summary(
    paths: tuple,
    recursive: bool,
    exclude: tuple,
    verbose: bool,
) -> None:
    """Show summary statistics only.

    Display aggregated complexity statistics for the analyzed files.

    Examples:
        pycomplex show-summary src/
        pycomplex show-summary src/ tests/
    """
    analyzer = ComplexityAnalyzer()
    formatter = OutputFormatter()

    all_results = _analyze_paths(paths, analyzer, recursive, exclude, verbose)

    if not all_results:
        click.echo("No Python files found to analyze.")
        sys.exit(1)

    # Show only summary
    summary_output = formatter.format_summary(all_results)
    click.echo(summary_output)


def _analyze_paths(
    paths: tuple,
    analyzer: ComplexityAnalyzer,
    recursive: bool,
    exclude: tuple,
    verbose: bool,
) -> list:
    """Helper function to analyze given paths."""
    all_results = []

    for path_str in paths:
        path = Path(path_str)

        if verbose:
            click.echo(f"Analyzing: {path}", err=True)

        if path.is_file():
            result = analyzer.analyze_file(path)
            if result:
                all_results.append(result)
            elif verbose:
                click.echo(
                    f"Skipped: {path} (not a Python file or parse error)", err=True
                )

        elif path.is_dir():
            results = analyzer.analyze_directory(
                path, recursive=recursive, exclude_patterns=list(exclude)
            )
            all_results.extend(results)

            if verbose:
                click.echo(f"Found {len(results)} Python files in {path}", err=True)

        else:
            click.echo(f"Error: {path} is not a file or directory", err=True)
            sys.exit(1)

    return all_results


if __name__ == "__main__":
    main()
