==================================================
schedule_actual list_daily
==================================================

Description
=================================
前日までの実績作業時間と当日以降の予定作業時間を結合した日ごとの一覧を出力します。


Examples
=================================

以下のコマンドは、親ジョブ配下の 2022-01-01 から 2022-01-02 までの日ごとの作業時間を出力します。

.. code-block::

    $ annoworkcli schedule_actual list_daily --workspace_id org --parent_job_id parent_job1 \
      --start_date 2022-01-01 --end_date 2022-01-02 --timezone_offset 9 --format json --output out.json


以下の出力例は、日本時間での実行日が2022-01-02の場合です。
実行日より前は実績作業時間、実行日以降はアサイン時間が出力されます。

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
開始日と終了日の両方を指定すると、その期間の全日を出力します。作業時間がない日は0になります。

.. argparse::
   :ref: annoworkcli.schedule_actual.list_daily.add_parser
   :prog: annoworkcli schedule_actual list_daily
   :nosubcommands:
   :nodefaultconst:
