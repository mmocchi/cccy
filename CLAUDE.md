# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses **go-task** as the task runner with **uv** for Python package management.

### Setup and Dependencies
- `task install` - Install dependencies with uv
- `task dev` - Install package in development mode

### Testing and Quality
- `task test` - Run tests with pytest
- `task lint` - Run ruff linting and mypy type checking
- `task format` - Format code with ruff
- `task format-check` - Check code formatting without changes
- `task check` - Run all checks (complexity + lint + format)

### Complexity Analysis
- `task complexity` - Analyze code complexity (show-list)
- `task complexity-summary` - Show complexity summary statistics
- `task complexity-check` - Check complexity thresholds (max cyclomatic: 10)

### Build and Clean
- `task build` - Build package with uv
- `task clean` - Clean build artifacts

### Direct pycomplex Usage
- `uv run pycomplex show-list src/` - Show complexity for all files
- `uv run pycomplex check --max-complexity 10 src/` - CI-friendly complexity check
- `uv run pycomplex show-summary src/` - Show summary statistics only
- `uv run pycomplex check` - Uses configuration from pyproject.toml
- `uv run pycomplex show-list` - Uses configuration from pyproject.toml
- `uv run pycomplex show-summary` - Uses configuration from pyproject.toml

## Configuration

pycomplex can be configured in `pyproject.toml` under the `[tool.pycomplex]` section:

```toml
[tool.pycomplex]
# Maximum complexity thresholds
max-complexity = 10
max-cognitive = 7

# File patterns to exclude (default: empty)
exclude = [
    "*/migrations/*",
    "*/venv/*",
    "*/.venv/*",
    "*/node_modules/*",
    "*/__pycache__/*",
    "*.egg-info/*",
]

# File patterns to include (default: all .py files)
# If specified, only files matching these patterns will be analyzed
include = []

# Default paths to analyze when no paths are provided
# If not specified, current directory is used
paths = ["src/"]
```

**Configuration Priority**: CLI options override configuration file settings.

## Architecture Overview

**pycomplex** is a Python complexity measurement tool that analyzes code for both Cyclomatic and Cognitive complexity.

### Core Components

1. **CLI Interface** (`cli.py`)
   - Three main commands: `check`, `show-list`, `show-summary`
   - Built with Click framework
   - Handles path analysis, exclusion patterns, and output formatting

2. **Complexity Analyzer** (`analyzer.py`)
   - `ComplexityAnalyzer` class for analyzing Python files/directories
   - Uses `mccabe` library for Cyclomatic complexity
   - Uses `cognitive-complexity` library for Cognitive complexity
   - Returns structured results via `FileComplexityResult` and `ComplexityResult` NamedTuples

3. **Output Formatters** (`formatters.py`)
   - `OutputFormatter` class with static methods for different output formats
   - Supports: table (tabulate), JSON, CSV, detailed table, and summary
   - Handles both file-level and function-level complexity reporting

### Key Data Structures

- `ComplexityResult`: Function-level complexity data (name, complexities, line info)
- `FileComplexityResult`: File-level aggregated data with status classification
- Status levels: "OK", "MEDIUM", "HIGH" based on thresholds (5/10 cyclomatic, 4/7 cognitive)

### Tool Configuration

- **Ruff**: Linting and formatting (targets Python 3.8+)
- **MyPy**: Strict type checking enabled
- **Pytest**: Testing with coverage reporting
- **Pre-commit**: Hook available for complexity checking
- **GitHub Actions**: Ready-to-use action for CI/CD integration

### Dependencies

Core runtime dependencies:
- `mccabe>=0.7.0` - Cyclomatic complexity calculation
- `cognitive-complexity>=1.3.0` - Cognitive complexity calculation
- `click>=8.0.0` - CLI framework
- `tabulate>=0.9.0` - Table formatting

Development dependencies include pytest, mypy, and ruff (see pyproject.toml).