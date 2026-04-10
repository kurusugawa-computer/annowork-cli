=========================================
expected_working_time list_daily_total
=========================================

Description
=================================
予定稼働時間を日ごとに合計して出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の予定稼働時間（日ごと合計）を出力します。

.. code-block:: 

    $ annoworkcli expected_working_time list_daily_total --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "expected_working_hours": 8
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.list_expected_working_time_daily_total.add_parser
   :prog: annoworkcli expected_working_time list_daily_total
   :nosubcommands:
   :nodefaultconst:
