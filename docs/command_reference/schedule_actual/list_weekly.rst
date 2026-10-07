==================================================
schedule_actual list_weekly
==================================================

Description
=================================
前日までの実績作業時間と当日以降の予定作業時間を結合した週ごとの一覧を出力します。


Examples
=================================

以下のコマンドは、親ジョブ配下の 2022-01-01 から 2022-01-08 までの週ごとの作業時間を出力します。

.. code-block::

    $ annoworkcli schedule_actual list_weekly --workspace_id org --parent_job_id parent_job1 \
      --start_date 2022-01-01 --end_date 2022-01-08 --timezone_offset 9 --format json --output out.json


以下の出力例は、日本時間での実行日が2022-01-02の場合です。
実行日より前は実績作業時間、実行日以降はアサイン時間が出力されます。

.. code-block:: json
   :caption: out.json

   [
      {
         "start_date": "2021-12-26",
         "end_date": "2022-01-01",
         "assigned_working_hours": 0.0,
         "actual_working_hours": 20.0,
         "cumulative_working_hours": 20.0
      },
      {
         "start_date": "2022-01-02",
         "end_date": "2022-01-08",
         "assigned_working_hours": 30.0,
         "actual_working_hours": 0.0,
         "cumulative_working_hours": 50.0
      }
   ]


Usage Details
=================================

週の区切りは日曜日始まり、土曜日終わりです。
集計する作業時間は指定した開始日・終了日の範囲内ですが、出力の ``start_date`` と ``end_date`` は週全体の範囲です。
``cumulative_working_hours`` は、出力対象の先頭週からの累積時間です。

.. argparse::
   :ref: annoworkcli.schedule_actual.list_weekly.add_parser
   :prog: annoworkcli schedule_actual list_weekly
   :nosubcommands:
   :nodefaultconst:
