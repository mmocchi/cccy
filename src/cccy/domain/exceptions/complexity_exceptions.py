"""cccyのカスタム例外。"""


class CccyError(Exception):
    """cccyエラーのベース例外。"""

    pass


class ConfigurationError(CccyError):
    """設定に問題がある場合に発生します。"""

    pass


class AnalysisError(CccyError):
    """解析が失敗した場合に発生します。"""

    pass


class FileAnalysisError(AnalysisError):
    """特定のファイルの解析が失敗した場合に発生します。"""

    def __init__(self, file_path: str, message: str) -> None:
        """ファイルパスとエラーメッセージで初期化します。

        Args:
            file_path: 解析に失敗したファイルのパス
            message: エラーメッセージ

        """
        self.file_path = file_path
        super().__init__(f"Error analyzing {file_path}: {message}")


class DirectoryAnalysisError(AnalysisError):
    """ディレクトリの解析が失敗した場合に発生します。"""

    def __init__(self, directory_path: str, message: str) -> None:
        """ディレクトリパスとエラーメッセージで初期化します。

        Args:
            directory_path: 解析に失敗したディレクトリのパス
            message: エラーメッセージ

        """
        self.directory_path = directory_path
        super().__init__(f"Error analyzing directory {directory_path}: {message}")


class ComplexityCalculationError(CccyError):
    """複雑度計算が失敗した場合に発生します。"""

    def __init__(self, function_name: str, calculator_type: str, message: str) -> None:
        """関数の詳細とエラーメッセージで初期化します。

        Args:
            function_name: 失敗した関数の名前
            calculator_type: 失敗した複雑度カルキュレーターのタイプ
            message: エラーメッセージ

        """
        self.function_name = function_name
        self.calculator_type = calculator_type
        super().__init__(
            f"Error calculating {calculator_type} complexity for {function_name}: {message}"
        )
