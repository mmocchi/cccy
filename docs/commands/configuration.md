# 設定ファイル

cccyは `pyproject.toml` ファイルで設定をカスタマイズできます。設定ファイルを使用することで、毎回コマンドライン引数を指定する必要がなくなります。

## 基本的な設定

プロジェクトのルートディレクトリに `pyproject.toml` ファイルを作成し、`[tool.cccy]` セクションに設定を記述します。

```toml
[tool.cccy]
# 最大複雑度の閾値
max-complexity = 10
max-cognitive = 7

# 除外するファイルパターン
exclude = [
    "*/migrations/*",
    "*/venv/*",
    "*/.venv/*",
    "*/node_modules/*",
    "*/__pycache__/*",
    "*.egg-info/*",
]

# 包含するファイルパターン（指定した場合のみこれらのファイルを解析）
include = []

# 引数なしで実行した際のデフォルトパス
paths = ["src/"]
```

## 設定項目の詳細

### 複雑度の閾値

```toml
[tool.cccy]
# 循環的複雑度の最大値（デフォルト: なし）
max-complexity = 10

# 認知的複雑度の最大値（デフォルト: なし）
max-cognitive = 7
```

### パス設定

```toml
[tool.cccy]
# デフォルトで解析するパス
paths = ["src/", "lib/"]

# 再帰解析の有効/無効（デフォルト: true）
recursive = true
```

### ファイルフィルタリング

```toml
[tool.cccy]
# 除外パターン（glob形式）
exclude = [
    "*/tests/*",
    "*/test_*",
    "*/migrations/*",
    "*/vendor/*",
    "*/__pycache__/*",
    "*.egg-info/*",
    "*/.git/*",
    "*/.venv/*",
    "*/node_modules/*",
]

# 包含パターン（glob形式）
# 指定した場合、これらのパターンにマッチするファイルのみを解析
include = [
    "*.py",
]
```

### 出力設定

```toml
[tool.cccy]
# デフォルトの出力形式（table, json, csv, detailed）
format = "table"

# 詳細出力の有効/無効（デフォルト: false）
verbose = false
```

## 設定の優先順位

設定の優先順位は以下の通りです（上位が優先）：

1. **コマンドライン引数**
2. **環境変数**
3. **pyproject.toml の設定**
4. **デフォルト値**

### 例

```toml
# pyproject.toml
[tool.cccy]
max-complexity = 8
paths = ["src/"]
```

```bash
# 設定ファイルの値を使用
cccy check  # max-complexity=8, paths=["src/"]

# コマンドライン引数で上書き
cccy check --max-complexity 12  # max-complexity=12, paths=["src/"]

# パスも上書き
cccy check --max-complexity 12 tests/  # max-complexity=12, paths=["tests/"]
```

## プロジェクト別の設定例

### Webアプリケーション

```toml
[tool.cccy]
max-complexity = 10
max-cognitive = 7
paths = ["src/", "app/"]
exclude = [
    "*/migrations/*",
    "*/static/*",
    "*/templates/*",
    "*/tests/*",
    "*/venv/*",
]
```

### ライブラリプロジェクト

```toml
[tool.cccy]
max-complexity = 8
max-cognitive = 6
paths = ["src/"]
exclude = [
    "*/tests/*",
    "*/examples/*",
    "*/docs/*",
]
```

### データサイエンスプロジェクト

```toml
[tool.cccy]
max-complexity = 12
max-cognitive = 8
paths = ["src/", "notebooks/"]
exclude = [
    "*/data/*",
    "*/output/*",
    "*/checkpoints/*",
    "*.ipynb",
]
include = [
    "*.py",
]
```

### マイクロサービス

```toml
[tool.cccy]
max-complexity = 8
max-cognitive = 6
paths = ["api/", "services/", "shared/"]
exclude = [
    "*/tests/*",
    "*/migrations/*",
    "*/proto/*",
    "*/vendor/*",
]
```

## 環境変数での設定

環境変数を使用して一時的に設定を変更できます：

```bash
# 環境変数での設定
export CCCY_MAX_COMPLEXITY=12
export CCCY_MAX_COGNITIVE=8
export CCCY_FORMAT=json

cccy show-list  # 環境変数の設定を使用
```

### 利用可能な環境変数

```bash
CCCY_MAX_COMPLEXITY     # 循環的複雑度の最大値
CCCY_MAX_COGNITIVE      # 認知的複雑度の最大値
CCCY_FORMAT             # 出力形式
CCCY_EXCLUDE            # 除外パターン（カンマ区切り）
CCCY_INCLUDE            # 包含パターン（カンマ区切り）
CCCY_RECURSIVE          # 再帰解析（true/false）
CCCY_VERBOSE            # 詳細出力（true/false）
```

## チーム開発での設定管理

### 共通設定の管理

```toml
# プロジェクト共通の設定
[tool.cccy]
max-complexity = 10
max-cognitive = 7
exclude = [
    "*/tests/*",
    "*/migrations/*",
]
paths = ["src/"]
```

### 個人設定の分離

```bash
# 個人の開発環境用の設定
export CCCY_MAX_COMPLEXITY=15  # より緩い設定で開発
cccy show-list
```

### CI/CD用の設定

```yaml
# GitHub Actions
env:
  CCCY_MAX_COMPLEXITY: 8  # CI/CDではより厳しく
  CCCY_MAX_COGNITIVE: 6
```

## 設定の検証

```bash
# 現在の設定を確認（将来の機能）
cccy config show

# 設定ファイルの検証
cccy config validate
```

## トラブルシューティング

### 設定が反映されない場合

1. ファイルパスが正しいか確認
2. TOML形式が正しいか確認
3. コマンドライン引数で上書きされていないか確認

```bash
# 設定の読み込み状況をデバッグ
cccy --debug show-list
```

### 推奨設定のテンプレート

```bash
# 設定ファイルのテンプレートを生成（将来の機能）
cccy config init
```