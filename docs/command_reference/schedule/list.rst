=========================================
schedule list
=========================================

Description
=================================
取得期間の指定・省略時の動作は :ref:`schedule-list-date-range` を参照してください。

作業計画の一覧を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の作業計画情報を出力します。

.. code-block:: console

    $ annoworkcli schedule list --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "schedule_id": "b3fa6635-b6ea-49dc-b1cd-c23a50ed26f1",
         "workspace_id": "org",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "workspace_member_id": "53ba2c39-5c02-4df4-abdb-eab0143ac0c7",
         "start_date": "2021-12-28",
         "end_date": "2022-01-03",
         "type": "percentage",
         "value": 100,
         "created_datetime": "2021-12-27T08:14:45.882Z",
         "updated_datetime": "2021-12-27T08:19:16.352Z",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_name": "MOON",
         "assigned_working_hours": 10.0
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli schedule list --workspace_id org --start_date 2022-01-01 \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_schedule.add_parser
   :prog: annoworkcli schedule list
   :nosubcommands:
   :nodefaultconst:

参照先の親ジョブやメンバーが存在しない作業計画も出力します。
取得できない名前やユーザー情報は、JSONでは ``null``、CSVでは空欄になります。
