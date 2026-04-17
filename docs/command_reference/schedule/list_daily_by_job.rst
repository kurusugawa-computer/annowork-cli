=========================================
schedule list_daily_by_job
=========================================

Description
=================================
作業計画から求めたアサイン時間を日ごと・ジョブごとに集計して出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとのアサイン時間（ジョブごと）を出力します。

.. code-block:: 

    $ annoworkcli schedule list_daily_by_job --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "job_name": "MOON",
         "assigned_working_hours": 12.0,
         "active_user_count": 4
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_by_job.add_parser
   :prog: annoworkcli schedule list_daily_by_job
   :nosubcommands:
   :nodefaultconst:
