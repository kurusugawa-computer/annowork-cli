==============================================================
actual_working_time list_daily_groupby_tag
==============================================================

Description
=================================
日ごとの実績作業時間を、ワークスペースタグで集計した値を出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとの実績作業時間情報を、ワークスペースタグで集計した値を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list_daily_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "job_id": "caa0da6f-34aa-40cb-abc0-976c9aab3b40",
         "job_name": "MOON",
         "actual_working_hours": {
            "total": 10,
            "by_tag": {
               "type:acceptor": 4,
               "type:monitored": 5
            }
         },
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "PLANET"         
      }
   ]


.. note::

   ``actual_working_hours.total`` は、ワークスペースタグを無視して集計した値です。
   ``actual_working_hours.by_tag`` の値の合計とは限りません。
   
   たとえば上記の出力結果だと、``actual_working_hours.total ≠ actual_working_hours.by_tag.type:acceptor + actual_working_hours.by_tag.type:monitored`` です。

   



タグ別の値は ``actual_working_hours.by_tag`` に出力します。タグ名が ``total`` でも全体合計とは別に集計します。
CSVでは、全体合計は ``actual_working_hours.total``、タグ別の列は ``actual_working_hours.by_tag.<タグ名>`` になります。
従来の ``actual_working_hours.<タグ名>`` を参照する処理は更新してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_hours_daily_groupby_tag.add_parser
   :prog: annoworkcli actual_working_time list_daily_groupby_tag
   :nosubcommands:
   :nodefaultconst: