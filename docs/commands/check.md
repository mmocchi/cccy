# cccy check

複雑度が閾値を超えているかチェックするコマンドです。CI/CDでの使用に最適化されており、問題のあるファイルが見つかった場合は終了コード1で終了します。

## 基本的な使い方

```bash
# 循環的複雑度のみチェック
cccy check --max-complexity 10 src/

# 両方の複雑度をチェック
cccy check --max-complexity 10 --max-cognitive 7 src/
```

## オプション

### 複雑度の閾値

```bash
# 循環的複雑度の最大値を設定
cccy check --max-complexity 10 src/

# 認知的複雑度の最大値を設定
cccy check --max-cognitive 7 src/

# 両方を設定
cccy check --max-complexity 10 --max-cognitive 7 src/
```

### ファイルの除外・包含

```bash
# 特定のパターンを除外
cccy check --exclude "*/tests/*" --exclude "*/migrations/*" src/

# 特定のパターンのみ包含
cccy check --include "*.py" src/

# 再帰解析を無効化
cccy check --no-recursive src/
```

## 出力例

### 問題なしの場合

```bash
$ cccy check --max-complexity 10 src/
All files passed complexity check.
$ echo $?
0
```

### 問題ありの場合

```bash
$ cccy check --max-complexity 8 src/
Files exceeding complexity thresholds:

File                    Cyclomatic    Cognitive    Status
--------------------    ----------    ---------    ------
src/complex_func.py             12            8    HIGH
src/another_complex.py          10            6    HIGH

2 files exceeded the complexity thresholds.
$ echo $?
1
```

## 終了コード

- **0**: すべてのファイルが閾値以下
- **1**: 一つ以上のファイルが閾値を超えている
- **2**: エラーが発生した（ファイルが見つからない、権限エラーなど）

## CI/CDでの使用例

### GitHub Actions

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

### GitLab CI

```yaml
complexity_check:
  stage: test
  script:
    - pip install cccy
    - cccy check --max-complexity 10 src/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## 設定ファイルとの組み合わせ

`pyproject.toml` に設定がある場合：

```toml
[tool.cccy]
max-complexity = 8
max-cognitive = 6
exclude = ["*/tests/*"]
paths = ["src/"]
```

コマンドライン引数で上書き可能：

```bash
# 設定ファイルの設定を使用
cccy check

# 閾値のみ上書き
cccy check --max-complexity 12

# パスも上書き
cccy check --max-complexity 12 src/ tests/
```

## 段階的な導入

大規模プロジェクトでは段階的に閾値を厳しくしていくことを推奨：

```bash
# Phase 1: 現状把握
cccy check --max-complexity 20 --max-cognitive 15 src/

# Phase 2: 徐々に厳しく
cccy check --max-complexity 15 --max-cognitive 12 src/

# Phase 3: 目標値
cccy check --max-complexity 10 --max-cognitive 7 src/
```