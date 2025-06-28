"""CLI layer facade service for clean architecture compliance."""

from typing import Optional, Union

from cccy.domain.entities.complexity import FileComplexityResult
from cccy.domain.interfaces.cli_services import (
    AnalyzerFactoryInterface,
    AnalyzerServiceInterface,
    ConfigServiceInterface,
    LoggingServiceInterface,
    OutputFormatterInterface,
    ResultFilterInterface,
)
from cccy.domain.services.complexity_analyzer import ComplexityAnalyzer


class CliFacadeService:
    """Facade service for CLI operations to maintain clean architecture."""

    def __init__(
        self,
        logging_service: LoggingServiceInterface,
        config_service: ConfigServiceInterface,
        analyzer_factory: AnalyzerFactoryInterface,
        output_formatter: OutputFormatterInterface,
        result_filter: ResultFilterInterface,
    ) -> None:
        """Initialize CLI facade with injected dependencies.

        Args:
            logging_service: Service for logging configuration
            config_service: Service for configuration management
            analyzer_factory: Factory for creating analyzer instances
            output_formatter: Service for output formatting
            result_filter: Service for filtering results

        """
        self._logging_service = logging_service
        self._config_service = config_service
        self._analyzer_factory = analyzer_factory
        self._output_formatter = output_formatter
        self._result_filter = result_filter

    def setup_logging(self, level: str) -> None:
        """Set up logging configuration.

        Args:
            level: Logging level to set

        """
        self._logging_service.setup_logging(level)

    def load_and_merge_config(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[tuple[str, ...]] = None,
        include: Optional[tuple[str, ...]] = None,
        paths: Optional[tuple[str, ...]] = None,
    ) -> dict[str, Union[str, int, list[str], None]]:
        """Load configuration and merge with CLI options.

        Args:
            max_complexity: CLI max complexity option
            max_cognitive: CLI max cognitive option
            exclude: CLI exclude patterns
            include: CLI include patterns
            paths: CLI paths

        Returns:
            Merged configuration dictionary

        """
        return self._config_service.load_and_merge_config(
            max_complexity=max_complexity,
            max_cognitive=max_cognitive,
            exclude=exclude,
            include=include,
            paths=paths,
        )

    def create_analyzer_service(
        self, max_complexity: Optional[int] = None
    ) -> tuple[ComplexityAnalyzer, AnalyzerServiceInterface]:
        """Create analyzer and service instances.

        Args:
            max_complexity: Analyzer max complexity threshold

        Returns:
            Tuple of (ComplexityAnalyzer, AnalyzerService)

        """
        return self._analyzer_factory.create_analyzer_service(max_complexity)

    def get_output_formatter(self) -> OutputFormatterInterface:
        """Get output formatter instance.

        Returns:
            OutputFormatter interface

        """
        return self._output_formatter

    def filter_failed_results(
        self,
        results: list[FileComplexityResult],
        max_complexity: int,
        max_cognitive: Optional[int] = None,
    ) -> list[FileComplexityResult]:
        """Filter results that exceed complexity thresholds.

        Args:
            results: Analysis results list
            max_complexity: Maximum allowed cyclomatic complexity
            max_cognitive: Maximum allowed cognitive complexity (optional)

        Returns:
            List of results that exceed thresholds

        """
        return self._result_filter.filter_failed_results(
            results, max_complexity, max_cognitive
        )
