"""Complexity calculator interfaces (ports)."""

import ast
from abc import ABC, abstractmethod
from typing import Union


class ComplexityCalculator(ABC):
    """複雑度カルキュレーターの抽象ベースクラス。"""

    @abstractmethod
    def calculate(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        """関数ノードの複雑度を計算します。

        Args:
            node: 関数を表すAST要素

        Returns:
            複雑度スコア

        """

    @property
    @abstractmethod
    def name(self) -> str:
        """この複雑度メトリクスの名前を返します。"""
