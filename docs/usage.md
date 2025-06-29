# 基本的な使い方

cccyはコマンドラインツールとして使用できます。3つの主要なコマンドが利用可能です。

## 主要コマンド

### cccy show-list
すべてのファイルの複雑度を一覧表示します。

```bash
cccy show-list src/
```

### cccy check  
複雑度が閾値を超えているかチェックします（CI/CD向け）。

```bash
cccy check --max-complexity 10 --max-cognitive 7 src/
```

### cccy show-summary
プロジェクト全体の複雑度統計を表示します。

```bash
cccy show-summary src/
```

## クイックスタート

```bash
# インストール
uv tool install cccy

# 基本的な使用
cccy show-list src/

# CI/CDでのチェック
cccy check --max-complexity 10 src/
```

詳細な使用方法については、各コマンドのページを参照してください：

- **[cccy check](commands/check.md)** - 複雑度チェック（CI/CD向け）
- **[cccy show-list](commands/show-list.md)** - 複雑度一覧表示
- **[cccy show-summary](commands/show-summary.md)** - 統計サマリー
- **[設定ファイル](commands/configuration.md)** - pyproject.tomlでの設定方法