"""Output formatters for complexity analysis results."""

import csv
import json
from io import StringIO
from typing import List

from tabulate import tabulate

from .analyzer import FileComplexityResult


class OutputFormatter:
    """Formats complexity analysis results for output."""

    @staticmethod
    def format_table(results: List[FileComplexityResult]) -> str:
        """Format results as a table.

        Args:
            results: List of file complexity results

        Returns:
            Formatted table string
        """
        if not results:
            return "No Python files analyzed."

        headers = ["File", "Cyclomatic", "Cognitive", "Status"]
        rows = []

        for result in results:
            rows.append(
                [
                    result.file_path,
                    result.max_cyclomatic,
                    result.max_cognitive,
                    result.status,
                ]
            )

        return str(tabulate(rows, headers=headers, tablefmt="grid"))

    @staticmethod
    def format_detailed_table(results: List[FileComplexityResult]) -> str:
        """Format results as a detailed table with function-level information.

        Args:
            results: List of file complexity results

        Returns:
            Formatted detailed table string
        """
        if not results:
            return "No Python files analyzed."

        output = []

        for result in results:
            output.append(f"\n=== {result.file_path} ===")

            if not result.functions:
                output.append("No functions found.")
                continue

            headers = ["Function", "Line", "Cyclomatic", "Cognitive"]
            rows = []

            for func in result.functions:
                rows.append(
                    [
                        func.name,
                        func.lineno,
                        func.cyclomatic_complexity,
                        func.cognitive_complexity,
                    ]
                )

            output.append(str(tabulate(rows, headers=headers, tablefmt="grid")))
            output.append(
                f"File totals - Cyclomatic: {result.total_cyclomatic}, "
                f"Cognitive: {result.total_cognitive}, Status: {result.status}"
            )

        return "\n".join(output)

    @staticmethod
    def format_json(results: List[FileComplexityResult]) -> str:
        """Format results as JSON.

        Args:
            results: List of file complexity results

        Returns:
            JSON formatted string
        """
        data = []

        for result in results:
            functions = []
            for func in result.functions:
                functions.append(
                    {
                        "name": func.name,
                        "line": func.lineno,
                        "cyclomatic_complexity": func.cyclomatic_complexity,
                        "cognitive_complexity": func.cognitive_complexity,
                        "end_line": func.end_lineno,
                    }
                )

            data.append(
                {
                    "file_path": result.file_path,
                    "functions": functions,
                    "totals": {
                        "cyclomatic_complexity": result.total_cyclomatic,
                        "cognitive_complexity": result.total_cognitive,
                    },
                    "max_complexity": {
                        "cyclomatic": result.max_cyclomatic,
                        "cognitive": result.max_cognitive,
                    },
                    "status": result.status,
                }
            )

        return json.dumps(data, indent=2)

    @staticmethod
    def format_csv(results: List[FileComplexityResult]) -> str:
        """Format results as CSV.

        Args:
            results: List of file complexity results

        Returns:
            CSV formatted string
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "file_path",
                "function_name",
                "line_number",
                "cyclomatic_complexity",
                "cognitive_complexity",
                "file_max_cyclomatic",
                "file_max_cognitive",
                "file_status",
            ]
        )

        # Write data rows
        for result in results:
            if result.functions:
                for func in result.functions:
                    writer.writerow(
                        [
                            result.file_path,
                            func.name,
                            func.lineno,
                            func.cyclomatic_complexity,
                            func.cognitive_complexity,
                            result.max_cyclomatic,
                            result.max_cognitive,
                            result.status,
                        ]
                    )
            else:
                # File with no functions
                writer.writerow(
                    [
                        result.file_path,
                        "",
                        "",
                        0,
                        0,
                        result.max_cyclomatic,
                        result.max_cognitive,
                        result.status,
                    ]
                )

        return output.getvalue()

    @staticmethod
    def format_summary(results: List[FileComplexityResult]) -> str:
        """Format a summary of the analysis results.

        Args:
            results: List of file complexity results

        Returns:
            Summary string
        """
        if not results:
            return "No Python files analyzed."

        total_files = len(results)
        total_functions = sum(len(result.functions) for result in results)

        status_counts = {"OK": 0, "MEDIUM": 0, "HIGH": 0}
        for result in results:
            status_counts[result.status] += 1

        high_complexity_files = [r for r in results if r.status == "HIGH"]

        summary_lines = [
            f"Analyzed {total_files} files with {total_functions} functions",
            f"Status distribution: OK: {status_counts['OK']}, "
            f"MEDIUM: {status_counts['MEDIUM']}, HIGH: {status_counts['HIGH']}",
        ]

        if high_complexity_files:
            summary_lines.append("\nHigh complexity files:")
            for result in high_complexity_files:
                summary_lines.append(
                    f"  {result.file_path} (max cyclomatic: {result.max_cyclomatic}, "
                    f"max cognitive: {result.max_cognitive})"
                )

        return "\n".join(summary_lines)
