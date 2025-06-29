# 実用例

## 出力フォーマット

cccyは複数の出力フォーマットをサポートしています。

### テーブル形式（デフォルト）

```bash
cccy show-list src/
```

**出力例：**

```
File                    Cyclomatic    Cognitive    Status
--------------------    ----------    ---------    ------
src/main.py                      3            2    OK
src/complex_func.py             12            8    HIGH
src/utils.py                     5            4    MEDIUM
```

### JSON形式

```bash
cccy show-list --format json src/
```

**出力例：**

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

### CSV形式

```bash
cccy show-list --format csv src/
```

**出力例：**

```csv
file_path,cyclomatic_complexity,cognitive_complexity,status
src/main.py,3,2,OK
src/complex_func.py,12,8,HIGH
src/utils.py,5,4,MEDIUM
```

### 詳細形式

```bash
cccy show-list --format detailed src/
```

**出力例：**

```
File: src/main.py (Status: OK)
  Functions:
    main (line 10): Cyclomatic=3, Cognitive=2
  Totals: Cyclomatic=3, Cognitive=2

File: src/complex_func.py (Status: HIGH)
  Functions:
    complex_function (line 5): Cyclomatic=12, Cognitive=8
    helper_func (line 25): Cyclomatic=2, Cognitive=1
  Totals: Cyclomatic=14, Cognitive=9
```

## 統計サマリー

```bash
cccy show-summary src/
```

**出力例：**

```
Complexity Summary
==================
Files analyzed: 15
Total functions: 45

Cyclomatic Complexity:
  Mean: 4.2
  Median: 3.0
  Max: 12
  Files with high complexity (>10): 2

Cognitive Complexity:
  Mean: 3.1
  Median: 2.0
  Max: 8
  Files with high complexity (>7): 1

Status Distribution:
  OK: 12 files
  MEDIUM: 2 files
  HIGH: 1 file
```

## CI/CDでの使用例

### 基本的なチェック

```bash
# 複雑度が閾値を超えた場合、終了コード1で終了
cccy check --max-complexity 10 src/
```

### 両方の複雑度をチェック

```bash
cccy check --max-complexity 10 --max-cognitive 7 src/
```

### 特定のファイルを除外

```bash
cccy check --exclude "*/tests/*" --exclude "*/migrations/*" --max-complexity 8 src/
```

## GitHub Actionsでの使用例

```yaml
name: Complexity Check

on: [push, pull_request]

jobs:
  complexity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install cccy
        run: pip install cccy
      - name: Check complexity
        run: cccy check --max-complexity 10 --max-cognitive 7 src/
```

## Pre-commitでの使用例

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/mmocchi/cccy
    rev: v0.2.0
    hooks:
      - id: cccy
        args: [--max-complexity=10, --max-cognitive=7]
```

## 設定ファイルを使った実用例

**pyproject.toml:**

```toml
[tool.cccy]
max-complexity = 8
max-cognitive = 6
exclude = [
    "*/tests/*",
    "*/migrations/*",
    "*/vendor/*",
]
paths = ["src/", "scripts/"]
```

**使用法:**

```bash
# 設定ファイルの設定を使用
cccy check

# 設定ファイルの設定を使用してリスト表示
cccy show-list

# コマンドライン引数で設定を上書き
cccy check --max-complexity 10
```

## 大規模プロジェクトでの使用例

```bash
# 段階的にチェックレベルを上げる
cccy check --max-complexity 15 --max-cognitive 10 src/  # 最初は緩く
cccy check --max-complexity 12 --max-cognitive 8 src/   # 徐々に厳しく
cccy check --max-complexity 10 --max-cognitive 7 src/   # 最終目標

# 高複雑度のファイルのみ表示
cccy show-list --format detailed src/ | grep -A 10 "Status: HIGH"

# JSON出力でスクリプト処理
cccy show-list --format json src/ | jq '.[] | select(.status == "HIGH")'
```