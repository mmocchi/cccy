"""Custom exceptions for cccy."""


class CccyError(Exception):
    """Base exception for cccy errors."""

    pass


class ConfigurationError(CccyError):
    """Raised when there's an issue with configuration."""

    pass


class AnalysisError(CccyError):
    """Raised when analysis fails."""

    pass


class FileAnalysisError(AnalysisError):
    """Raised when analyzing a specific file fails."""

    def __init__(self, file_path: str, message: str) -> None:
        """Initialize with file path and error message.

        Args:
            file_path: Path to the file that failed analysis
            message: Error message

        """
        self.file_path = file_path
        super().__init__(f"Error analyzing {file_path}: {message}")


class DirectoryAnalysisError(AnalysisError):
    """Raised when analyzing a directory fails."""

    def __init__(self, directory_path: str, message: str) -> None:
        """Initialize with directory path and error message.

        Args:
            directory_path: Path to the directory that failed analysis
            message: Error message

        """
        self.directory_path = directory_path
        super().__init__(f"Error analyzing directory {directory_path}: {message}")


class ComplexityCalculationError(CccyError):
    """Raised when complexity calculation fails."""

    def __init__(self, function_name: str, calculator_type: str, message: str) -> None:
        """Initialize with function details and error message.

        Args:
            function_name: Name of the function that failed
            calculator_type: Type of complexity calculator that failed
            message: Error message

        """
        self.function_name = function_name
        self.calculator_type = calculator_type
        super().__init__(
            f"Error calculating {calculator_type} complexity for {function_name}: {message}"
        )
