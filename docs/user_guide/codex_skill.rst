==========================================
Agent Skill
==========================================

AIエージェントからannowork-cliを使ってAnnoworkのジョブ、ワークスペースメンバー、予定、実績作業時間などを操作・集計するためのAgent Skillを提供しています。

Skillのファイルは、annowork-cliリポジトリの ``skills/annowork-cli-user-operations`` ディレクトリにあります。
``SKILL.md`` だけでなく、コマンド索引も使用するため、ディレクトリ全体をインストールしてください。
annoworkcli本体のインストールと認証情報の設定は :doc:`getting_started` と :doc:`configurations` を参照してください。


Codexへのインストール
==========================================

Linux環境で以下のコマンドを実行します。
GitHubからSkillディレクトリだけをダウンロードして、Codexの個人用Skillディレクトリへ展開します。

.. code-block:: console

    $ mkdir -p ~/.codex/skills
    $ curl --fail --location --silent --show-error https://github.com/kurusugawa-computer/annowork-cli/archive/refs/heads/main.tar.gz \
        | tar -xz --strip-components=2 -C ~/.codex/skills annowork-cli-main/skills/annowork-cli-user-operations

インストール先は ``~/.codex/skills/annowork-cli-user-operations`` です。


コマンド索引の更新（開発者向け）
==========================================

コマンド索引は、annoworkcliのargparseの定義から生成します。
コマンドの追加・変更後は、リポジトリのルートで次のコマンドを実行してください。

.. code-block:: console

    $ make generate-skill-command-index

生成先は ``skills/annowork-cli-user-operations/references/command-index.md`` です。
このファイルは手動で編集せず、生成した変更もコミットしてください。
``make format`` でも索引を生成し、 ``make lint`` では定義との一致を確認します。
索引の確認だけを行う場合は ``make check-skill-command-index`` を実行してください。


関連情報
==========================================

* `CodexにおけるSkillの配置例 <https://developers.openai.com/blog/eval-skills>`_
