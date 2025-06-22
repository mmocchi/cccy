"""複雑度解析結果の出力フォーマッター。"""

import csv
import json
from io import StringIO

from tabulate import tabulate

from cccy.models import FileComplexityResult


class OutputFormatter:
    """複雑度解析結果の出力フォーマッター。"""

    @staticmethod
    def format_table(results: list[FileComplexityResult]) -> str:
        """結果をテーブルとしてフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            フォーマットされたテーブル文字列

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
    def format_detailed_table(results: list[FileComplexityResult]) -> str:
        """関数レベル情報を含む詳細テーブルとして結果をフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            フォーマットされた詳細テーブル文字列

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
    def format_json(results: list[FileComplexityResult]) -> str:
        """Pydanticモデルシリアライゼーションを使用して結果をJSONとしてフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            JSONフォーマットされた文字列

        """
        # Use Pydantic's model_dump and transform for legacy format compatibility
        data = []
        for result in results:
            result_dict = result.model_dump()

            # Transform functions to legacy format
            functions = []
            for func in result_dict["functions"]:
                functions.append(
                    {
                        "name": func["name"],
                        "line": func[
                            "lineno"
                        ],  # Map lineno to line for backward compatibility
                        "cyclomatic_complexity": func["cyclomatic_complexity"],
                        "cognitive_complexity": func["cognitive_complexity"],
                        "end_line": func["end_lineno"],
                    }
                )

            # Transform to legacy format for backward compatibility
            transformed = {
                "file_path": result_dict["file_path"],
                "functions": functions,
                "totals": {
                    "cyclomatic_complexity": result_dict["total_cyclomatic"],
                    "cognitive_complexity": result_dict["total_cognitive"],
                },
                "max_complexity": {
                    "cyclomatic": result_dict["max_cyclomatic"],
                    "cognitive": result_dict["max_cognitive"],
                },
                "status": result.status,  # Use property for status
            }
            data.append(transformed)
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_csv(results: list[FileComplexityResult]) -> str:
        """結果をCSVとしてフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            CSVフォーマットされた文字列

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
    def format_functions_json(results: list[FileComplexityResult]) -> str:
        """関数レベルの結果をJSONとしてフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            関数に焦点を当てたJSONフォーマットされた文字列

        """
        data = []

        for result in results:
            for func in result.functions:
                data.append(
                    {
                        "file_path": result.file_path,
                        "function_name": func.name,
                        "line_number": func.lineno,
                        "end_line_number": func.end_lineno,
                        "cyclomatic_complexity": func.cyclomatic_complexity,
                        "cognitive_complexity": func.cognitive_complexity,
                        "file_status": result.status,
                    }
                )

        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_functions_csv(results: list[FileComplexityResult]) -> str:
        """関数レベルの結果をCSVとしてフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            関数に焦点を当てたCSVフォーマットされた文字列

        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "file_path",
                "function_name",
                "line_number",
                "end_line_number",
                "cyclomatic_complexity",
                "cognitive_complexity",
                "file_status",
            ]
        )

        # Write data rows
        for result in results:
            for func in result.functions:
                writer.writerow(
                    [
                        result.file_path,
                        func.name,
                        func.lineno,
                        func.end_lineno,
                        func.cyclomatic_complexity,
                        func.cognitive_complexity,
                        result.status,
                    ]
                )

        return output.getvalue()

    @staticmethod
    def format_summary(results: list[FileComplexityResult]) -> str:
        """解析結果の要約をフォーマットします。

        Args:
            results: ファイル複雑度結果のリスト

        Returns:
            要約文字列

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
