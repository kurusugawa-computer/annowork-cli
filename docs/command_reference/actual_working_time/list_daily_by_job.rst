==============================================================
actual_working_time list_daily_by_job
==============================================================

Description
=================================
実績作業時間を日ごと・ジョブごとに集計して出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとの実績作業時間（ジョブごと）を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list_daily_by_job --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "PLANET",
         "job_id": "caa0da6f-34aa-40cb-abc0-976c9aab3b40",
         "job_name": "MOON",
         "actual_working_hours": 7.716666666666667,
         "active_user_count": 3
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_hours_daily_by_job.add_parser
   :prog: annoworkcli actual_working_time list_daily_by_job
   :nosubcommands:
   :nodefaultconst:
