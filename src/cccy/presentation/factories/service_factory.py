"""Service factory for presentation layer to maintain clean architecture."""

from typing import Optional, Union

from cccy.application.services.analysis_service import AnalyzerService
from cccy.application.services.cli_facade_service import CliFacadeService
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
from cccy.infrastructure.calculators.concrete_calculators import (
    CognitiveComplexityCalculator,
    CyclomaticComplexityCalculator,
)
from cccy.infrastructure.config.manager import CccyConfig
from cccy.infrastructure.formatters.output import OutputFormatter
from cccy.infrastructure.logging.config import setup_logging


class _PresentationLoggingService(LoggingServiceInterface):
    """Logging service implementation for presentation layer."""

    def setup_logging(self, level: str) -> None:
        """Set up logging configuration."""
        setup_logging(level=level)


class _PresentationConfigService(ConfigServiceInterface):
    """Configuration service implementation for presentation layer."""

    def load_and_merge_config(
        self,
        max_complexity: Optional[int] = None,
        max_cognitive: Optional[int] = None,
        exclude: Optional[tuple[str, ...]] = None,
        include: Optional[tuple[str, ...]] = None,
        paths: Optional[tuple[str, ...]] = None,
    ) -> dict[str, Union[str, int, list[str], None]]:
        """Load and merge configuration options."""
        config = CccyConfig()
        return config.merge_with_cli_options(
            max_complexity=max_complexity,
            max_cognitive=max_cognitive,
            exclude=list(exclude) if exclude else None,
            include=list(include) if include else None,
            paths=list(paths) if paths else None,
        )


class _PresentationAnalyzerFactory(AnalyzerFactoryInterface):
    """Analyzer factory implementation for presentation layer."""

    def create_analyzer_service(
        self, max_complexity: Optional[int] = None
    ) -> tuple[ComplexityAnalyzer, AnalyzerServiceInterface]:
        """Create analyzer and service instances."""
        cyclomatic_calculator = CyclomaticComplexityCalculator()
        cognitive_calculator = CognitiveComplexityCalculator()

        analyzer = ComplexityAnalyzer(
            cyclomatic_calculator=cyclomatic_calculator,
            cognitive_calculator=cognitive_calculator,
            max_complexity=max_complexity,
        )
        service = AnalyzerService(analyzer)
        return analyzer, service


class _PresentationOutputFormatter(OutputFormatterInterface):
    """Output formatter implementation for presentation layer."""

    def __init__(self) -> None:
        """Initialize with concrete formatter."""
        self._formatter = OutputFormatter()

    def format_table(self, results: list[FileComplexityResult]) -> str:
        """Format results as table."""
        return self._formatter.format_table(results)

    def format_detailed_table(self, results: list[FileComplexityResult]) -> str:
        """Format results as detailed table."""
        return self._formatter.format_detailed_table(results)

    def format_json(self, results: list[FileComplexityResult]) -> str:
        """Format results as JSON."""
        return self._formatter.format_json(results)

    def format_csv(self, results: list[FileComplexityResult]) -> str:
        """Format results as CSV."""
        return self._formatter.format_csv(results)

    def format_functions_json(self, results: list[FileComplexityResult]) -> str:
        """Format function-level results as JSON."""
        return self._formatter.format_functions_json(results)

    def format_functions_csv(self, results: list[FileComplexityResult]) -> str:
        """Format function-level results as CSV."""
        return self._formatter.format_functions_csv(results)

    def format_summary(self, results: list[FileComplexityResult]) -> str:
        """Format results summary."""
        return self._formatter.format_summary(results)


class _PresentationResultFilter(ResultFilterInterface):
    """Result filter implementation for presentation layer."""

    def filter_failed_results(
        self,
        results: list[FileComplexityResult],
        max_complexity: int,
        max_cognitive: Optional[int] = None,
    ) -> list[FileComplexityResult]:
        """Filter results that exceed complexity thresholds."""
        failed_results = []

        for result in results:
            exceeds_cyclomatic = result.max_cyclomatic > max_complexity
            exceeds_cognitive = (
                max_cognitive is not None and result.max_cognitive > max_cognitive
            )

            if exceeds_cyclomatic or exceeds_cognitive:
                failed_results.append(result)

        return failed_results


class PresentationLayerServiceFactory:
    """Factory for creating services in presentation layer."""

    @staticmethod
    def create_cli_facade() -> CliFacadeService:
        """Create CLI facade with all dependencies."""
        return CliFacadeService(
            logging_service=_PresentationLoggingService(),
            config_service=_PresentationConfigService(),
            analyzer_factory=_PresentationAnalyzerFactory(),
            output_formatter=_PresentationOutputFormatter(),
            result_filter=_PresentationResultFilter(),
        )

    @staticmethod
    def create_logging_service() -> LoggingServiceInterface:
        """Create logging service instance."""
        return _PresentationLoggingService()

    @staticmethod
    def create_config_service() -> ConfigServiceInterface:
        """Create configuration service instance."""
        return _PresentationConfigService()

    @staticmethod
    def create_analyzer_factory() -> AnalyzerFactoryInterface:
        """Create analyzer factory instance."""
        return _PresentationAnalyzerFactory()

    @staticmethod
    def create_output_formatter() -> OutputFormatterInterface:
        """Create output formatter instance."""
        return _PresentationOutputFormatter()

    @staticmethod
    def create_result_filter() -> ResultFilterInterface:
        """Create result filter instance."""
        return _PresentationResultFilter()
