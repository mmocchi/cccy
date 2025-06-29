# cccy show-list

すべてのファイルの複雑度を一覧表示するコマンドです。複数の出力形式をサポートしており、人間が読みやすい形式からスクリプト処理に適した形式まで選択できます。

## 基本的な使い方

```bash
# 基本的な使用法
cccy show-list src/

# カレントディレクトリを解析
cccy show-list .

# 複数のディレクトリを解析
cccy show-list src/ tests/
```

## 出力形式

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

## オプション

### ファイルの除外・包含

```bash
# 特定のパターンを除外
cccy show-list --exclude "*/tests/*" --exclude "*/migrations/*" src/

# 特定のパターンのみ包含
cccy show-list --include "*.py" src/

# 再帰解析を無効化
cccy show-list --no-recursive src/
```

### ソートとフィルタリング

```bash
# 詳細情報を表示
cccy show-list --verbose src/
```

## 実用例

### 高複雑度ファイルの特定

```bash
# JSON出力を使用して高複雑度ファイルのみ抽出
cccy show-list --format json src/ | jq '.[] | select(.status == "HIGH")'

# CSV出力をソートして複雑度順に表示
cccy show-list --format csv src/ | sort -t',' -k2 -nr
```

### 複雑度トレンドの追跡

```bash
# 複雑度データをファイルに保存
cccy show-list --format json src/ > complexity_$(date +%Y%m%d).json

# 時系列での変化を追跡
cccy show-list --format csv src/ >> complexity_history.csv
```

### スクリプトでの活用

```bash
#!/bin/bash

# 高複雑度ファイルの数をカウント
HIGH_COUNT=$(cccy show-list --format json src/ | jq '[.[] | select(.status == "HIGH")] | length')

if [ "$HIGH_COUNT" -gt 0 ]; then
    echo "Warning: $HIGH_COUNT files have high complexity"
    cccy show-list --format table src/ | grep HIGH
fi
```

## パフォーマンス

### 大規模プロジェクトでの使用

```bash
# 特定のディレクトリのみ解析
cccy show-list --no-recursive src/core/

# 不要なファイルを除外してパフォーマンス向上
cccy show-list --exclude "*/vendor/*" --exclude "*/node_modules/*" src/
```

## 出力のカスタマイズ

### 環境変数での設定

```bash
# デフォルト出力形式を変更
export CCCY_FORMAT=json
cccy show-list src/

# デフォルト除外パターンを設定
export CCCY_EXCLUDE="*/tests/*,*/migrations/*"
cccy show-list src/
```

### パイプラインでの活用

```bash
# 特定の条件でフィルタリング
cccy show-list --format json src/ | \
  jq '.[] | select(.totals.cyclomatic_complexity > 10)' | \
  jq -r '.file_path'

# 統計情報の計算
cccy show-list --format csv src/ | \
  awk -F',' 'NR>1 {sum+=$2; count++} END {print "Average:", sum/count}'
```