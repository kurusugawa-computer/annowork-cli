---
name: annowork-cli-user-operations
description: ユーザーからAnnowork上の情報取得、作業時間の集計、リソース操作を依頼されたときに使用します。操作にはannoworkcliを使用してください。annowork-cli自体の開発には使用しません。
---

# annowork-cli-user-operations

ユーザーから依頼されたAnnoworkの操作には、`annoworkcli`を使用してください。

## コマンドの調べ方

- 使用するコマンドが明確でない場合は、[コマンド索引](references/command-index.md)を参照してください。
- 実行前に、索引に記載されたコマンドに`--help`を付けて、引数、オプション、既定値を確認してください。コマンド名やオプションを推測しないでください。
- ヘルプだけでは情報が不足している場合は、[コマンドリファレンス](https://annowork-cli.readthedocs.io/ja/latest/command_reference/index.html)を参照してください。
- バージョンによる違いが疑われる場合は、`annoworkcli --version`で確認してください。

## 認証と対象の確認

- APIへのアクセスには、実行環境にAnnoworkの認証情報が必要です。[認証情報の設定](https://annowork-cli.readthedocs.io/ja/latest/user_guide/configurations.html)を参照してください。認証情報がない場合はユーザーに設定を依頼し、対話入力で停止するコマンドを実行しないでください。
- 認証情報をチャット、ログ、出力ファイルに記載しないでください。
- ワークスペースIDは`--workspace_id`または環境変数`ANNOWORK_WORKSPACE_ID`で指定します。対象が不明な場合は`annoworkcli my list_workspace_member --help`を確認して所属先を調べてください。
- ワークスペースID、ワークスペースメンバーID、アカウントID、ジョブIDを区別してください。対象のIDが不明な場合は一覧取得コマンドで確認してください。
- Annofab APIにアクセスする連携コマンドでは、Annofabの認証情報と対象プロジェクトへの権限も確認してください。

## リソースの変更

- ジョブ、メンバー、予定、実績などを作成・更新・削除するときは、実行前に対象のワークスペース、リソース、操作、設定内容を具体的に提示してください。
- ユーザーが具体的な実行内容を承認済みの場合は、その範囲で実行してください。対象や設定が未確定の場合や承認された範囲を変更する場合は、確認を取ってください。
- `--yes`は確認を省略するオプションです。対象と設定が承認済みで、自動実行に必要な場合に使用してください。
- 変更後は、可能であれば一覧取得などの読み取りコマンドで結果を確認してください。

## 集計と出力

- 作業時間を集計する場合は、対象期間、タイムゾーン、ジョブやメンバーなどの集計単位を確認してください。
- 出力形式や保存先の指定は、[出力方法](https://annowork-cli.readthedocs.io/ja/latest/user_guide/cli_usage_output.html)と使用するコマンドのヘルプを参照してください。

## 参考サイト

- [GitHubリポジトリ](https://github.com/kurusugawa-computer/annowork-cli)
- [ユーザーガイド](https://annowork-cli.readthedocs.io/ja/latest/user_guide/index.html)
