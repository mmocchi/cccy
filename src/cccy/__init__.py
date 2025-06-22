"""Python complexity measurement tool."""

import importlib.metadata

# Public API exports
from cccy.application.interfaces.calculators import ComplexityCalculator
from cccy.application.services.analysis_service import AnalyzerService
from cccy.domain.entities.complexity import ComplexityResult, FileComplexityResult
from cccy.domain.exceptions.complexity_exceptions import (
    AnalysisError,
    CccyError,
    ComplexityCalculationError,
    ConfigurationError,
    DirectoryAnalysisError,
    FileAnalysisError,
)
from cccy.domain.services.complexity_analyzer import ComplexityAnalyzer
from cccy.infrastructure.calculators.concrete_calculators import (
    CognitiveComplexityCalculator,
    ComplexityCalculatorFactory,
    CyclomaticComplexityCalculator,
)
from cccy.infrastructure.config.manager import CccyConfig
from cccy.infrastructure.formatters.output import OutputFormatter


def get_version() -> str:
    """Get the package version from metadata."""
    try:
        return importlib.metadata.version("cccy")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


__all__ = [
    "AnalysisError",
    "AnalyzerService",
    "CccyConfig",
    "CccyError",
    "CognitiveComplexityCalculator",
    "ComplexityAnalyzer",
    "ComplexityCalculationError",
    "ComplexityCalculator",
    "ComplexityCalculatorFactory",
    "ComplexityResult",
    "ConfigurationError",
    "CyclomaticComplexityCalculator",
    "DirectoryAnalysisError",
    "FileAnalysisError",
    "FileComplexityResult",
    "OutputFormatter",
    "get_version",
]
