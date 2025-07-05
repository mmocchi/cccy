"""Service layer for complexity analysis operations."""

import logging
from pathlib import Path
from typing import Optional

import click

from cccy.domain.entities.complexity import FileComplexityResult
from cccy.domain.interfaces.cli_services import AnalyzerServiceInterface
from cccy.domain.services.complexity_analyzer import ComplexityAnalyzer

logger = logging.getLogger(__name__)


class AnalyzerService(AnalyzerServiceInterface):
    """複雑度解析操作を処理するサービス。"""

    def __init__(self, analyzer: ComplexityAnalyzer) -> None:
        """アナライザーインスタンスでサービスを初期化します。

        Args:
            analyzer: 使用するComplexityAnalyzerインスタンス

        """
        self.analyzer = analyzer

    def analyze_paths(
        self,
        paths: tuple[str, ...],
        recursive: bool = True,
        exclude_patterns: Optional[list[str]] = None,
        include_patterns: Optional[list[str]] = None,
        verbose: bool = False,
    ) -> list[FileComplexityResult]:
        """指定されたパスを解析し、複雑度結果を返します。

        Args:
            paths: 解析するパスのタプル
            recursive: ディレクトリを再帰的に解析するかどうか
            exclude_patterns: 除外するグロブパターンのリスト
            include_patterns: 含めるグロブパターンのリスト
            verbose: 詳細出力を有効にする

        Returns:
            FileComplexityResultオブジェクトのリスト

        Raises:
            FileNotFoundError: 指定されたパスが存在しない場合
            PermissionError: ファイルを読み込めない場合

        """
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or []
        all_results = []

        for path_str in paths:
            path = Path(path_str)
            results = self._analyze_single_path(
                path, recursive, exclude_patterns, include_patterns, verbose
            )
            all_results.extend(results)

        return all_results

    def _analyze_single_path(
        self,
        path: Path,
        recursive: bool,
        exclude_patterns: list[str],
        include_patterns: list[str],
        verbose: bool,
    ) -> list[FileComplexityResult]:
        """単一のパス(ファイルまたはディレクトリ)を解析します。

        Args:
            path: 解析するパス
            recursive: ディレクトリを再帰的に解析するかどうか
            exclude_patterns: 除外するグロブパターンのリスト
            include_patterns: 含めるグロブパターンのリスト
            verbose: 詳細出力を有効にする

        Returns:
            FileComplexityResultオブジェクトのリスト

        """
        if verbose:
            click.echo(f"Analyzing: {path}", err=True)

        try:
            return self._process_path(
                path, recursive, exclude_patterns, include_patterns, verbose
            )
        except PermissionError as e:
            self._handle_permission_error(path, e, verbose)
            return []
        except Exception as e:
            self._handle_general_error(path, e, verbose)
            return []

    def _process_path(
        self,
        path: Path,
        recursive: bool,
        exclude_patterns: list[str],
        include_patterns: list[str],
        verbose: bool,
    ) -> list[FileComplexityResult]:
        """パスのタイプに基づいてパスを処理します。

        Args:
            path: 処理するパス
            recursive: ディレクトリを再帰的に解析するかどうか
            exclude_patterns: 除外するグロブパターンのリスト
            include_patterns: 含めるグロブパターンのリスト
            verbose: 詳細出力を有効にする

        Returns:
            FileComplexityResultオブジェクトのリスト

        Raises:
            FileNotFoundError: パスがファイルでもディレクトリでもない場合

        """
        if path.is_file():
            result = self._analyze_single_file(path, verbose)
            return [result] if result else []

        if path.is_dir():
            return self._analyze_directory(
                path, recursive, exclude_patterns, include_patterns, verbose
            )

        raise FileNotFoundError(f"Path {path} is not a file or directory")

    def _handle_permission_error(
        self, path: Path, error: PermissionError, verbose: bool
    ) -> None:
        """アクセス拒否エラーを処理します。

        Args:
            path: エラーの原因となったパス
            error: アクセス拒否エラー
            verbose: 詳細出力を表示するかどうか

        """
        logger.error(f"Permission denied accessing {path}: {error}")
        if verbose:
            click.echo(f"Error: Permission denied accessing {path}", err=True)

    def _handle_general_error(
        self, path: Path, error: Exception, verbose: bool
    ) -> None:
        """一般的な解析エラーを処理します。

        Args:
            path: エラーの原因となったパス
            error: 一般的なエラー
            verbose: 詳細出力を表示するかどうか

        """
        logger.error(f"Error analyzing {path}: {error}")
        if verbose:
            click.echo(f"Error analyzing {path}: {error}", err=True)

    def _analyze_single_file(
        self, file_path: Path, verbose: bool = False
    ) -> Optional[FileComplexityResult]:
        """単一ファイルを解析します。

        Args:
            file_path: 解析するファイルのパス
            verbose: 詳細出力を有効にする

        Returns:
            FileComplexityResultまたは解析が失敗した場合はNone

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
        exclude_patterns: list[str],
        include_patterns: list[str],
        verbose: bool = False,
    ) -> list[FileComplexityResult]:
        """ディレクトリを解析します。

        Args:
            directory: 解析するディレクトリ
            recursive: 再帰的に解析するかどうか
            exclude_patterns: 除外するグロブパターンのリスト
            include_patterns: 含めるグロブパターンのリスト
            verbose: 詳細出力を有効にする

        Returns:
            FileComplexityResultオブジェクトのリスト

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
        results: list[FileComplexityResult],
        max_complexity: int,
        max_cognitive: Optional[int] = None,
    ) -> list[FileComplexityResult]:
        """複雑度闾値を超える結果をフィルタリングします。

        Args:
            results: 解析結果のリスト
            max_complexity: 許可される最大循環的複雑度
            max_cognitive: 許可される最大認知的複雑度(オプション)

        Returns:
            闾値を超える結果のリスト

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
