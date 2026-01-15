=========================================
actual_working_time list_weekly
=========================================

Description
=================================
実績作業時間の一覧を週ごと（日曜日始まり）に出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の実績作業時間を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list_weekly --workspace_id org --start_date 2022-01-01  \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_id": "12345678-1234-1234-1234-123456789abc",
         "parent_job_name": "プロジェクトA",
         "job_id": "87654321-4321-4321-4321-cba987654321",
         "job_name": "タスク1",
         "start_date": "2021-12-26",
         "end_date": "2022-01-01",
         "actual_working_hours": 20.5,
      },
      {
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "user_id": "alice",
         "username": "Alice",
         "parent_job_id": "12345678-1234-1234-1234-123456789abc",
         "parent_job_name": "プロジェクトA",
         "job_id": "87654321-4321-4321-4321-cba987654321",
         "job_name": "タスク1",
         "start_date": "2022-01-02",
         "end_date": "2022-01-08",
         "actual_working_hours": 25.0,
      }
   ]




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_time_weekly.add_parser
   :prog: annoworkcli actual_working_time list_weekly
   :nosubcommands:
   :nodefaultconst:
