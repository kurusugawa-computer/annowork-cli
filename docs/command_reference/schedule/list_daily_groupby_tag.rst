=========================================
schedule list_daily_groupby_tag
=========================================

Description
=================================
日ごとのアサイン時間を、ワークスペースタグで集計した値を出力します。



Examples
=================================

以下のコマンドは、2022-01-01以降の日毎のアサイン時間を、ワークスペースタグで集計した値を出力します。

.. code-block:: 

    $ annoworkcli schedule list_daily_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "MOON",
         "assigned_working_hours": {
            "total": 8.0,
            "by_tag": {
               "type:acceptor": 6.0,
               "type:monitored": 8.0
            }
         }
      }
   ]


.. note::

   ``assigned_working_hours.total`` は、ワークスペースタグを無視して集計した値です。
   ``assigned_working_hours.by_tag`` の値の合計とは限りません。

   たとえば上記の出力結果だと、``assigned_working_hours.total ≠ assigned_working_hours.by_tag.type:acceptor + assigned_working_hours.by_tag.type:monitored`` です。




タグ別の値は ``assigned_working_hours.by_tag`` に出力します。タグ名が ``total`` でも全体合計とは別に集計します。
CSVでは、全体合計は ``assigned_working_hours.total``、タグ別の列は ``assigned_working_hours.by_tag.<タグ名>`` になります。
従来の ``assigned_working_hours.<タグ名>`` を参照する処理は更新してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_groupby_tag.add_parser
   :prog: annoworkcli schedule list_daily_groupby_tag
   :nosubcommands:
   :nodefaultconst: