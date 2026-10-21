# Usage for Developer
開発者用のドキュメントです。
ソースコードの生成、テスト実行、リリース手順などを記載します。

# 開発方法
VSCodeのdevcotainerを利用して開発します。
https://code.visualstudio.com/docs/remote/containers

1. 以下の環境変数を定義する
    * `ANNOFAB_USER_ID`
    * `ANNOFAB_PASSWORD`
    * `ANNOWORK_USER_ID`
    * `ANNOWORK_PASSWORD`
2. VSCodeのdevcontainerを起動します。

# 開発フロー
* mainブランチを元にしてブランチを作成して、プルリクを作成してください。mainブランチへの直接pushすることはGitHub上で禁止しています。

# シークレットの検査
開発環境のセットアップ時に、コミット対象のシークレットを検査するpre-commit hookをインストールしてください。

```bash
uv sync
uv run pre-commit install
```

以後、コミット時にgitleaksでステージ済みの変更を検査し、シークレットを検出した場合はコミットを中止します。初回実行時にはフックの実行環境がダウンロードされます。

Git履歴全体を検査するには、以下を実行してください。gitleaksがインストールされていない場合はDockerを使用します。

```bash
make gitleaks
```

GitHub Actionsでも、mainへのpushとmain向けのプルリクエストでGit履歴全体を検査します。検出結果のシークレットはマスクされます。

# Release
GitHubのReleasesからリリースしてください。
バージョンはSemantic Versioningに従います。
リリースすると、以下の状態になります。

* パッケージのバージョンは、uv-dynamic-versioningでGitHubのバージョンタグから生成されます。実行時の`annoworkcli.__version__`は、インストールされたパッケージのメタデータから取得します。
* 自動でPyPIに公開されます。


# Document
以下のコマンドを実行すると、`docs/_build/html/`にドキュメントが生成されます。

```
$ make docs
```

ドキュメントはReadTheDocsにデプロイしています。
GitHubのmainブランチが更新されると、ReadTheDocsに自動でデプロイされます。

