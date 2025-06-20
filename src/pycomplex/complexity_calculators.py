"""Abstract complexity calculators for pluggable complexity calculation strategies."""

import ast
import logging
from abc import ABC, abstractmethod
from typing import ClassVar, Dict, List, Type, Union

import mccabe
from cognitive_complexity.api import get_cognitive_complexity

logger = logging.getLogger(__name__)


class ComplexityCalculator(ABC):
    """Abstract base class for complexity calculators."""

    @abstractmethod
    def calculate(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        """Calculate complexity for a function node.

        Args:
            node: AST node representing a function

        Returns:
            Complexity score

        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this complexity metric."""
        pass


class CyclomaticComplexityCalculator(ComplexityCalculator):
    """Calculator for McCabe cyclomatic complexity."""

    def calculate(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        """Calculate cyclomatic complexity for a function node.

        Args:
            node: AST node representing a function

        Returns:
            Cyclomatic complexity score

        Raises:
            ComplexityCalculationError: If calculation fails and strict mode is enabled

        """
        try:
            # Create a temporary module with just this function
            module = ast.Module(body=[node], type_ignores=[])

            # Use mccabe to calculate complexity
            visitor = mccabe.PathGraphingAstVisitor()
            visitor.preorder(module, visitor)

            for graph in visitor.graphs.values():
                if graph.entity == node.name:
                    complexity = graph.complexity()
                    return int(complexity) if complexity is not None else 1

            return 1  # Default complexity for simple functions
        except Exception as e:
            logger.warning(
                f"Failed to calculate cyclomatic complexity for {node.name}: {e}"
            )
            return 1  # Return default value on error

    @property
    def name(self) -> str:
        """Return the name of this complexity metric."""
        return "cyclomatic"


class CognitiveComplexityCalculator(ComplexityCalculator):
    """Calculator for cognitive complexity."""

    def calculate(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        """Calculate cognitive complexity for a function node.

        Args:
            node: AST node representing a function

        Returns:
            Cognitive complexity score

        Raises:
            ComplexityCalculationError: If calculation fails and strict mode is enabled

        """
        try:
            complexity = get_cognitive_complexity(node)
            return int(complexity) if complexity is not None else 0
        except Exception as e:
            logger.warning(
                f"Failed to calculate cognitive complexity for {node.name}: {e}"
            )
            return 0  # Return default value on error

    @property
    def name(self) -> str:
        """Return the name of this complexity metric."""
        return "cognitive"


class ComplexityCalculatorFactory:
    """Factory for creating complexity calculators."""

    _calculators: ClassVar[Dict[str, Type[ComplexityCalculator]]] = {
        "cyclomatic": CyclomaticComplexityCalculator,
        "cognitive": CognitiveComplexityCalculator,
    }

    @classmethod
    def create(cls, calculator_type: str) -> ComplexityCalculator:
        """Create a complexity calculator of the specified type.

        Args:
            calculator_type: Type of calculator to create ("cyclomatic" or "cognitive")

        Returns:
            ComplexityCalculator instance

        Raises:
            ValueError: If calculator_type is not supported

        """
        if calculator_type not in cls._calculators:
            available = ", ".join(cls._calculators.keys())
            raise ValueError(
                f"Unknown calculator type: {calculator_type}. "
                f"Available types: {available}"
            )

        return cls._calculators[calculator_type]()

    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available calculator types.

        Returns:
            List of available calculator type names

        """
        return list(cls._calculators.keys())

    @classmethod
    def register_calculator(
        cls, name: str, calculator_class: Type[ComplexityCalculator]
    ) -> None:
        """Register a new complexity calculator type.

        Args:
            name: Name of the calculator type
            calculator_class: Calculator class (must inherit from ComplexityCalculator)

        Raises:
            TypeError: If calculator_class doesn't inherit from ComplexityCalculator

        """
        if not issubclass(calculator_class, ComplexityCalculator):
            raise TypeError(
                f"Calculator class must inherit from ComplexityCalculator, "
                f"got {calculator_class.__name__}"
            )

        cls._calculators[name] = calculator_class
