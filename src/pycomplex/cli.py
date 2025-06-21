"""Command line interface for pycomplex."""

import sys
from typing import Optional

import click

from .cli_helpers import (
    create_analyzer_service,
    display_failed_results,
    display_success_results,
    format_and_display_output,
    handle_no_results,
    load_and_merge_config,
    validate_required_config,
)
from .formatters import OutputFormatter
from .logging_config import setup_logging
from .type_helpers import get_list_value, get_optional_int_value


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def main(ctx: click.Context) -> None:
    """\b
    ┌─────────────────────────────────────────────────────────┐
    │  ___        ___                 _                       │
    │ | _ \\_  _  / __|___ _ __  _ __ | |_____ __              │
    │ |  _/ || || (__/ _ \\ '  \\| '_ \\| / -_) \\ /              │
    │ |_|  \\_, | \\___\\___/_|_|_| .__/|_\\___/_\\_\\              │
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
      check          Validate complexity thresholds (CI-friendly)
      show-list      Display detailed complexity metrics
      show-functions Show function-level complexity metrics
      show-summary   Show aggregated statistics

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
@click.option("--log-level", default="WARNING", help="Set logging level")
def check(
    paths: tuple,
    max_complexity: Optional[int],
    max_cognitive: Optional[int],
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
    log_level: str,
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
    # Setup logging
    setup_logging(level=log_level)

    # Load configuration and merge with CLI options
    merged_config = load_and_merge_config(
        max_complexity=max_complexity,
        max_cognitive=max_cognitive,
        exclude=exclude,
        include=include,
        paths=paths,
    )

    # Validate required configuration
    validate_required_config(merged_config)

    final_max_complexity = get_optional_int_value(merged_config["max_complexity"])
    final_max_cognitive = get_optional_int_value(merged_config["max_cognitive"])
    final_exclude = get_list_value(merged_config["exclude"])
    final_include = get_list_value(merged_config["include"])
    final_paths = get_list_value(merged_config["paths"])

    # Create analyzer and service
    analyzer, service = create_analyzer_service(max_complexity=final_max_complexity)

    # Analyze paths
    all_results = service.analyze_paths(
        tuple(final_paths), recursive, final_exclude, final_include, verbose
    )

    if not all_results:
        handle_no_results()

    # Filter files that exceed thresholds
    if final_max_complexity is not None:
        failed_results = service.filter_failed_results(
            all_results, final_max_complexity, final_max_cognitive
        )

        if failed_results:
            display_failed_results(
                failed_results,
                len(all_results),
                final_max_complexity,
                final_max_cognitive,
            )
            sys.exit(1)
        else:
            display_success_results(len(all_results))
    else:
        display_success_results(len(all_results))


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
@click.option("--log-level", default="WARNING", help="Set logging level")
def show_list(
    paths: tuple,
    output_format: str,
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
    log_level: str,
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
    # Setup logging
    setup_logging(level=log_level)

    # Load configuration and merge with CLI options
    merged_config = load_and_merge_config(
        exclude=exclude,
        include=include,
        paths=paths,
    )

    final_exclude = get_list_value(merged_config["exclude"])
    final_include = get_list_value(merged_config["include"])
    final_paths = get_list_value(merged_config["paths"])

    # Create analyzer and service
    analyzer, service = create_analyzer_service()
    formatter = OutputFormatter()

    # Analyze paths
    all_results = service.analyze_paths(
        tuple(final_paths), recursive, final_exclude, final_include, verbose
    )

    if not all_results:
        handle_no_results()

    # Format and display output
    format_and_display_output(all_results, output_format, formatter)


@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv"], case_sensitive=False),
    default="table",
    help="Output format: table|json|csv (default: table)",
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
@click.option("--log-level", default="WARNING", help="Set logging level")
def show_functions(
    paths: tuple,
    output_format: str,
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
    log_level: str,
) -> None:
    """Show function-level complexity metrics

    \b
    PURPOSE:
      Display complexity metrics for individual functions and methods.
      Focus on function-level details rather than file-level summaries.
      Perfect for identifying specific functions that need refactoring.

    \b
    EXAMPLES:
      pycomplex show-functions                 # Use pyproject.toml config
      pycomplex show-functions src/           # Analyze specific directory
      pycomplex show-functions --format json  # JSON output for tools
      pycomplex show-functions --format csv   # Spreadsheet-friendly

    \b
    OUTPUT FORMATS:
      table      Function table grouped by file (default)
      json       Machine-readable JSON with function details
      csv        Function-level CSV data
    """
    # Setup logging
    setup_logging(level=log_level)

    # Load configuration and merge with CLI options
    merged_config = load_and_merge_config(
        exclude=exclude,
        include=include,
        paths=paths,
    )

    final_exclude = get_list_value(merged_config["exclude"])
    final_include = get_list_value(merged_config["include"])
    final_paths = get_list_value(merged_config["paths"])

    # Create analyzer and service
    analyzer, service = create_analyzer_service()
    formatter = OutputFormatter()

    # Analyze paths
    all_results = service.analyze_paths(
        tuple(final_paths), recursive, final_exclude, final_include, verbose
    )

    if not all_results:
        handle_no_results()

    # Format and display function-level output
    if output_format == "table":
        output = formatter.format_detailed_table(all_results)
    elif output_format == "json":
        output = formatter.format_functions_json(all_results)
    elif output_format == "csv":
        output = formatter.format_functions_csv(all_results)

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
@click.option("--log-level", default="WARNING", help="Set logging level")
def show_summary(
    paths: tuple,
    recursive: bool,
    exclude: tuple,
    include: tuple,
    verbose: bool,
    log_level: str,
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
    # Setup logging
    setup_logging(level=log_level)

    # Load configuration and merge with CLI options
    merged_config = load_and_merge_config(
        exclude=exclude,
        include=include,
        paths=paths,
    )

    final_exclude = get_list_value(merged_config["exclude"])
    final_include = get_list_value(merged_config["include"])
    final_paths = get_list_value(merged_config["paths"])

    # Create analyzer and service
    analyzer, service = create_analyzer_service()
    formatter = OutputFormatter()

    # Analyze paths
    all_results = service.analyze_paths(
        tuple(final_paths), recursive, final_exclude, final_include, verbose
    )

    if not all_results:
        handle_no_results()

    # Show only summary
    summary_output = formatter.format_summary(all_results)
    click.echo(summary_output)


if __name__ == "__main__":
    main()
