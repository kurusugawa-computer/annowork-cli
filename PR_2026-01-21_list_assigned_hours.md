# annofab list_assigned_hours コマンドの追加

## 概要

AnnofabプロジェクトIDを指定して、紐づくジョブのスケジュール時間（アサイン時間）を日ごとに出力するコマンドを追加しました。

### 背景

現状では、AnnofabプロジェクトIDから紐づくジョブのアサイン時間を取得するには、以下の2ステップが必要でした：

1. `annofab list_job` コマンドでAnnofabプロジェクトに紐づくジョブを取得
2. `schedule list_daily` コマンドでジョブのアサイン時間を取得

このコマンドにより、**1回のコマンド実行で取得可能**になりました。

## 実装内容

### 追加ファイル

- `annoworkcli/annofab/list_assigned_hours.py`: メインの実装
- `docs/command_reference/annofab/list_assigned_hours.rst`: コマンドのドキュメント

### 変更ファイル

- `annoworkcli/annofab/subcommand.py`: 新コマンドをサブコマンドとして登録

### コマンド仕様

```bash
annoworkcli annofab list_assigned_hours \
  --workspace_id <workspace_id> \
  --annofab_project_id <project_id> [<project_id> ...] \
  --start_date YYYY-MM-DD \
  --end_date YYYY-MM-DD \
  [--user_id <user_id> [<user_id> ...]] \
  [--format csv|json] \
  [--output <file_path>]
```

#### 必須引数

- `--workspace_id`: 対象のワークスペースID
- `--annofab_project_id`: AnnofabプロジェクトID（複数指定可能）
- `--start_date`: 集計開始日（YYYY-MM-DD形式）
- `--end_date`: 集計終了日（YYYY-MM-DD形式）

#### オプション引数

- `--user_id`: 絞り込み対象のユーザID（複数指定可能）
- `--format`: 出力フォーマット（csv/json、デフォルト: csv）
- `--output`: 出力先ファイルパス

### 出力フォーマット

```json
[
  {
    "date": "2021-11-05",
    "parent_job_id": "parent_job",
    "parent_job_name": "親ジョブ",
    "workspace_member_id": "58005ead-f85b-45d8-931b-54ba2837d7b1",
    "user_id": "alice",
    "username": "Alice",
    "assigned_working_hours": 1.5,
    "annofab_account_id": "4f275f74-5c58-4d35-a700-2475de20d2da"
  }
]
```

### 技術的な詳細

- **親ジョブ単位で集計**: 子ジョブのスケジュールを親ジョブ単位で集計して出力
- **Annofab認証不要**: Annowork APIのみを使用（Annofab APIは不要）
- **既存コードの再利用**: 
  - `ListAssignedHoursDaily` クラスでスケジュール取得
  - `get_annofab_project_id_from_job()` でジョブとAnnofabプロジェクトの紐付け判定

## 検討事項

### 1. コマンド名

#### 検討した選択肢

- **`list_assigned_hours_daily`** (却下)
  - より明示的だが冗長
  - `schedule` サブコマンド配下では妥当だが、`annofab` サブコマンド配下では文脈的に「日ごと」が期待される

- **`list_assigned_hours`** (採用) ✅
  - `annofab` サブコマンド配下では、日ごとに出力することが自然と期待される
  - 簡潔で分かりやすい
  - `schedule list_daily` の内部実装が "assigned_hours_daily" なので、名前の一貫性もある

### 2. 出力フィールド

#### job_id / job_name の扱い

- **検討内容**: `schedule list_daily` コマンドでは `job_id` と `job_name` が出力されるが、このコマンドでは必要か？

- **結論**: 不要 ✅
  - `schedule list_daily` の `job_id` が、このコマンドの `parent_job_id` に対応
  - 子ジョブの情報は親ジョブ単位で集計されるため、個別の `job_id` は意味をなさない
  - `annofab list_working_hours` コマンドとの一貫性を保つため `parent_job_id` / `parent_job_name` を使用

#### annofab_project_id の扱い

- **結論**: 出力に含めない ✅
  - 1個の親ジョブは複数のAnnofabプロジェクトに紐づく可能性がある
  - 入力パラメータとしては指定するが、出力には含めないことで混乱を避ける

### 3. 集計単位

#### 子ジョブの詳細表示オプション

- **検討内容**: `--include_child_jobs` のようなオプションで、子ジョブの詳細も表示できるようにするか？

- **結論**: オプションは不要 ✅
  - 親ジョブ単位の集計が主な用途
  - 子ジョブの詳細が必要な場合は `schedule list_daily` を直接使用すれば良い
  - シンプルさを優先

### 4. 日付範囲のデフォルト

#### デフォルト動作の検討

- **検討した選択肢**:
  - デフォルトで今日から1ヶ月分を取得 (却下)
  - デフォルト値なし、必須引数とする (採用) ✅

- **理由**: 
  - `annofab list_working_hours` コマンドと一貫性を保つ
  - 意図しない大量データ取得を防ぐ
  - 明示的な指定を促すことでユーザーの意図を明確にする

### 5. Annofab認証の要否

- **結論**: 不要 ✅
  - ジョブ情報の取得はAnnowork APIのみで可能
  - `annofab list_working_hours` はAnnofab APIを呼ぶため認証が必要だが、このコマンドはスケジュール取得のみなので不要
  - 認証設定の手間を削減できる

### 6. 複数Annofabプロジェクトの指定

- **結論**: 複数指定可能 ✅
  - `--annofab_project_id` は `nargs="+"` で複数指定を許可
  - `annofab list_working_hours` コマンドと同様の仕様
  - 複数プロジェクトをまとめて確認できる利便性

## 参考コマンド

### 類似コマンドとの比較

| コマンド | 入力 | 出力 | 認証 |
|---------|------|------|------|
| `schedule list_daily` | job_id | job単位のアサイン時間 | Annowork |
| `annofab list_working_hours` | annofab_project_id | 実績作業時間 + Annofab作業時間 | Annowork + Annofab |
| **`annofab list_assigned_hours`** | annofab_project_id | parent_job単位のアサイン時間 | Annowork |

## テスト

- `make format`: コードフォーマット完了
- `make lint`: 全チェック通過（ruff、mypy）

## 今後の拡張可能性

- 週次集計版（`list_assigned_hours_weekly`）の追加
- タグでのグルーピング（`list_assigned_hours_groupby_tag`）の追加
