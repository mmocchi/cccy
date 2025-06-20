# pycomplex

A Python complexity measurement tool that analyzes your code for Cyclomatic and Cognitive complexity.

## Features

- **Dual Complexity Metrics**: Measures both Cyclomatic Complexity (McCabe) and Cognitive Complexity
- **Flexible Output**: Supports table, JSON, CSV, and detailed formats
- **CLI Tool**: Easy-to-use command-line interface
- **Directory Analysis**: Recursively analyze entire projects or specific directories
- **Configurable Thresholds**: Set maximum complexity limits with appropriate exit codes
- **Exclusion Patterns**: Skip files matching glob patterns
- **GitHub Actions Integration**: Ready-to-use action for CI/CD pipelines
- **Pre-commit Hook**: Integrate with pre-commit for automated checks

## Installation

### Using uv (Recommended)

```bash
uv tool install pycomplex
```

### Using pip

```bash
pip install pycomplex
```

## Usage

### Basic Usage

```bash
# Show complexity list for all files
pycomplex show-list src/

# Check if complexity exceeds thresholds (CI/CD usage)
pycomplex check --max-complexity 10 src/

# Show summary statistics only
pycomplex show-summary src/
```

### Advanced Options

```bash
# Different output formats
pycomplex show-list --format json src/
pycomplex show-list --format csv src/
pycomplex show-list --format detailed src/

# Check with both cyclomatic and cognitive thresholds
pycomplex check --max-complexity 10 --max-cognitive 7 src/

# Exclude specific patterns
pycomplex show-list --exclude "*/tests/*" --exclude "*/migrations/*" src/

# Non-recursive analysis
pycomplex show-list --no-recursive src/

# Verbose output
pycomplex show-summary --verbose src/
```

### Output Formats

#### Table Format (Default)
```
File                    Cyclomatic    Cognitive    Status
--------------------    ----------    ---------    ------
src/main.py                      3            2    OK
src/complex_func.py             12            8    HIGH
```

#### JSON Format
```json
[
  {
    "file_path": "src/main.py",
    "functions": [
      {
        "name": "main",
        "line": 10,
        "cyclomatic_complexity": 3,
        "cognitive_complexity": 2
      }
    ],
    "totals": {
      "cyclomatic_complexity": 3,
      "cognitive_complexity": 2
    },
    "max_complexity": {
      "cyclomatic": 3,
      "cognitive": 2
    },
    "status": "OK"
  }
]
```

#### Detailed Format
Shows function-level complexity for each file with totals and status.

## Development Setup

This project uses modern Python development tools:

- **mise**: Tool version management
- **uv**: Fast Python package manager
- **go-task**: Task runner

### Prerequisites

Install mise for tool management:

```bash
curl https://mise.run | sh
```

### Setup

```bash
# Clone the repository
git clone https://github.com/example/pycomplex.git
cd pycomplex

# Install tools (Python, uv, task)
mise install

# Install dependencies
task install

# Install in development mode
task dev
```

### Development Tasks

```bash
# Run tests
task test

# Run linting and type checking
task lint              # = ruff check + mypy

# Format code
task format           # = ruff format

# Check formatting without changes
task format-check     # = ruff format --check

# Analyze code complexity
task complexity       # = pycomplex show-list src/
task complexity-summary # = pycomplex show-summary src/
task complexity-check  # = pycomplex check --max-complexity 10 src/

# Run all checks (complexity + lint + format)
task check

# Build package
task build

# Clean build artifacts
task clean
```

### Subcommands

#### `pycomplex check`
CI/CD friendly command that checks complexity against thresholds and exits with error code 1 if any file exceeds limits. Only shows problematic files.

```bash
pycomplex check --max-complexity 10 src/
pycomplex check --max-complexity 10 --max-cognitive 7 src/
```

#### `pycomplex show-list`
Shows all files with their complexity metrics in various formats.

```bash
pycomplex show-list src/
pycomplex show-list --format detailed src/
```

#### `pycomplex show-summary`
Shows only aggregated statistics.

```bash
pycomplex show-summary src/
```

## GitHub Actions Integration

Use the provided GitHub Action in your workflows:

```yaml
name: Complexity Check

on: [push, pull_request]

jobs:
  complexity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: example/pycomplex@v1
        with:
          path: src/
          max-complexity: 10
          format: json
          summary: true
```

## Pre-commit Integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/example/pycomplex
    rev: v1.0.0
    hooks:
      - id: pycomplex
        args: [--max-complexity=10]
```

## Configuration

Create a `.pycomplex.toml` file in your project root:

```toml
[tool.pycomplex]
max_complexity = 10
exclude = [
    "*/tests/*",
    "*/migrations/*",
    "*/build/*"
]
format = "table"
recursive = true
```

## Complexity Thresholds

### Cyclomatic Complexity
- **1-5**: Simple, low risk
- **6-10**: Moderate complexity
- **11+**: High complexity, consider refactoring

### Cognitive Complexity
- **1-4**: Simple, low risk
- **5-7**: Moderate complexity
- **8+**: High complexity, consider refactoring

### Status Levels
- **OK**: All functions below moderate thresholds
- **MEDIUM**: Some functions in moderate complexity range
- **HIGH**: Functions exceed recommended thresholds

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `task test`
5. Run linting: `task lint`
6. Format code: `task format`
7. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Uses `mccabe` for Cyclomatic Complexity calculation
- Uses `cognitive-complexity` for Cognitive Complexity calculation
- Built with `click` for CLI interface
- Uses `tabulate` for table formatting