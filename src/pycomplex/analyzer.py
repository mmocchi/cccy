"""Complexity analysis module for Python source code."""

import ast
from pathlib import Path
from typing import List, NamedTuple, Optional, Union

import mccabe
from cognitive_complexity.api import get_cognitive_complexity


class ComplexityResult(NamedTuple):
    """Result of complexity analysis for a single function or method."""

    name: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    lineno: int
    col_offset: int
    end_lineno: Optional[int] = None
    end_col_offset: Optional[int] = None


class FileComplexityResult(NamedTuple):
    """Result of complexity analysis for a single file."""

    file_path: str
    functions: List[ComplexityResult]
    total_cyclomatic: int
    total_cognitive: int
    max_cyclomatic: int
    max_cognitive: int

    @property
    def status(self) -> str:
        """Return status based on complexity thresholds."""
        if self.max_cyclomatic > 10 or self.max_cognitive > 7:
            return "HIGH"
        elif self.max_cyclomatic > 5 or self.max_cognitive > 4:
            return "MEDIUM"
        else:
            return "OK"


class ComplexityAnalyzer:
    """Analyzes Python source code for complexity metrics."""

    def __init__(self, max_complexity: Optional[int] = None):
        """Initialize analyzer with optional complexity threshold.

        Args:
            max_complexity: Maximum allowed cyclomatic complexity
        """
        self.max_complexity = max_complexity

    def analyze_file(
        self, file_path: Union[str, Path]
    ) -> Optional[FileComplexityResult]:
        """Analyze a single Python file for complexity.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            FileComplexityResult or None if file cannot be analyzed
        """
        file_path = Path(file_path)

        if not file_path.exists() or not file_path.is_file():
            return None

        if file_path.suffix != ".py":
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                source_code = f.read()

            return self._analyze_source(str(file_path), source_code)
        except (OSError, UnicodeDecodeError, SyntaxError):
            return None

    def analyze_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
    ) -> List[FileComplexityResult]:
        """Analyze all Python files in a directory.

        Args:
            directory: Directory to analyze
            recursive: Whether to analyze subdirectories
            exclude_patterns: List of glob patterns to exclude
            include_patterns: List of glob patterns to include (if specified, only these will be analyzed)

        Returns:
            List of FileComplexityResult objects
        """
        directory = Path(directory)
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or []

        if not directory.exists() or not directory.is_dir():
            return []

        results = []
        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            # Skip excluded files
            if any(file_path.match(pattern) for pattern in exclude_patterns):
                continue
            
            # If include patterns are specified, only include matching files
            if include_patterns:
                if not any(file_path.match(pattern) for pattern in include_patterns):
                    continue

            result = self.analyze_file(file_path)
            if result:
                results.append(result)

        return results

    def _analyze_source(
        self, file_path: str, source_code: str
    ) -> Optional[FileComplexityResult]:
        """Analyze source code for complexity metrics.

        Args:
            file_path: Path to the source file
            source_code: Python source code to analyze

        Returns:
            FileComplexityResult or None if analysis fails
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return None

        functions = []
        total_cyclomatic = 0
        total_cognitive = 0
        max_cyclomatic = 0
        max_cognitive = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate cyclomatic complexity using mccabe
                cyclomatic = self._calculate_cyclomatic_complexity(node)

                # Calculate cognitive complexity
                cognitive = self._calculate_cognitive_complexity(node)

                result = ComplexityResult(
                    name=node.name,
                    cyclomatic_complexity=cyclomatic,
                    cognitive_complexity=cognitive,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    end_lineno=getattr(node, "end_lineno", None),
                    end_col_offset=getattr(node, "end_col_offset", None),
                )

                functions.append(result)
                total_cyclomatic += cyclomatic
                total_cognitive += cognitive
                max_cyclomatic = max(max_cyclomatic, cyclomatic)
                max_cognitive = max(max_cognitive, cognitive)

        return FileComplexityResult(
            file_path=file_path,
            functions=functions,
            total_cyclomatic=total_cyclomatic,
            total_cognitive=total_cognitive,
            max_cyclomatic=max_cyclomatic,
            max_cognitive=max_cognitive,
        )

    def _calculate_cyclomatic_complexity(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> int:
        """Calculate cyclomatic complexity for a function node.

        Args:
            node: AST node representing a function

        Returns:
            Cyclomatic complexity score
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
        except Exception:
            return 1

    def _calculate_cognitive_complexity(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> int:
        """Calculate cognitive complexity for a function node.

        Args:
            node: AST node representing a function

        Returns:
            Cognitive complexity score
        """
        try:
            complexity = get_cognitive_complexity(node)
            return int(complexity) if complexity is not None else 0
        except Exception:
            return 0

    def should_fail(self, results: List[FileComplexityResult]) -> bool:
        """Determine if analysis should fail based on complexity thresholds.

        Args:
            results: List of file analysis results

        Returns:
            True if any file exceeds complexity threshold
        """
        if not self.max_complexity:
            return False

        for result in results:
            if result.max_cyclomatic > self.max_complexity:
                return True

        return False
