"""Pythonソースコードの複雑度解析モジュール。"""

import ast
from pathlib import Path
from typing import Optional, Union

from cccy.complexity_calculators import (
    CognitiveComplexityCalculator,
    CyclomaticComplexityCalculator,
)
from cccy.models import ComplexityResult, FileComplexityResult


class ComplexityAnalyzer:
    """複雑度メトリクスのためにPythonソースコードを解析します。"""

    def __init__(self, max_complexity: Optional[int] = None) -> None:
        """オプションの複雑度闾値でアナライザーを初期化します。

        Args:
            max_complexity: 許可される最大の循環的複雑度

        """
        self.max_complexity = max_complexity
        self.cyclomatic_calculator = CyclomaticComplexityCalculator()
        self.cognitive_calculator = CognitiveComplexityCalculator()

    def analyze_file(
        self, file_path: Union[str, Path]
    ) -> Optional[FileComplexityResult]:
        """単一のPythonファイルの複雑度を解析します。

        Args:
            file_path: 解析するPythonファイルのパス

        Returns:
            FileComplexityResultまたはファイルを解析できない場合はNone

        """
        file_path = Path(file_path)

        if not file_path.exists() or not file_path.is_file():
            return None

        if file_path.suffix != ".py":
            return None

        try:
            with file_path.open(encoding="utf-8") as f:
                source_code = f.read()

            return self._analyze_source(str(file_path), source_code)
        except (OSError, UnicodeDecodeError, SyntaxError):
            return None

    def analyze_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        exclude_patterns: Optional[list[str]] = None,
        include_patterns: Optional[list[str]] = None,
    ) -> list[FileComplexityResult]:
        """ディレクトリ内のすべてのPythonファイルを解析します。

        Args:
            directory: 解析するディレクトリ
            recursive: サブディレクトリも解析するかどうか
            exclude_patterns: 除外するグロブパターンのリスト
            include_patterns: 含めるグロブパターンのリスト(指定した場合、これらのみが解析される)

        Returns:
            FileComplexityResultオブジェクトのリスト

        """
        directory = Path(directory)
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or []

        if not directory.exists() or not directory.is_dir():
            return []

        files_to_analyze = self._get_python_files(
            directory, recursive, exclude_patterns, include_patterns
        )
        return self._analyze_files(files_to_analyze)

    def _get_python_files(
        self,
        directory: Path,
        recursive: bool,
        exclude_patterns: list[str],
        include_patterns: list[str],
    ) -> list[Path]:
        """ディレクトリから解析するPythonファイルのリストを取得します。

        Args:
            directory: 検索するディレクトリ
            recursive: 再帰的に検索するかどうか
            exclude_patterns: 除外するパターン
            include_patterns: 含めるパターン(指定された場合、これらのみ)

        Returns:
            解析するPythonファイルパスのリスト

        """
        pattern = "**/*.py" if recursive else "*.py"
        all_files = list(directory.glob(pattern))

        return [
            file_path
            for file_path in all_files
            if self._should_include_file(file_path, exclude_patterns, include_patterns)
        ]

    def _should_include_file(
        self, file_path: Path, exclude_patterns: list[str], include_patterns: list[str]
    ) -> bool:
        """ファイルを解析に含めるかどうかを判定します。

        Args:
            file_path: ファイルのパス
            exclude_patterns: 除外するパターン
            include_patterns: 含めるパターン(指定された場合、これらのみ)

        Returns:
            ファイルを含める必要がある場合はTrue

        """
        # 除外されたファイルをスキップ
        if any(file_path.match(pattern) for pattern in exclude_patterns):
            return False

        # インクルードパターンが指定されている場合、マッチするファイルのみを含める
        if include_patterns:
            return any(file_path.match(pattern) for pattern in include_patterns)

        return True

    def _analyze_files(self, files: list[Path]) -> list[FileComplexityResult]:
        """ファイルのリストを解析します。

        Args:
            files: 解析するファイルパスのリスト

        Returns:
            解析結果のリスト

        """
        results = []
        for file_path in files:
            result = self.analyze_file(file_path)
            if result:
                results.append(result)
        return results

    def _analyze_source(
        self, file_path: str, source_code: str
    ) -> Optional[FileComplexityResult]:
        """複雑度メトリクスのためにソースコードを解析します。

        Args:
            file_path: ソースファイルのパス
            source_code: 解析するPythonソースコード

        Returns:
            FileComplexityResultまたは解析が失敗した場合はNone

        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return None

        functions = []
        total_cyclomatic = 0
        total_cognitive = 0
        max_cyclomatic = 0
        max_cognitive = 0

        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):  # 関数と非同期関数
                # カルキュレーターを使用して循環的複雑度を計算
                cyclomatic = self.cyclomatic_calculator.calculate(node)

                # カルキュレーターを使用して認知的複雑度を計算
                cognitive = self.cognitive_calculator.calculate(node)

                result = ComplexityResult(
                    name=node.name,
                    cyclomatic_complexity=cyclomatic,
                    cognitive_complexity=cognitive,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    end_lineno=getattr(node, "end_lineno", None),
                    end_col_offset=getattr(node, "end_col_offset", None),
                )

                functions.append(result)
                total_cyclomatic += cyclomatic
                total_cognitive += cognitive
                max_cyclomatic = max(max_cyclomatic, cyclomatic)
                max_cognitive = max(max_cognitive, cognitive)

        return FileComplexityResult(
            file_path=file_path,
            functions=functions,
            total_cyclomatic=total_cyclomatic,
            total_cognitive=total_cognitive,
            max_cyclomatic=max_cyclomatic,
            max_cognitive=max_cognitive,
        )

    def should_fail(self, results: list[FileComplexityResult]) -> bool:
        """複雑度の闾値に基づいて解析が失敗すべきかどうかを判定します。

        Args:
            results: ファイル解析結果のリスト

        Returns:
            いずれかのファイルが複雑度の闾値を超えている場合はTrue

        """
        if not self.max_complexity:
            return False

        return any(result.max_cyclomatic > self.max_complexity for result in results)
