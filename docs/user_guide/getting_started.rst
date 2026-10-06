==========================================
Getting Started
==========================================

annoworkcliは、Annoworkのジョブ、ワークスペースメンバー、実績作業時間、アサイン時間などを操作するコマンドラインツールです。
APIにアクセスするには、Annoworkのアカウントと対象ワークスペースでの操作権限が必要です。

動作環境とインストール
==========================================

Python 3.12以上とpipが必要です。パッケージ名と実行するコマンド名は、どちらも ``annoworkcli`` です。
以下のコマンド例はBashなどのPOSIXシェル用です。 ``YOUR_USER_ID`` などの値は実際の値に置き換えてください。

仮想環境を作成してインストールします。

.. code-block:: bash

    python --version
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install annoworkcli
    annoworkcli --version

WindowsのPowerShellでは、仮想環境の有効化と環境変数の設定に次の構文を使用します。
以降のコマンド例も、環境変数や複数行の書き方を利用するシェルに合わせて変更してください。

.. code-block:: powershell

    python --version
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install annoworkcli
    annoworkcli --version
    $env:ANNOWORK_USER_ID = 'YOUR_USER_ID'
    $env:ANNOWORK_PASSWORD = 'YOUR_PASSWORD'

``annoworkcli --version`` で ``annoworkcli X.Y.Z`` のようにバージョンが表示されれば、インストールは完了です。
``python -m annoworkcli`` でも同じCLIを実行できます。

更新するには、インストールした環境で次のコマンドを実行します。

.. code-block:: bash

    python -m pip install --upgrade annoworkcli

認証情報の設定と初回の動作確認
==========================================

環境変数にAnnoworkのユーザーIDとパスワードを設定し、自分のアカウント情報を取得します。

.. code-block:: bash

    export ANNOWORK_USER_ID='YOUR_USER_ID'
    export ANNOWORK_PASSWORD='YOUR_PASSWORD'
    annoworkcli my get

自分のアカウント情報がJSONで表示されれば、認証は成功です。
認証情報の優先順位、 ``.netrc`` 、対話入力、Annofab連携の設定は :doc:`configurations` を参照してください。

ワークスペースを選んで実行する
==========================================

所属するワークスペースを調べます。このコマンドはワークスペースIDを指定する必要がありません。

.. code-block:: bash

    annoworkcli my list_workspace_member --format json

出力されたメンバー情報の ``workspace_id`` を、対象ワークスペースのIDとして使用します。
``workspace_member_id`` はそのワークスペース内のメンバーのIDで、 ``workspace_id`` とは異なります。

.. code-block:: bash

    export ANNOWORK_WORKSPACE_ID='YOUR_WORKSPACE_ID'
    annoworkcli job list --format json --output jobs.json

``jobs.json`` にジョブ一覧が出力されます。ジョブがなければ、JSONの出力は空の配列になります。
ワークスペースの指定方法は :doc:`command_line_options` 、出力方法は :doc:`cli_usage_output` を参照してください。

次に読むページ
==========================================

* :doc:`user_guide` : コマンド構造、ヘルプ、用途に合うコマンドの探し方
* :doc:`../examples/index` : 実績作業時間のCSV出力など、一連の実行例
* :doc:`../command_reference/index` : 各コマンドの引数、既定値、出力内容
* :doc:`../faq` : インストール、認証、実行時の問題の調べ方
