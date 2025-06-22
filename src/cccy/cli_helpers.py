"""Helper functions for CLI operations."""

import sys
from typing import Optional, Union

import click

from cccy.analyzer import ComplexityAnalyzer
from cccy.config import CccyConfig
from cccy.formatters import OutputFormatter
from cccy.models import ComplexityResult, FileComplexityResult
from cccy.services import AnalyzerService


def load_and_merge_config(
    max_complexity: Optional[int] = None,
    max_cognitive: Optional[int] = None,
    exclude: Optional[tuple[str, ...]] = None,
    include: Optional[tuple[str, ...]] = None,
    paths: Optional[tuple[str, ...]] = None,
) -> dict[str, Union[str, int, list[str], None]]:
    """設定を読み込み、CLIオプションとマージします。

    Args:
        max_complexity: CLI最大複雑度オプション
        max_cognitive: CLI最大認知的オプション
        exclude: CLI除外パターン
        include: CLI含めるパターン
        paths: CLIパス

    Returns:
        マージされた設定辞書

    """
    config = CccyConfig()
    return config.merge_with_cli_options(
        max_complexity=max_complexity,
        max_cognitive=max_cognitive,
        exclude=list(exclude) if exclude else None,
        include=list(include) if include else None,
        paths=list(paths) if paths else None,
    )


def create_analyzer_service(
    max_complexity: Optional[int] = None,
) -> tuple[ComplexityAnalyzer, AnalyzerService]:
    """アナライザーとサービスインスタンスを作成します。

    Args:
        max_complexity: アナライザーの最大複雑度闾値

    Returns:
        (ComplexityAnalyzer, AnalyzerService)のタプル

    """
    analyzer = ComplexityAnalyzer(max_complexity=max_complexity)
    service = AnalyzerService(analyzer)
    return analyzer, service


def handle_no_results() -> None:
    """Pythonファイルが見つからない場合を処理します。"""
    click.echo("No Python files found to analyze.")
    sys.exit(1)


def display_failed_results(
    failed_results: list,
    total_results_count: int,
    max_complexity: int,
    max_cognitive: Optional[int] = None,
) -> None:
    """複雑度チェックに失敗した結果を表示します。

    Args:
        failed_results: チェックに失敗した結果のリスト
        total_results_count: 解析されたファイルの総数
        max_complexity: 最大循環的複雑度闾値
        max_cognitive: 最大認知的複雑度闾値(オプション)

    """
    _display_failure_header()

    for result in failed_results:
        _display_single_failed_result(result, max_complexity, max_cognitive)

    _display_failure_summary(len(failed_results), total_results_count)


def _display_failure_header() -> None:
    """失敗した複雑度チェックのヘッダーを表示します。"""
    click.echo("❌ Complexity check failed!")
    click.echo("\nFiles exceeding complexity thresholds:")


def _display_single_failed_result(
    result: FileComplexityResult, max_complexity: int, max_cognitive: Optional[int]
) -> None:
    """単一の失敗結果の詳細を表示します。

    Args:
        result: 失敗したファイル複雑度結果
        max_complexity: 最大循環的複雑度闾値
        max_cognitive: 最大認知的複雑度闾値(オプション)

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
    functions: list[ComplexityResult], max_complexity: int, max_cognitive: Optional[int]
) -> list[str]:
    """複雑度闾値を超える関数のリストを取得します。

    Args:
        functions: 関数複雑度結果のリスト
        max_complexity: 最大循環的複雑度闾値
        max_cognitive: 最大認知的複雑度闾値(オプション)

    Returns:
        フォーマットされた問題のある関数の説明リスト

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
    """失敗した複雑度チェックの要約を表示します。

    Args:
        failed_count: 失敗したファイルの数
        total_count: 解析されたファイルの総数

    """
    click.echo(
        f"\n❌ {failed_count} out of {total_count} files failed complexity check"
    )


def display_success_results(total_results_count: int) -> None:
    """複雑度チェックの成功メッセージを表示します。

    Args:
        total_results_count: パスしたファイルの総数

    """
    click.echo(f"✅ All {total_results_count} files passed complexity check!")


def validate_required_config(
    merged_config: dict[str, Union[str, int, list[str], None]],
) -> None:
    """必要な設定が存在することを検証します。

    Args:
        merged_config: マージされた設定辞書

    Raises:
        SystemExit: 必要な設定が缠っている場合

    """
    if merged_config["max_complexity"] is None:
        click.echo(
            "Error: --max-complexity is required or must be set in pyproject.toml [tool.cccy] section",
            err=True,
        )
        sys.exit(1)


def format_and_display_output(
    results: list,
    output_format: str,
    formatter: OutputFormatter,
) -> None:
    """指定されたフォーマットに基づいて出力をフォーマットし、表示します。

    Args:
        results: 解析結果のリスト
        output_format: 希望する出力フォーマット
        formatter: OutputFormatterインスタンス

    Raises:
        SystemExit: 不明なフォーマットが指定された場合

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
