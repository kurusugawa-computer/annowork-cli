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

用途からコマンドを探す
==========================================
複数の値を渡せるコマンドラインオプションと、JSON形式の値を渡すコマンドラインオプションは、 ``file://`` を指定することでファイルの中身を渡すことができます。

``--workspace_id`` が必須のコマンドでは、コマンドライン引数を省略した場合に環境変数 ``ANNOWORK_WORKSPACE_ID`` を使用できます。

.. code-block::
    :caption: job_id.txt

    job1
    job2


.. code-block::

    # 標準入力で指定する
    $ annoworkcli job list --workspace_id org --job_id job1 job2

    # 相対パスでファイルを指定する
    $ annoworkcli job list --workspace_id org --job_id file://job_id.txt




ロギングコントロール

ログメッセージは、標準エラー出力とログファイル ``.log/annoworkcli.log`` に出力されます。
``.log/annoworkcli.log`` は、1日ごとにログロテート（新しいログファイルが生成）されます。

``--debug`` を指定すれば、HTTPリクエストも出力されます。


.. code-block::

    $ annoworkcli my get -o out/my.json
    INFO     : 2022-01-12 10:42:52,791 : annoworkcli.__main__           : sys.argv=['annoworkcli', 'my', 'get', '-o', 'out/my.json']
    INFO     : 2022-01-12 10:42:53,390 : annoworkcli.common.utils       : out/my.json に出力しました。

    $ annoworkcli my get -o out/my.json --debug
    INFO     : 2022-01-12 10:43:45,339 : annoworkcli.__main__           : sys.argv=['annoworkcli', 'my', 'get', '-o', 'out/my.json', '--debug']
    DEBUG    : 2022-01-12 10:43:45,339 : annoworkapi.resource           : Create annoworkapi resource instance :: {'login_user_id': 'alice', 'endpoint_url': 'https://annowork.com'}
    DEBUG    : 2022-01-12 10:43:45,615 : annoworkapi.api                : Sent a request :: {'request': {'http_method': 'get', 'url': 'https://annowork.com/api/v1/my/account', 'query_params': None, 'header_params': None, 'request_body': None}, 'response': {'status_code': 401, 'content_length': 26}}
    DEBUG    : 2022-01-12 10:43:46,047 : annoworkapi.api                : Sent a request :: {'requests': {'http_method': 'post', 'url': 'https://annowork.com/api/v1/login', 'query_params': None, 'request_body_json': {'user_id': 'alice', 'password': '***'}, 'request_body_data': None, 'header_params': None}, 'response': {'status_code': 200, 'content_length': 4105}}
    DEBUG    : 2022-01-12 10:43:46,154 : annoworkapi.api                : Sent a request :: {'request': {'http_method': 'get', 'url': 'https://annowork.com/api/v1/my/account', 'query_params': None, 'header_params': None, 'request_body': None}, 'response': {'status_code': 200, 'content_length': 365}}
    INFO     : 2022-01-12 10:43:46,155 : annoworkcli.common.utils       : out/my.json に出力しました。


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
