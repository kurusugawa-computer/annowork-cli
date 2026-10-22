=========================================
actual_working_time list_weekly
=========================================

Description
=================================
実績作業時間の一覧を週ごと（日曜日始まり、土曜日終わり）に出力します。
``--timezone_offset`` で指定したタイムゾーンを日付と週の区切りに使用します。未指定の場合はローカルのタイムゾーンを使用します。
未指定時は実績日の夏時間規則を反映します。明示した時差は季節によらず固定値として使用します。
日付や週をまたぐ実績は、各日に作業した時間に分割してから週ごとに集計します。

``--start_date`` と ``--end_date`` を指定した場合は、その期間内の作業時間だけを集計します（開始日・終了日を含みます）。
出力の ``start_date`` と ``end_date`` は、集計対象期間にかかわらず週全体の範囲を示します。

``--user_id``、``--job_id``、``--parent_job_id``、``--start_date``、``--end_date`` のいずれかを1つ以上指定してください。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の実績作業時間を出力します。

.. code-block:: console

    $ annoworkcli actual_working_time list_weekly --workspace_id org --start_date 2022-01-01  \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_id": "parent_job1",
         "parent_job_name": "Parent Job1",
         "job_id": "job1",
         "job_name": "Job1",
         "start_date": "2021-12-26",
         "end_date": "2022-01-01",
         "actual_working_hours": 20.5
      },
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_id": "parent_job1",
         "parent_job_name": "Parent Job1",
         "job_id": "job2",
         "job_name": "Job2",
         "start_date": "2022-01-02",
         "end_date": "2022-01-08",
         "actual_working_hours": 25.0
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli actual_working_time list_weekly --workspace_id org --start_date 2022-01-01  \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_weekly/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_time_weekly.add_parser
   :prog: annoworkcli actual_working_time list_weekly
   :nosubcommands:
   :nodefaultconst:
