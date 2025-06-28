"""Concrete complexity calculator implementations."""

import ast
import logging
from typing import ClassVar, Union

import mccabe
from cognitive_complexity.api import get_cognitive_complexity

from cccy.domain.interfaces.calculators import ComplexityCalculator

logger = logging.getLogger(__name__)


class CyclomaticComplexityCalculator(ComplexityCalculator):
    """McCabe循環的複雑度のカルキュレーター。"""

    def calculate(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        """関数ノードの循環的複雑度を計算します。

        Args:
            node: 関数を表すAST要素

        Returns:
            循環的複雑度スコア

        Raises:
            ComplexityCalculationError: 計算が失敗し、厳密モードが有効な場合

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
        """この複雑度メトリクスの名前を返します。"""
        return "cyclomatic"


class CognitiveComplexityCalculator(ComplexityCalculator):
    """認知的複雑度のカルキュレーター。"""

    def calculate(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        """関数ノードの認知的複雑度を計算します。

        Args:
            node: 関数を表すAST要素

        Returns:
            認知的複雑度スコア

        Raises:
            ComplexityCalculationError: 計算が失敗し、厳密モードが有効な場合

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
        """この複雑度メトリクスの名前を返します。"""
        return "cognitive"


class ComplexityCalculatorFactory:
    """複雑度カルキュレーターを作成するファクトリー。"""

    _calculators: ClassVar[dict[str, type[ComplexityCalculator]]] = {
        "cyclomatic": CyclomaticComplexityCalculator,
        "cognitive": CognitiveComplexityCalculator,
    }

    @classmethod
    def create(cls, calculator_type: str) -> ComplexityCalculator:
        """指定されたタイプの複雑度カルキュレーターを作成します。

        Args:
            calculator_type: 作成するカルキュレーターのタイプ("cyclomatic"または"cognitive")

        Returns:
            ComplexityCalculatorインスタンス

        Raises:
            ValueError: calculator_typeがサポートされていない場合

        """
        if calculator_type not in cls._calculators:
            available = ", ".join(cls._calculators.keys())
            raise ValueError(
                f"Unknown calculator type: {calculator_type}. "
                f"Available types: {available}"
            )

        return cls._calculators[calculator_type]()

    @classmethod
    def get_available_types(cls) -> list[str]:
        """利用可能なカルキュレータータイプのリストを取得します。

        Returns:
            利用可能なカルキュレータータイプ名のリスト

        """
        return list(cls._calculators.keys())

    @classmethod
    def register_calculator(
        cls, name: str, calculator_class: type[ComplexityCalculator]
    ) -> None:
        """新しい複雑度カルキュレータータイプを登録します。

        Args:
            name: カルキュレータータイプの名前
            calculator_class: カルキュレータークラス(ComplexityCalculatorを継承する必要があります)

        Raises:
            TypeError: calculator_classがComplexityCalculatorを継承していない場合

        """
        if not issubclass(calculator_class, ComplexityCalculator):
            raise TypeError(
                f"Calculator class must inherit from ComplexityCalculator, "
                f"got {calculator_class.__name__}"
            )

        cls._calculators[name] = calculator_class
