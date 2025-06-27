"""CLI service interfaces for dependency injection."""

from abc import ABC, abstractmethod
from typing import Optional, Union

from cccy.domain.entities.complexity import FileComplexityResult
from cccy.domain.services.complexity_analyzer import ComplexityAnalyzer


class LoggingServiceInterface(ABC):
    """Interface for logging configuration service."""

    @abstractmethod
    def setup_logging(self, level: str) -> None:
        """Setup logging configuration."""


class ConfigServiceInterface(ABC):
    """Interface for configuration service."""

    @abstractmethod
    def load_and_merge_config(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[tuple[str, ...]] = None,
        include: Optional[tuple[str, ...]] = None,
        paths: Optional[tuple[str, ...]] = None,
    ) -> dict[str, Union[str, int, list[str], None]]:
        """Load configuration and merge with CLI options."""


class AnalyzerFactoryInterface(ABC):
    """Interface for analyzer factory service."""

    @abstractmethod
    def create_analyzer_service(
        self, max_complexity: Optional[int] = None
    ) -> tuple[ComplexityAnalyzer, "AnalyzerServiceInterface"]:
        """Create analyzer and service instances."""


class AnalyzerServiceInterface(ABC):
    """Interface for analyzer service."""

    @abstractmethod
    def analyze_paths(
        self,
        paths: tuple,
        recursive: bool = True,
        exclude_patterns: Optional[list[str]] = None,
        include_patterns: Optional[list[str]] = None,
        verbose: bool = False,
    ) -> list[FileComplexityResult]:
        """Analyze specified paths and return complexity results."""

    @abstractmethod
    def filter_failed_results(
        self,
        results: list[FileComplexityResult],
        max_complexity: int,
        max_cognitive: Optional[int] = None,
    ) -> list[FileComplexityResult]:
        """Filter results that exceed complexity thresholds."""


class OutputFormatterInterface(ABC):
    """Interface for output formatter."""

    @abstractmethod
    def format_table(self, results: list[FileComplexityResult]) -> str:
        """Format results as table."""

    @abstractmethod
    def format_detailed_table(self, results: list[FileComplexityResult]) -> str:
        """Format results as detailed table."""

    @abstractmethod
    def format_json(self, results: list[FileComplexityResult]) -> str:
        """Format results as JSON."""

    @abstractmethod
    def format_csv(self, results: list[FileComplexityResult]) -> str:
        """Format results as CSV."""

    @abstractmethod
    def format_functions_json(self, results: list[FileComplexityResult]) -> str:
        """Format function-level results as JSON."""

    @abstractmethod
    def format_functions_csv(self, results: list[FileComplexityResult]) -> str:
        """Format function-level results as CSV."""

    @abstractmethod
    def format_summary(self, results: list[FileComplexityResult]) -> str:
        """Format results summary."""


class ResultFilterInterface(ABC):
    """Interface for result filtering service."""

    @abstractmethod
    def filter_failed_results(
        self,
        results: list[FileComplexityResult],
        max_complexity: int,
        max_cognitive: Optional[int] = None,
    ) -> list[FileComplexityResult]:
        """Filter results that exceed complexity thresholds."""