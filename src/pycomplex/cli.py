"""Command line interface for pycomplex."""

import sys
from pathlib import Path
from typing import Optional

import click

from .analyzer import ComplexityAnalyzer
from .config import PyComplexConfig
from .formatters import OutputFormatter


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def main(ctx: click.Context) -> None:
    """
    \b
    ┌─────────────────────────────────────────────────────────┐
    │  ___        ___                 _                       │
    │ | _ \_  _  / __|___ _ __  _ __ | |_____ __              │
    │ |  _/ || || (__/ _ \ '  \| '_ \| / -_) \ /              │
    │ |_|  \_, | \___\___/_|_|_| .__/|_\___/_\_\              │
    │      |__/                |_|                            │
    │                                                         │
    │ Python Code Complexity Analyzer - v0.1.0                │
    │                                                         │
    └─────────────────────────────────────────────────────────┘

    \b
    Analyze Python code for Cyclomatic and Cognitive complexity.
    Enforce complexity thresholds in CI/CD pipelines.
    Configure via pyproject.toml for project-wide settings.
    
    \b
    QUICK START:
      pycomplex check                    # Use pyproject.toml config
      pycomplex show-list src/           # Analyze src/ directory
      pycomplex check --max-complexity 10 src/
    
    \b
    COMMANDS:
      check        Validate complexity thresholds (CI-friendly)
      show-list    Display detailed complexity metrics
      show-summary Show aggregated statistics
    
    \b
    CONFIGURATION:
      Add [tool.pycomplex] section to pyproject.toml
      Set max-complexity, exclude patterns, default paths, etc.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--max-complexity",
    type=int,
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
@click.option(
    "--include", multiple=True, help="Include only files matching these glob patterns"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def check(
    paths: tuple,
    max_complexity: Optional[int],
    max_cognitive: Optional[int],
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
) -> None:
    """Check if complexity exceeds thresholds (CI/CD friendly)

    \b
    PURPOSE:
      Validate code complexity against defined thresholds.
      Exit with code 1 if any violations found (perfect for CI/CD).
      Only displays files that exceed the limits.

    \b
    EXAMPLES:
      pycomplex check                           # Use pyproject.toml config
      pycomplex check --max-complexity 10 src/ # Set threshold explicitly
      pycomplex check --max-cognitive 7 src/   # Add cognitive limit
      pycomplex check --exclude "*/tests/*"    # Exclude test files

    \b
    CONFIGURATION:
      CLI options override pyproject.toml settings.
      Use --verbose to see analysis progress.
    """
    # Load configuration and merge with CLI options
    config = PyComplexConfig()
    merged_config = config.merge_with_cli_options(
        max_complexity=max_complexity,
        max_cognitive=max_cognitive,
        exclude=list(exclude) if exclude else None,
        include=list(include) if include else None,
        paths=list(paths) if paths else None,
    )
    
    # Validate required configuration
    if merged_config["max_complexity"] is None:
        click.echo("Error: --max-complexity is required or must be set in pyproject.toml [tool.pycomplex] section", err=True)
        sys.exit(1)
    
    final_max_complexity = merged_config["max_complexity"]
    final_max_cognitive = merged_config["max_cognitive"]
    final_exclude = merged_config["exclude"]
    final_include = merged_config["include"]
    final_paths = merged_config["paths"]

    analyzer = ComplexityAnalyzer(max_complexity=final_max_complexity)

    all_results = _analyze_paths(tuple(final_paths), analyzer, recursive, final_exclude, final_include, verbose)

    if not all_results:
        click.echo("No Python files found to analyze.")
        sys.exit(1)

    # Filter files that exceed thresholds
    failed_results = []
    for result in all_results:
        exceeds_cyclomatic = result.max_cyclomatic > final_max_complexity
        exceeds_cognitive = final_max_cognitive and result.max_cognitive > final_max_cognitive

        if exceeds_cyclomatic or exceeds_cognitive:
            failed_results.append(result)

    if failed_results:
        click.echo("❌ Complexity check failed!")
        click.echo("\nFiles exceeding complexity thresholds:")

        for result in failed_results:
            click.echo(f"\n📁 {result.file_path}")
            click.echo(
                f"   Max Cyclomatic: {result.max_cyclomatic} (limit: {final_max_complexity})"
            )
            if final_max_cognitive:
                click.echo(
                    f"   Max Cognitive: {result.max_cognitive} (limit: {final_max_cognitive})"
                )
            click.echo(f"   Status: {result.status}")

            # Show functions that exceed limits
            problem_functions = []
            for func in result.functions:
                if func.cyclomatic_complexity > final_max_complexity:
                    problem_functions.append(
                        f"   - {func.name}() line {func.lineno}: cyclomatic={func.cyclomatic_complexity}"
                    )
                elif final_max_cognitive and func.cognitive_complexity > final_max_cognitive:
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
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv", "detailed"], case_sensitive=False),
    default="table",
    help="Output format: table|json|csv|detailed (default: table)",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively analyze directories (default: True)",
)
@click.option(
    "--exclude", multiple=True, help="Exclude files matching these glob patterns"
)
@click.option(
    "--include", multiple=True, help="Include only files matching these glob patterns"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def show_list(
    paths: tuple,
    output_format: str,
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
) -> None:
    """Show detailed complexity metrics for all files

    \b
    PURPOSE:
      Display comprehensive complexity analysis for all files.
      Support multiple output formats for integration.
      Perfect for development and analysis workflows.

    \b
    EXAMPLES:
      pycomplex show-list                    # Use pyproject.toml config
      pycomplex show-list src/              # Analyze specific directory
      pycomplex show-list --format json     # JSON output for tools
      pycomplex show-list --format csv      # Spreadsheet-friendly
      pycomplex show-list --format detailed # Function-level details

    \b
    OUTPUT FORMATS:
      table      Pretty table (default)
      detailed   Function-level breakdown
      json       Machine-readable JSON
      csv        Comma-separated values
    """
    # Load configuration and merge with CLI options
    config = PyComplexConfig()
    merged_config = config.merge_with_cli_options(
        exclude=list(exclude) if exclude else None,
        include=list(include) if include else None,
        paths=list(paths) if paths else None,
    )
    
    final_exclude = merged_config["exclude"]
    final_include = merged_config["include"]
    final_paths = merged_config["paths"]

    analyzer = ComplexityAnalyzer()
    formatter = OutputFormatter()

    all_results = _analyze_paths(tuple(final_paths), analyzer, recursive, final_exclude, final_include, verbose)

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
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively analyze directories (default: True)",
)
@click.option(
    "--exclude", multiple=True, help="Exclude files matching these glob patterns"
)
@click.option(
    "--include", multiple=True, help="Include only files matching these glob patterns"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def show_summary(
    paths: tuple,
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
) -> None:
    """Show aggregated complexity statistics

    \b
    PURPOSE:
      Display high-level overview of codebase complexity.
      Quick health check without file-by-file details.
      Ideal for dashboards and reporting.

    \b
    EXAMPLES:
      pycomplex show-summary              # Use pyproject.toml config
      pycomplex show-summary src/         # Analyze specific directory
      pycomplex show-summary src/ tests/  # Multiple directories

    \b
    OUTPUT INCLUDES:
      • Total files and functions analyzed
      • Status distribution (OK/MEDIUM/HIGH)
      • List of high-complexity files
      • Overall codebase health metrics
    """
    # Load configuration and merge with CLI options
    config = PyComplexConfig()
    merged_config = config.merge_with_cli_options(
        exclude=list(exclude) if exclude else None,
        include=list(include) if include else None,
        paths=list(paths) if paths else None,
    )
    
    final_exclude = merged_config["exclude"]
    final_include = merged_config["include"]
    final_paths = merged_config["paths"]

    analyzer = ComplexityAnalyzer()
    formatter = OutputFormatter()

    all_results = _analyze_paths(tuple(final_paths), analyzer, recursive, final_exclude, final_include, verbose)

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
    exclude: list,
    include: list,
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
                path, recursive=recursive, exclude_patterns=exclude, include_patterns=include
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
