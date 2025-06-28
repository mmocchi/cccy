"""CLI共通処理とオプション定義。"""

from typing import Callable, Optional, TypeVar

import click

from cccy.presentation.cli.helpers import (
    create_analyzer_service,
    handle_no_results,
    load_and_merge_config,
)
from cccy.presentation.factories.service_factory import PresentationLayerServiceFactory
from cccy.shared.type_helpers import get_list_value, get_optional_int_value

F = TypeVar("F", bound=Callable)


def common_options(f: F) -> F:
    """共通のCLIオプションデコレーター。"""
    f = click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")(f)
    f = click.option("--log-level", default="WARNING", help="Set logging level")(f)
    f = click.option(
        "--exclude", multiple=True, help="Exclude files matching these glob patterns"
    )(f)
    f = click.option(
        "--include",
        multiple=True,
        help="Include only files matching these glob patterns",
    )(f)
    f = click.option(
        "--recursive/--no-recursive",
        default=True,
        help="Recursively analyze directories (default: True)",
    )(f)
    f = click.argument("paths", nargs=-1, type=click.Path(exists=True), required=False)(
        f
    )
    return f  # noqa: RET504


def analysis_options(f: F) -> F:
    """解析用のCLIオプションデコレーター。"""
    f = click.option(
        "--max-cognitive",
        type=int,
        help="Maximum allowed cognitive complexity (optional)",
    )(f)
    f = click.option(
        "--max-complexity",
        type=int,
        help="Maximum allowed cyclomatic complexity",
    )(f)
    return f  # noqa: RET504


def format_options(f: F) -> F:
    """フォーマット用のCLIオプションデコレーター。"""
    f = click.option(
        "--format",
        "output_format",
        type=click.Choice(["table", "json", "csv", "detailed"], case_sensitive=False),
        default="table",
        help="Output format: table|json|csv|detailed (default: table)",
    )(f)
    return f  # noqa: RET504


class CommonProcessor:
    """CLI共通処理のプロセッサー。"""

    @staticmethod
    def setup_and_load_config(
        log_level: str,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: tuple = (),
        include: tuple = (),
        paths: tuple = (),
    ) -> dict:
        """ログ設定と設定読み込みを実行します。"""
        cli_facade = PresentationLayerServiceFactory.create_cli_facade()
        cli_facade.setup_logging(level=log_level)

        return load_and_merge_config(
            max_complexity=max_complexity,
            max_cognitive=max_cognitive,
            exclude=exclude,
            include=include,
            paths=paths,
        )

    @staticmethod
    def extract_final_config(merged_config: dict) -> tuple:
        """マージされた設定から最終的なパラメータを抽出します。"""
        final_max_complexity = get_optional_int_value(merged_config["max_complexity"])
        final_max_cognitive = get_optional_int_value(merged_config["max_cognitive"])
        final_exclude = get_list_value(merged_config["exclude"])
        final_include = get_list_value(merged_config["include"])
        final_paths = get_list_value(merged_config["paths"])

        return (
            final_max_complexity,
            final_max_cognitive,
            final_exclude,
            final_include,
            final_paths,
        )

    @staticmethod
    def analyze_and_get_results(
        final_paths: list,
        recursive: bool,
        final_exclude: list,
        final_include: list,
        verbose: bool,
        max_complexity: Optional[int] = None,
    ) -> tuple:
        """解析を実行して結果を取得します。"""
        analyzer, service = create_analyzer_service(max_complexity=max_complexity)

        all_results = service.analyze_paths(
            tuple(final_paths), recursive, final_exclude, final_include, verbose
        )

        if not all_results:
            handle_no_results()

        return all_results, service
