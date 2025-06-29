# インストール

cccyは複数の方法でインストールできます。

## uvを使用（推奨）

[uv](https://docs.astral.sh/uv/)は高速なPythonパッケージマネージャーです。

```bash
uv tool install cccy
```

## pipを使用

```bash
pip install cccy
```

## インストールの確認

インストールが成功したことを確認するには、以下のコマンドを実行してください：

```bash
cccy --version
```

または、ヘルプを表示：

```bash
cccy --help
```

## 開発版のインストール

最新の開発版をインストールしたい場合：

```bash
pip install git+https://github.com/mmocchi/cccy.git
```

## システム要件

- Python 3.9以上
- サポートするオペレーティングシステム：
  - Linux
  - macOS  
  - Windows

## 依存関係

cccyは以下のパッケージに依存しています：

- `mccabe` - 循環的複雑度の計算
- `cognitive-complexity` - 認知的複雑度の計算
- `click` - CLIフレームワーク
- `tabulate` - テーブル形式の出力
- `pydantic` - 設定管理

これらの依存関係は自動的にインストールされます。