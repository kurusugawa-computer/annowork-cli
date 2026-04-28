==================================================
schedule_actual list_daily
==================================================

Description
=================================
前日までの実績作業時間と当日以降の予定作業時間を結合した日ごとの一覧を出力します。


Examples
=================================

以下のコマンドは、親ジョブ配下の 2022-01-01 から 2022-01-31 までの日ごとの作業時間を出力します。

.. code-block::

    $ annoworkcli schedule_actual list_daily --workspace_id org --parent_job_id parent_job1 \
      --start_date 2022-01-01 --end_date 2022-01-31 --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-01",
         "assigned_working_hours": 0.0,
         "actual_working_hours": 8.0,
         "cumulative_working_hours": 8.0
      },
      {
         "date": "2022-01-02",
         "assigned_working_hours": 6.0,
         "actual_working_hours": 0.0,
         "cumulative_working_hours": 14.0
      }
   ]


Usage Details
=================================

``cumulative_working_hours`` は、出力対象の先頭日からの累積時間です。

.. argparse::
   :ref: annoworkcli.schedule_actual.list_daily.add_parser
   :prog: annoworkcli schedule_actual list_daily
   :nosubcommands:
   :nodefaultconst:
