# Auto Retry Failed Jobs Action

GitHub Actions のワークフローで失敗したジョブを自動的に再実行するアクションです。

## 機能

- 特定のブランチでの失敗のみを対象にするブランチフィルター
- 特定のジョブが失敗した場合のみ再実行する条件フィルター
- 最大再試行回数の設定
- 再実行前の待機時間

## 使用方法

### 基本的な使用例

```yaml
- name: Auto retry failed jobs
  uses: ./.github/actions/auto-retry-failed-jobs
  with:
    workflow_config: |
      {
        "Test": {
          "branches": ["main", "develop"],
          "jobs": ["test"],
          "max_retries": 3
        },
        "CI": {
          "branches": ["main"],
          "jobs": ["lint", "build"],
          "max_retries": 2
        }
      }
```

### 詳細設定例

```yaml
- name: Auto retry failed jobs
  uses: ./.github/actions/auto-retry-failed-jobs
  with:
    workflow_config: |
      {
        "Test": {
          "branches": ["main", "develop"],
          "jobs": ["test"],
          "max_retries": 3
        },
        "Deploy": {
          "branches": ["main"],
          "jobs": [],
          "max_retries": 1
        },
        "CI": {
          "branches": ["main", "develop", "release"],
          "jobs": ["lint", "typecheck"],
          "max_retries": 2
        }
      }
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

## 入力パラメータ

| パラメータ | 必須 | デフォルト値 | 説明 |
|-----------|------|-------------|------|
| `workflow_config` | ✅ | - | ワークフロー別設定（JSON形式） |
| `github_token` | ❌ | `${{ github.token }}` | GitHub API アクセストークン |

## 出力

| 出力名 | 説明 |
|-------|------|
| `retry_executed` | 再実行が実行されたかどうか（true/false） |
| `failed_jobs` | 失敗したジョブのリスト（カンマ区切り） |

## 設定方式

### JSON設定

`workflow_config` パラメータでワークフローごとに詳細な設定を行います。

```json
{
  "ワークフロー名": {
    "branches": ["対象ブランチ"],
    "jobs": ["条件ジョブ"],
    "max_retries": 最大再試行回数
  }
}
```

### 設定項目

| 項目 | 必須 | デフォルト値 | 説明 |
|------|------|-------------|------|
| `branches` | ❌ | `["main", "develop"]` | 対象ブランチの配列 |
| `jobs` | ❌ | `[]` | 条件ジョブの配列（空の場合は全ジョブ失敗で再実行） |
| `max_retries` | ❌ | `3` | 最大再試行回数 |

## フィルター機能

### ワークフローフィルター

ワークフロー名がJSONのキーとして存在する場合のみ対象になります。

### ブランチフィルター

指定されたブランチでの失敗のみが対象になります。

- 空配列の場合: デフォルト値 `["main", "develop"]` が適用
- 複数指定: 配列で指定（例: `["main", "develop", "release"]`）

### ジョブ条件フィルター

指定されたジョブが失敗した場合のみ再実行されます。

- 空配列の場合: 任意のジョブ失敗で再実行
- 複数指定: 配列で指定（例: `["test", "lint", "build"]`）

## ワークフロー例

```yaml
name: Auto Retry on Failure

on:
  workflow_run:
    workflows: ["CI", "Deploy"]
    types: [completed]

permissions:
  actions: write
  contents: read

jobs:
  auto-retry:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Auto retry failed jobs
        uses: ./.github/actions/auto-retry-failed-jobs
        with:
          workflow_config: |
            {
              "CI": {
                "branches": ["main"],
                "jobs": ["test"],
                "max_retries": 2
              }
            }
```

## 注意事項

- `actions: write` 権限が必要です
- 再実行前に30秒間の待機時間があります
- 最大再試行回数に達した場合、それ以上の再実行は行われません