==========================================
CLIの基本
==========================================

コマンド構造
==========================================

.. code-block:: text

    annoworkcli <command> <subcommand> [options]

``command`` は ``job`` や ``workspace_member`` などのカテゴリ、 ``subcommand`` は ``list`` や ``delete`` などの操作です。
オプションはサブコマンドの後に指定します。オプション名の単語はアンダースコアで区切ります。

.. code-block:: bash

    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --format json

バージョンとヘルプ
==========================================

.. code-block:: bash

    annoworkcli --version
    annoworkcli --help
    annoworkcli job --help
    annoworkcli job list --help

ヘルプには必須の引数、使用できる値、既定値が表示されます。
詳細は :doc:`../command_reference/index` の各サブコマンドの「Usage Details」でも確認できます。

.. _shell-completion:

シェル補完
==========================================

``completion`` コマンドで補完スクリプトを生成すると、コマンド名、サブコマンド、オプション名、および選択肢をTabキーで補完できます。
補完時にannoworkcliを起動したり、Web APIにアクセスしたりすることはありません。
構文は :doc:`../command_reference/completion` を参照してください。

Bash、Zsh、Fish、PowerShell、Tcshに対応しています。annoworkcliの更新後はスクリプトを再生成してください。

Bash
------------------------------------------

Bash 4以上が必要です。以下のコマンドで現在のシェルに補完を設定します。
次回以降も有効にする場合は、生成したスクリプトを読み込む ``source`` の行を ``~/.bashrc`` に追加してください。

.. code-block:: bash

    mkdir -p ~/.local/share/bash-completion/completions
    annoworkcli completion bash > ~/.local/share/bash-completion/completions/annoworkcli
    source ~/.local/share/bash-completion/completions/annoworkcli

Zsh
------------------------------------------

.. code-block:: zsh

    mkdir -p ~/.zsh/completions
    annoworkcli completion zsh > ~/.zsh/completions/_annoworkcli

``~/.zshrc`` で、補完の初期化より前に保存先を ``fpath`` に追加し、新しいシェルを起動してください。
すでに ``compinit`` を実行している場合は、その行の前に ``fpath`` の設定を追加してください。

.. code-block:: zsh

    fpath=(~/.zsh/completions $fpath)
    autoload -Uz compinit
    compinit

Fish
------------------------------------------

.. code-block:: fish

    mkdir -p ~/.config/fish/completions
    annoworkcli completion fish > ~/.config/fish/completions/annoworkcli.fish

新しいシェルで有効になります。

PowerShell
------------------------------------------

.. code-block:: powershell

    annoworkcli completion powershell | Out-File -Encoding utf8 "$HOME/annoworkcli-completion.ps1"
    . "$HOME/annoworkcli-completion.ps1"

次回以降も有効にする場合は、スクリプトを読み込む2行目を ``$PROFILE`` に追加してください。

Tcsh
------------------------------------------

.. code-block:: tcsh

    annoworkcli completion tcsh > ~/.annoworkcli-completion.tcsh
    source ~/.annoworkcli-completion.tcsh

次回以降も有効にする場合は、 ``source`` の行を ``~/.tcshrc`` に追加してください。

用途からコマンドを探す
==========================================
.. list-table::
    :header-rows: 1
    :widths: 45 55

    * - 用途
      - コマンド
    * - 自分のアカウント・所属ワークスペースを確認する
      - :doc:`../command_reference/my/index`
    * - ワークスペースを取得・作成する
      - :doc:`../command_reference/workspace/index`
    * - ワークスペースメンバーやタグを管理する
      - :doc:`../command_reference/workspace_member/index` 、 :doc:`../command_reference/workspace_tag/index`
    * - ジョブを取得・変更・削除する
      - :doc:`../command_reference/job/index`
    * - 実績作業時間を取得・集計する
      - :doc:`../command_reference/actual_working_time/index`
    * - アサイン時間を取得・集計・削除する
      - :doc:`../command_reference/schedule/index`
    * - 予定と実績を結合した累積作業時間を取得する
      - :doc:`../command_reference/schedule_actual/index`
    * - 予定稼働時間を取得・集計・削除する
      - :doc:`../command_reference/expected_working_time/index`
    * - Annofabと連携する
      - :doc:`../command_reference/annofab/index`

自動実行時の確認
==========================================

認証とワークスペースの設定は :doc:`configurations` 、値やファイルの渡し方は :doc:`command_line_options` を参照してください。
更新・削除コマンドには確認プロンプトがあるものがあります。
確認では ``y`` が承認、 ``N`` が中止またはスキップ、 ``ALL`` が以降の確認を省略して承認します。
入力は大文字と小文字を区別します。確認によっては ``ALL`` を利用できません。

``--yes`` を持つコマンドでは、 ``--yes yes`` のように値を指定すると確認を省略できます。
値なしの ``--yes`` では引数エラーになります。実行するサブコマンドのヘルプで対応の有無を確認してください。
