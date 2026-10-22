<!-- scripts/generate_skill_command_index.pyで自動生成しています。手動で編集しないでください。 -->

# annowork-cliコマンド索引

このファイルは、annowork-cliが提供するコマンドとその概要を確認するための索引です。
オプションや引数の詳細は、使用する環境で索引に記載されたコマンドに`--help`を付けて実行し、確認してください。

## account

ユーザアカウントに関するサブコマンド

- `annoworkcli account list_external_linkage_info`: アカウント外部連携情報取得の一覧を出力します。
- `annoworkcli account update_external_linkage_info`: アカウントの外部連携情報を更新します。

## actual_working_time

実績作業時間関係のサブコマンド

- `annoworkcli actual_working_time list`: 実績作業時間情報の一覧を出力します。
- `annoworkcli actual_working_time list_daily`: 実績作業時間を日ごとに集約した情報を一覧として出力します。
- `annoworkcli actual_working_time list_daily_by_job`: 実績作業時間を日ごと・ジョブごとに集計して出力します。
- `annoworkcli actual_working_time list_daily_groupby_tag`: 日ごとの実績作業時間を、ワークスペースタグで集計した値を出力します。
- `annoworkcli actual_working_time list_weekly`: 実績作業時間の一覧を週ごと（日曜日始まり）に出力します。

## annofab

Annofab連携に関するサブコマンド

- `annoworkcli annofab create_job`: Annofabプロジェクトからジョブを作成します。
- `annoworkcli annofab list_assigned_hours`: Annofabプロジェクトに紐づくジョブのアサイン時間を日ごとに出力します。
- `annoworkcli annofab list_job`: ジョブとジョブに紐づくAnnofabプロジェクトの情報を一緒に出力します。
- `annoworkcli annofab list_working_hours`: 日ごとの実績作業時間と、ジョブに紐づくAnnofabプロジェクトの作業時間を一緒に出力します。
- `annoworkcli annofab reshape_working_hours`: Annoworkの実績作業時間とアサイン時間、Annofabの作業時間を比較できるようなCSVファイルに成形します。
- `annoworkcli annofab set_account_external_linkage_info`: アカウントの外部連携情報に、Annofabから取得したaccount_idを設定します。 Annofabのuser_idはAnnoworkのuser_idと一致している必要があります。
- `annoworkcli annofab visualize_statistics`: Annofabの統計情報を実績作業時間と組み合わせて可視化します。

## completion

指定したシェル用の補完スクリプトを標準出力に書き出します。

- `annoworkcli completion`: 指定したシェル用の補完スクリプトを標準出力に書き出します。

## expected_working_time

予定稼働時間関係のサブコマンド

- `annoworkcli expected_working_time delete`: 予定稼働時間を削除します。
- `annoworkcli expected_working_time list`: 予定稼働時間の一覧を出力します。
- `annoworkcli expected_working_time list_groupby_tag`: ワークスペースタグで集計した予定稼働時間の一覧を出力します。
- `annoworkcli expected_working_time list_weekly`: 予定稼働時間の一覧を週ごと（日曜日始まり）に出力します。

## job

ジョブ関係のサブコマンド

- `annoworkcli job delete`: ジョブを削除します。
- `annoworkcli job list`: ジョブ一覧を出力します。
- `annoworkcli job update_status`: ジョブのステータスを変更します。

## my

自分自身に関するサブコマンド

- `annoworkcli my get`: ログイン中のアカウント情報を出力します。
- `annoworkcli my list_workspace_member`: 所属しているワークスペースでの自分自身のメンバー情報を出力します。

## schedule

作業計画関係のサブコマンド

- `annoworkcli schedule create`: 作業計画をユーザーごとに作成します。
- `annoworkcli schedule delete`: 親ジョブ・ユーザー・開始日で選んだ作業計画を削除します。
- `annoworkcli schedule delete_by_schedule_id`: IDを指定して作業計画を削除します。
- `annoworkcli schedule list`: 作業計画の一覧を出力します。
- `annoworkcli schedule list_daily`: 作業計画から求めたアサイン時間を日ごとに出力します。
- `annoworkcli schedule list_daily_by_parent_job`: 作業計画から求めたアサイン時間を日ごと・親ジョブごとに集計して出力します。
- `annoworkcli schedule list_daily_groupby_tag`: 日ごとのアサイン時間を、ワークスペースタグで集計した値を出力します。
- `annoworkcli schedule list_weekly`: 作業計画から求めたアサイン時間を週ごと（日曜日始まり）に出力します。
- `annoworkcli schedule list_workload_daily`: 全ユーザーの日別予定稼働時間と親ジョブ別アサイン時間を出力します。
- `annoworkcli schedule list_workload_daily_by_user`: 日付・ユーザーごとのアサイン状況と親ジョブ別の内訳を出力します。
- `annoworkcli schedule list_workload_weekly`: 全ユーザーの週別予定稼働時間と親ジョブ別アサイン時間を出力します。
- `annoworkcli schedule list_workload_weekly_by_user`: 週・ユーザーごとのアサイン状況と親ジョブ別の内訳を出力します。
- `annoworkcli schedule update`: 作業計画の期間・割当量を更新します。
- `annoworkcli schedule update_end_date`: 親ジョブ・ユーザー・現在の終了日で選んだ作業計画の終了日を一括変更します。
- `annoworkcli schedule update_start_date`: 親ジョブ・ユーザー・現在の開始日で選んだ作業計画の開始日を一括変更します。

## schedule_actual

予定と実績を結合した作業時間関係のサブコマンド

- `annoworkcli schedule_actual list_daily`: 前日までの実績と当日以降の予定を結合した日ごとの作業時間を出力します。
- `annoworkcli schedule_actual list_weekly`: 前日までの実績と当日以降の予定を結合した週ごとの作業時間を出力します。

## workspace

ワークスペース関係のサブコマンド

- `annoworkcli workspace create`: ワークスペースを作成します。
- `annoworkcli workspace list`: ワークスペースの一覧を取得します。
- `annoworkcli workspace update`: ワークスペースを更新します。

## workspace_member

ワークスペースメンバ関係のサブコマンド

- `annoworkcli workspace_member append_tag`: ワークスペースメンバにワークスペースタグを追加します。
- `annoworkcli workspace_member create`: ワークスペースメンバを作成します。
- `annoworkcli workspace_member delete`: ワークスペースメンバを削除します。
- `annoworkcli workspace_member list`: ワークスペースメンバの一覧を出力します。無効化されたメンバも出力します。
- `annoworkcli workspace_member remove_tag`: ワークスペースメンバからワークスペースタグを削除します。
- `annoworkcli workspace_member update_role`: ワークスペースメンバのロールを変更します。

## workspace_tag

ワークスペースタグ関係のサブコマンド

- `annoworkcli workspace_tag create`: ワークスペースタグを作成します。
- `annoworkcli workspace_tag list`: ワークスペースタグの一覧を出力します。
- `annoworkcli workspace_tag update`: ワークスペースタグを更新します。
