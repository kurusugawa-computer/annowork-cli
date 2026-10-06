==========================================
出力とログの制御
==========================================

出力形式
==========================================

``--format`` / ``-f`` を持つコマンドでは、次の形式を指定できます。

* ``csv`` : CSV。ファイル出力の文字コードはBOM付きUTF-8です。
* ``json`` : インデントされたJSON。文字コードはUTF-8です。

``job list`` や ``actual_working_time list_daily`` の既定値は ``csv`` です。
``my get`` のようにJSONのみを出力し、 ``--format`` を持たないコマンドもあります。
拡張子で出力形式を自動選択するわけではないので、JSONが必要なら ``--format json`` を指定してください。

.. code-block:: bash

    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --format json --output jobs.json
    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --format csv --output jobs.csv

出力先
==========================================

``--output`` / ``-o`` で出力先ファイルを指定します。未指定の場合は標準出力に出力します。
通常のJSON/CSV出力では、親ディレクトリを自動作成し、同名のファイルがあれば上書きします。
ディレクトリに複数のファイルを出力するコマンドは、各コマンドの ``--output_dir`` などの説明を確認してください。

.. code-block:: bash

    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --format json --output out/jobs.json
    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --format json > jobs.json

ログ
==========================================

ログは標準エラー出力と、カレントディレクトリの ``.log/annoworkcli.log`` に出力されます。
ログファイルは1日ごとにローテートされます。実行するディレクトリにはログを書き込める必要があります。
標準出力には取得結果が出るため、JSONやCSVをプログラムに渡す場合は標準エラー出力と混ぜずに扱ってください。

.. code-block:: bash

    annoworkcli my get > my.json 2> execution.log
    annoworkcli my get --output my.json --debug

``--debug`` を指定すると、HTTPリクエストの内容やレスポンスのステータスコードなどがログに出ます。
エラーの調査手順は :doc:`../faq` を参照してください。
