"""Python complexity measurement tool."""

import importlib.metadata

from cccy.analyzer import ComplexityAnalyzer
from cccy.complexity_calculators import (
    CognitiveComplexityCalculator,
    ComplexityCalculator,
    ComplexityCalculatorFactory,
    CyclomaticComplexityCalculator,
)
from cccy.config import CccyConfig
from cccy.exceptions import (
    AnalysisError,
    CccyError,
    ComplexityCalculationError,
    ConfigurationError,
    DirectoryAnalysisError,
    FileAnalysisError,
)
from cccy.formatters import OutputFormatter
from cccy.models import ComplexityResult, FileComplexityResult
from cccy.services import AnalyzerService


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
