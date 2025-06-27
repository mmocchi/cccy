"""Service factory for presentation layer to maintain clean architecture."""

from cccy.application.services.analysis_service import AnalyzerService
from cccy.application.services.cli_facade_service import CliFacadeService
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
from typing import Optional, Union
from cccy.domain.entities.complexity import FileComplexityResult


class PresentationLayerServiceFactory:
    """Factory for creating services in presentation layer."""

    @staticmethod
    def create_cli_facade() -> CliFacadeService:
        """Create CLI facade with all dependencies."""
        
        class PresentationLoggingService(LoggingServiceInterface):
            def setup_logging(self, level: str) -> None:
                setup_logging(level=level)

        class PresentationConfigService(ConfigServiceInterface):
            def load_and_merge_config(
                self,
                max_complexity: Optional[int] = None,
                max_cognitive: Optional[int] = None,
                exclude: Optional[tuple[str, ...]] = None,
                include: Optional[tuple[str, ...]] = None,
                paths: Optional[tuple[str, ...]] = None,
            ) -> dict[str, Union[str, int, list[str], None]]:
                config = CccyConfig()
                return config.merge_with_cli_options(
                    max_complexity=max_complexity,
                    max_cognitive=max_cognitive,
                    exclude=list(exclude) if exclude else None,
                    include=list(include) if include else None,
                    paths=list(paths) if paths else None,
                )

        class PresentationAnalyzerFactory(AnalyzerFactoryInterface):
            def create_analyzer_service(
                self, max_complexity: Optional[int] = None
            ) -> tuple[ComplexityAnalyzer, AnalyzerServiceInterface]:
                cyclomatic_calculator = CyclomaticComplexityCalculator()
                cognitive_calculator = CognitiveComplexityCalculator()
                
                analyzer = ComplexityAnalyzer(
                    cyclomatic_calculator=cyclomatic_calculator,
                    cognitive_calculator=cognitive_calculator,
                    max_complexity=max_complexity,
                )
                service = AnalyzerService(analyzer)
                return analyzer, service

        class PresentationOutputFormatter(OutputFormatterInterface):
            def __init__(self):
                self._formatter = OutputFormatter()

            def format_table(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_table(results)

            def format_detailed_table(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_detailed_table(results)

            def format_json(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_json(results)

            def format_csv(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_csv(results)

            def format_functions_json(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_functions_json(results)

            def format_functions_csv(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_functions_csv(results)

            def format_summary(self, results: list[FileComplexityResult]) -> str:
                return self._formatter.format_summary(results)

        class PresentationResultFilter(ResultFilterInterface):
            def filter_failed_results(
                self,
                results: list[FileComplexityResult],
                max_complexity: int,
                max_cognitive: Optional[int] = None,
            ) -> list[FileComplexityResult]:
                failed_results = []

                for result in results:
                    exceeds_cyclomatic = result.max_cyclomatic > max_complexity
                    exceeds_cognitive = (
                        max_cognitive is not None and result.max_cognitive > max_cognitive
                    )

                    if exceeds_cyclomatic or exceeds_cognitive:
                        failed_results.append(result)

                return failed_results

        return CliFacadeService(
            logging_service=PresentationLoggingService(),
            config_service=PresentationConfigService(),
            analyzer_factory=PresentationAnalyzerFactory(),
            output_formatter=PresentationOutputFormatter(),
            result_filter=PresentationResultFilter(),
        )