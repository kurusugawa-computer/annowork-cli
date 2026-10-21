=========================================
schedule list_daily_by_parent_job
=========================================

Description
=================================
作業計画から求めたアサイン時間を日ごと・親ジョブごとに集計して出力します。


``--parent_job_id``、``--start_date``、``--end_date`` のいずれかを1つ以上指定してください。

Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとのアサイン時間（親ジョブごと）を出力します。

.. code-block:: 

    $ annoworkcli schedule list_daily_by_parent_job --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "MOON",
         "assigned_working_hours": 12.0,
         "active_user_count": 4
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_by_parent_job.add_parser
   :prog: annoworkcli schedule list_daily_by_parent_job
   :nosubcommands:
   :nodefaultconst:
