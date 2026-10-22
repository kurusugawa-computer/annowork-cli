=========================================
schedule list_weekly
=========================================

Description
=================================
作業計画から求めたアサイン時間をメンバー・ジョブ・週ごと（日曜日始まり）に出力します。


``--user_id``、``--parent_job_id``、``--start_date``、``--end_date`` のいずれかを1つ以上指定してください。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降のアサイン時間を出力します。

.. code-block:: console

    $ annoworkcli schedule list_weekly --workspace_id org --start_date 2022-01-01  \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_id": "job1",
         "parent_job_name": "MOON",
         "start_date": "2021-12-26",
         "end_date": "2022-01-01",
         "assigned_working_hours": 20
      },
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_id": "job1",
         "parent_job_name": "MOON",
         "start_date": "2022-01-02",
         "end_date": "2022-01-08",
         "assigned_working_hours": 25
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli schedule list_weekly --workspace_id org --start_date 2022-01-01  \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_weekly/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_schedule_weekly.add_parser
   :prog: annoworkcli schedule list_weekly
   :nosubcommands:
   :nodefaultconst:
