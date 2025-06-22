"""CLI バナー生成機能。"""

from cccy import get_version


def create_banner() -> str:
    """CLI バナーを動的バージョンで作成します。

    Returns:
        フォーマットされたバナー文字列

    """
    version = get_version()
    # バージョンを適切に配置するためのパディングを計算
    max_width = 57  # ボックス内の利用可能な幅
    version_text = f"v{version}"
    # ASCII アートの行の右側にバージョンを配置
    padding = max_width - 25 - len(version_text)  # 25 は ASCII アートの幅
    padding = max(padding, 1)

    return f"""┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ██▀ ██▀ ██▀ █▄█                                        │
│  ██▄ ██▄ ██▄  █     {version_text}{" " * padding}    │
│                                                         │
│  Python Code Complexity Analyzer                        │
│                                                         │
└─────────────────────────────────────────────────────────┘"""


def get_main_help_text() -> str:
    """メインヘルプテキストを取得します。

    Returns:
        メインコマンドのヘルプテキスト

    """
    return "Pythonコードの循環的複雑度と認知的複雑度を解析します。"
