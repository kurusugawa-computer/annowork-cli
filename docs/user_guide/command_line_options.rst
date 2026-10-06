==========================================
コマンドラインオプションと入力
==========================================

ここでは複数のコマンドに共通する指定方法を説明します。
利用できるオプションと既定値は、各サブコマンドのヘルプまたは :doc:`../command_reference/index` を確認してください。

ワークスペースとリソースID
==========================================

``--workspace_id`` / ``-w`` は対象ワークスペースのIDです。
必須のコマンドでは、引数、環境変数 ``ANNOWORK_WORKSPACE_ID`` の順で値を取得します。
両方が未指定または空の場合はエラーになります。

.. code-block:: bash

    annoworkcli my list_workspace_member --format json
    export ANNOWORK_WORKSPACE_ID='YOUR_WORKSPACE_ID'
    annoworkcli job list --format json
    annoworkcli job list --workspace_id OTHER_WORKSPACE_ID --format json

最初のコマンドの出力にある ``workspace_id`` を利用してください。
最後の例では環境変数より ``OTHER_WORKSPACE_ID`` が優先されます。

``--job_id`` / ``-j`` はジョブID、 ``--parent_job_id`` / ``-pj`` は親ジョブID、 ``--user_id`` / ``-u`` はユーザーIDです。
ジョブIDは ``job list`` 、メンバー情報は ``workspace_member list`` で調べられます。
``user_id`` と ``workspace_member_id`` は異なる値なので、各オプションが要求するIDを指定してください。
``job list`` などでは ``--job_id`` と ``--parent_job_id`` を同時に指定できません。

複数の値とファイル入力
==========================================

複数の値を受け付けるオプションには、空白で区切って値を渡します。
``file://`` に対応するオプションでは、1行に1つの値を書いたファイルも渡せます。

.. code-block:: bash

    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --job_id job1 job2
    annoworkcli job list --workspace_id YOUR_WORKSPACE_ID --job_id file://job_id.txt

.. code-block:: text
    :caption: job_id.txt

    job1
    job2

ファイルはUTF-8（BOM付きも可）で保存します。空行は無視されます。
``file://`` の後ろはファイルパスで、相対パスは実行時のカレントディレクトリを基準にします。
ファイル指定は1つの引数として渡してください。たとえば ``--job_id file://job_id.txt job3`` ではファイルが展開されません。
``--output`` などのファイルパスを指定するオプションでは、 ``file://`` を付けず通常のパスを渡します。

JSONの入力
==========================================

``account put_external_linkage_info`` の ``--external_linkage_info`` には、JSON文字列またはJSONファイルを渡せます。
次の例はアカウントの外部連携情報を更新します。

.. code-block:: bash

    annoworkcli account put_external_linkage_info --user_id YOUR_USER_ID \
      --external_linkage_info '{"annofab":{"account_id":"YOUR_ANNOFAB_ACCOUNT_ID"}}'

    annoworkcli account put_external_linkage_info --user_id YOUR_USER_ID \
      --external_linkage_info file://external_linkage_info.json

.. code-block:: json
    :caption: external_linkage_info.json

    {"annofab": {"account_id": "YOUR_ANNOFAB_ACCOUNT_ID"}}

JSONファイルはUTF-8で保存します。
BashではJSON文字列全体をシングルクォートで囲むと、内部のダブルクォートをそのまま渡せます。
JSONのキーや値はコマンドごとに異なるため、各コマンドの説明を確認してください。

日付とタイムゾーン
==========================================

``--start_date`` と ``--end_date`` には ``YYYY-MM-DD`` 形式の日付を指定します。
``actual_working_time list_daily`` では、開始日・終了日の両方を集計対象に含めます。

.. code-block:: bash

    annoworkcli actual_working_time list_daily --workspace_id YOUR_WORKSPACE_ID \
      --start_date 2026-01-01 --end_date 2026-01-31 --timezone_offset 9

``--timezone_offset`` はUTCからの時差を時間で指定します。日本標準時は ``9`` です。
上記コマンドで未指定の場合は実行環境のローカルタイムゾーンを使用するため、自動実行では明示すると日付の集計基準が一定になります。
日付やタイムゾーンの扱いはコマンドによって異なるため、各コマンドの説明を確認してください。

出力・認証・確認のオプション
==========================================

* ``--output`` / ``-o`` と ``--format`` / ``-f`` : :doc:`cli_usage_output`
* ``--debug`` : :doc:`cli_usage_output` のログの説明
* ``--annowork_user_id`` 、 ``--annowork_password`` 、 ``--endpoint_url`` : :doc:`configurations`
* Annofabの認証オプション : :doc:`configurations`
* ``--yes`` と対話式の確認 : :doc:`user_guide`
