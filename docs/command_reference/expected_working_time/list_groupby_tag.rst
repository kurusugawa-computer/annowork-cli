=========================================
expected_working_time list_groupby_tag
=========================================

Description
=================================
ワークスペースタグで集計した予定稼働時間を出力します。



``--user_id``、``--start_date``、``--end_date`` のいずれかを1つ以上指定してください。

Examples
=================================

以下のコマンドは、2022-01-01以降の予定稼働時間を、ワークスペースタグで集計した値を出力します。

.. code-block:: 

    $ annoworkcli expected_working_time list_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "expected_working_hours": {
            "total": 8.0,
            "by_tag": {
               "type:acceptor": 4.0,
               "type:monitored": 5.0
            }
         }
      }
   ]



.. note::

   ``expected_working_hours.total`` は、ワークスペースタグを無視して集計した値です。
   ``expected_working_hours.by_tag`` の値の合計とは限りません。

   たとえば上記の出力結果だと、``expected_working_hours.total ≠ expected_working_hours.by_tag.type:acceptor + expected_working_hours.by_tag.type:monitored`` です。



タグ別の値は ``expected_working_hours.by_tag`` に出力します。タグ名が ``total`` でも全体合計とは別に集計します。
CSVでは、全体合計は ``expected_working_hours.total``、タグ別の列は ``expected_working_hours.by_tag.<タグ名>`` になります。
従来の ``expected_working_hours.<タグ名>`` を参照する処理は更新してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.list_expected_working_time_groupby_tag.add_parser
   :prog: annoworkcli expected_working_time list_groupby_tag
   :nosubcommands:
   :nodefaultconst: