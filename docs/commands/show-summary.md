# cccy show-summary

プロジェクト全体の複雑度統計を要約して表示するコマンドです。個別ファイルの詳細ではなく、プロジェクト全体の傾向を把握するのに適しています。

## 基本的な使い方

```bash
# 基本的な使用法
cccy show-summary src/

# カレントディレクトリを解析
cccy show-summary .

# 複数のディレクトリを解析
cccy show-summary src/ tests/
```

## 出力例

### 基本的な出力

```bash
$ cccy show-summary src/
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

### 詳細な出力

```bash
cccy show-summary --verbose src/
```

**出力例：**

```
Complexity Summary (Verbose)
============================
Files analyzed: 15
Total functions: 45
Total lines of code: 1,250

Cyclomatic Complexity:
  Mean: 4.2
  Median: 3.0
  Standard Deviation: 2.8
  Min: 1
  Max: 12
  75th percentile: 6
  95th percentile: 10
  Files with complexity > 5: 8 (53.3%)
  Files with complexity > 10: 2 (13.3%)

Cognitive Complexity:
  Mean: 3.1
  Median: 2.0
  Standard Deviation: 2.1
  Min: 1
  Max: 8
  75th percentile: 4
  95th percentile: 7
  Files with complexity > 4: 5 (33.3%)
  Files with complexity > 7: 1 (6.7%)

Status Distribution:
  OK: 12 files (80.0%)
  MEDIUM: 2 files (13.3%)
  HIGH: 1 file (6.7%)

Top 5 Most Complex Files:
  1. src/complex_module.py (Cyclomatic: 12, Cognitive: 8)
  2. src/parser.py (Cyclomatic: 10, Cognitive: 6)
  3. src/analyzer.py (Cyclomatic: 8, Cognitive: 5)
  4. src/formatter.py (Cyclomatic: 7, Cognitive: 4)
  5. src/utils.py (Cyclomatic: 6, Cognitive: 4)
```

## オプション

### ファイルの除外・包含

```bash
# 特定のパターンを除外
cccy show-summary --exclude "*/tests/*" --exclude "*/migrations/*" src/

# 特定のパターンのみ包含
cccy show-summary --include "*.py" src/

# 再帰解析を無効化
cccy show-summary --no-recursive src/
```

### 詳細度の調整

```bash
# 詳細情報を表示
cccy show-summary --verbose src/

# 簡潔な出力（将来のオプション）
cccy show-summary --quiet src/
```

## 実用例

### プロジェクトの健全性チェック

```bash
#!/bin/bash

# 複雑度サマリーを取得
SUMMARY=$(cccy show-summary --verbose src/)

# 高複雑度ファイルの割合をチェック
HIGH_RATIO=$(echo "$SUMMARY" | grep "Files with complexity > 10:" | grep -o '[0-9.]*%' | grep -o '[0-9.]*')

if (( $(echo "$HIGH_RATIO > 20" | bc -l) )); then
    echo "Warning: $HIGH_RATIO% of files have high complexity"
    exit 1
fi
```

### 複雑度トレンドの追跡

```bash
# 日次レポートの生成
echo "Date: $(date)" >> complexity_trends.log
cccy show-summary src/ >> complexity_trends.log
echo "---" >> complexity_trends.log
```

### チーム別分析

```bash
# 異なるモジュールの複雑度比較
echo "Core Module:"
cccy show-summary src/core/

echo -e "\nUI Module:"
cccy show-summary src/ui/

echo -e "\nAPI Module:"
cccy show-summary src/api/
```

## CI/CDでの活用

### 複雑度レポートの生成

```yaml
# GitHub Actions example
- name: Generate Complexity Report
  run: |
    cccy show-summary --verbose src/ > complexity_report.txt
    
- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: complexity-report
    path: complexity_report.txt
```

### 品質ゲートの実装

```bash
# 平均複雑度のチェック
MEAN_COMPLEXITY=$(cccy show-summary src/ | grep "Mean:" | head -1 | awk '{print $2}')

if (( $(echo "$MEAN_COMPLEXITY > 5.0" | bc -l) )); then
    echo "Error: Average complexity ($MEAN_COMPLEXITY) exceeds threshold (5.0)"
    exit 1
fi
```

## JSON出力での詳細分析

```bash
# JSON形式でのサマリー出力（将来の機能）
cccy show-summary --format json src/ | jq '{
  total_files: .files_analyzed,
  avg_cyclomatic: .cyclomatic.mean,
  avg_cognitive: .cognitive.mean,
  high_complexity_ratio: .status.high_percentage
}'
```

## パフォーマンスと最適化

### 大規模プロジェクトでの使用

```bash
# キャッシュを使用した高速化（将来の機能）
cccy show-summary --cache src/

# 並列処理での高速化
cccy show-summary --jobs 4 src/
```

### メモリ使用量の最適化

```bash
# ストリーミング処理での大規模プロジェクト対応
cccy show-summary --streaming src/
```