"""Python複雑度解析ツールのコマンドラインインターフェース。"""

import sys
from typing import Optional

import click

from cccy.presentation.cli.banner import create_banner, get_main_help_text
from cccy.presentation.cli.common import (
    CommonProcessor,
    analysis_options,
    common_options,
    format_options,
)
from cccy.presentation.cli.helpers import (
    display_failed_results,
    display_success_results,
    format_and_display_output,
    validate_required_config,
)
from cccy.presentation.factories.service_factory import PresentationLayerServiceFactory


@click.group(
    invoke_without_command=True,
    help="Pythonコードの循環的複雑度と認知的複雑度を解析します",
)
@click.pass_context
@click.version_option()
def main(ctx: click.Context) -> None:  # noqa: D103
    if ctx.invoked_subcommand is None:
        # Display custom banner and help
        banner = create_banner()
        click.echo(click.style(banner, fg="cyan", bold=True))
        click.echo()
        click.echo()
        click.echo(get_main_help_text())
        click.echo()
        click.echo(ctx.get_help())


@main.command()
@analysis_options
@common_options
def check(
    paths: tuple[str, ...],
    max_complexity: Optional[int],
    max_cognitive: Optional[int],
    recursive: bool,
    exclude: tuple[str, ...],
    include: tuple[str, ...],
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
      cccy check                           # Use pyproject.toml config
      cccy check --max-complexity 10 src/ # Set threshold explicitly
      cccy check --max-cognitive 7 src/   # Add cognitive limit
      cccy check --exclude "*/tests/*"    # Exclude test files

    \b
    CONFIGURATION:
      CLI options override pyproject.toml settings.
      Use --verbose to see analysis progress.
    """
    # Setup and load configuration
    merged_config = CommonProcessor.setup_and_load_config(
        log_level, max_complexity, max_cognitive, exclude, include, paths
    )

    # Validate required configuration
    validate_required_config(merged_config)

    # Extract final configuration
    (
        final_max_complexity,
        final_max_cognitive,
        final_exclude,
        final_include,
        final_paths,
    ) = CommonProcessor.extract_final_config(merged_config)

    # Analyze and get results
    all_results, service = CommonProcessor.analyze_and_get_results(
        final_paths,
        recursive,
        final_exclude,
        final_include,
        verbose,
        final_max_complexity,
    )

    # Filter files that exceed thresholds
    if final_max_complexity is not None:
        cli_facade = PresentationLayerServiceFactory.create_cli_facade()
        failed_results = cli_facade.filter_failed_results(
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
@format_options
@common_options
def show_list(
    paths: tuple[str, ...],
    output_format: str,
    recursive: bool,
    exclude: tuple[str, ...],
    include: tuple[str, ...],
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
      cccy show-list                    # Use pyproject.toml config
      cccy show-list src/              # Analyze specific directory
      cccy show-list --format json     # JSON output for tools
      cccy show-list --format csv      # Spreadsheet-friendly
      cccy show-list --format detailed # Function-level details

    \b
    OUTPUT FORMATS:
      table      Pretty table (default)
      detailed   Function-level breakdown
      json       Machine-readable JSON
      csv        Comma-separated values
    """
    # Setup and load configuration
    merged_config = CommonProcessor.setup_and_load_config(
        log_level, exclude=exclude, include=include, paths=paths
    )

    # Extract final configuration
    (
        _,  # max_complexity not needed for show-list
        _,  # max_cognitive not needed for show-list
        final_exclude,
        final_include,
        final_paths,
    ) = CommonProcessor.extract_final_config(merged_config)

    # Analyze and get results
    all_results, _ = CommonProcessor.analyze_and_get_results(
        final_paths, recursive, final_exclude, final_include, verbose
    )

    # Format and display output
    format_and_display_output(all_results, output_format)


@main.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv"], case_sensitive=False),
    default="table",
    help="Output format: table|json|csv (default: table)",
)
@common_options
def show_functions(
    paths: tuple[str, ...],
    output_format: str,
    recursive: bool,
    exclude: tuple[str, ...],
    include: tuple[str, ...],
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
      cccy show-functions                 # Use pyproject.toml config
      cccy show-functions src/           # Analyze specific directory
      cccy show-functions --format json  # JSON output for tools
      cccy show-functions --format csv   # Spreadsheet-friendly

    \b
    OUTPUT FORMATS:
      table      Function table grouped by file (default)
      json       Machine-readable JSON with function details
      csv        Function-level CSV data
    """
    # Setup and load configuration
    merged_config = CommonProcessor.setup_and_load_config(
        log_level, exclude=exclude, include=include, paths=paths
    )

    # Extract final configuration
    (
        _,  # max_complexity not needed for show-functions
        _,  # max_cognitive not needed for show-functions
        final_exclude,
        final_include,
        final_paths,
    ) = CommonProcessor.extract_final_config(merged_config)

    # Analyze and get results
    all_results, _ = CommonProcessor.analyze_and_get_results(
        final_paths, recursive, final_exclude, final_include, verbose
    )

    cli_facade = PresentationLayerServiceFactory.create_cli_facade()
    formatter = cli_facade.get_output_formatter()

    # Format and display function-level output
    if output_format == "table":
        output = formatter.format_detailed_table(all_results)
    elif output_format == "json":
        output = formatter.format_functions_json(all_results)
    elif output_format == "csv":
        output = formatter.format_functions_csv(all_results)

    click.echo(output)


@main.command()
@common_options
def show_summary(
    paths: tuple[str, ...],
    recursive: bool,
    exclude: tuple[str, ...],
    include: tuple[str, ...],
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
      cccy show-summary              # Use pyproject.toml config
      cccy show-summary src/         # Analyze specific directory
      cccy show-summary src/ tests/  # Multiple directories

    \b
    OUTPUT INCLUDES:
      • Total files and functions analyzed
      • Status distribution (OK/MEDIUM/HIGH)
      • List of high-complexity files
      • Overall codebase health metrics
    """
    # Setup and load configuration
    merged_config = CommonProcessor.setup_and_load_config(
        log_level, exclude=exclude, include=include, paths=paths
    )

    # Extract final configuration
    (
        _,  # max_complexity not needed for show-summary
        _,  # max_cognitive not needed for show-summary
        final_exclude,
        final_include,
        final_paths,
    ) = CommonProcessor.extract_final_config(merged_config)

    # Analyze and get results
    all_results, _ = CommonProcessor.analyze_and_get_results(
        final_paths, recursive, final_exclude, final_include, verbose
    )

    cli_facade = PresentationLayerServiceFactory.create_cli_facade()
    formatter = cli_facade.get_output_formatter()

    # Show only summary
    summary_output = formatter.format_summary(all_results)
    click.echo(summary_output)


if __name__ == "__main__":
    main()
