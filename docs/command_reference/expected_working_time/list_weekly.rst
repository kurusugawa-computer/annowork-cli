=========================================
expected_working_time list_weekly
=========================================

Description
=================================
予定稼働時間の一覧を週ごと（日曜日始まり）に出力します。


取得期間の指定・省略時の動作は :ref:`planned-list-date-range` を参照してください。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の予定稼働時間を出力します。

.. code-block:: console

    $ annoworkcli expected_working_time list_weekly --workspace_id org --start_date 2022-01-01  \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "start_date": "2021-12-26",
         "end_date": "2022-01-01",
         "expected_working_hours": 20
      },
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "start_date": "2022-01-02",
         "end_date": "2022-01-08",
         "expected_working_hours": 25
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli expected_working_time list_weekly --workspace_id org --start_date 2022-01-01  \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_weekly/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.list_expected_working_time_weekly.add_parser
   :prog: annoworkcli expected_working_time list_weekly
   :nosubcommands:
   :nodefaultconst:
