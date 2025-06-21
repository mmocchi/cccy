# cccy

Pythonコードの循環的複雑度と認知的複雑度を解析するツールです。

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
uv tool install cccy
```

### Using pip

```bash
pip install cccy
```

## Usage

### Basic Usage

```bash
# Show complexity list for all files
cccy show-list src/

# Check if complexity exceeds thresholds (CI/CD usage)
cccy check --max-complexity 10 src/

# Show summary statistics only
cccy show-summary src/
```

### Advanced Options

```bash
# Different output formats
cccy show-list --format json src/
cccy show-list --format csv src/
cccy show-list --format detailed src/

# Check with both cyclomatic and cognitive thresholds
cccy check --max-complexity 10 --max-cognitive 7 src/

# Exclude specific patterns
cccy show-list --exclude "*/tests/*" --exclude "*/migrations/*" src/

# Non-recursive analysis
cccy show-list --no-recursive src/

# Verbose output
cccy show-summary --verbose src/
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
git clone https://github.com/mmocchi/cccy.git
cd cccy

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
task complexity       # = cccy show-list src/
task complexity-summary # = cccy show-summary src/
task complexity-check  # = cccy check --max-complexity 10 src/

# Run all checks (complexity + lint + format)
task check

# Build package
task build

# Clean build artifacts
task clean
```

### Subcommands

#### `cccy check`
CI/CD friendly command that checks complexity against thresholds and exits with error code 1 if any file exceeds limits. Only shows problematic files.

```bash
cccy check --max-complexity 10 src/
cccy check --max-complexity 10 --max-cognitive 7 src/
```

#### `cccy show-list`
Shows all files with their complexity metrics in various formats.

```bash
cccy show-list src/
cccy show-list --format detailed src/
```

#### `cccy show-summary`
Shows only aggregated statistics.

```bash
cccy show-summary src/
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
      - uses: mmocchi/cccy@v1
        with:
          command: check
          paths: src/
          max-complexity: 10
          max-cognitive: 7
```

### Advanced Usage Examples

```yaml
# Show detailed complexity list with JSON output
- uses: mmocchi/cccy@v1
  with:
    command: show-list
    paths: src/ tests/
    format: json
    exclude: "*/migrations/*,*/test_*.py"
    verbose: true

# Show function-level complexity
- uses: mmocchi/cccy@v1
  with:
    command: show-functions
    paths: src/
    format: csv
    include: "*.py"

# Show summary statistics only
- uses: mmocchi/cccy@v1
  with:
    command: show-summary
    paths: src/
    verbose: true
```

### Available Inputs

- `command`: Command to run (`check`, `show-list`, `show-functions`, `show-summary`) - default: `check`
- `paths`: Paths to analyze (space-separated) - default: `.`
- `format`: Output format (`table`, `json`, `csv`, `detailed`) - for show-list/show-functions only
- `max-complexity`: Maximum cyclomatic complexity - for check command
- `max-cognitive`: Maximum cognitive complexity - for check command
- `recursive`: Recursively analyze directories (`true`/`false`) - default: `true`
- `exclude`: Exclude patterns (comma-separated glob patterns)
- `include`: Include patterns (comma-separated glob patterns)
- `verbose`: Enable verbose output (`true`/`false`) - default: `false`

## Pre-commit Integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/mmocchi/cccy
    rev: v1.0.0
    hooks:
      - id: cccy
        args: [--max-complexity=10]
```

## Configuration

Create a `.cccy.toml` file in your project root:

```toml
[tool.cccy]
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