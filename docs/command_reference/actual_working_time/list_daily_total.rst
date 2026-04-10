==============================================================
actual_working_time list_daily_total
==============================================================

Description
=================================
実績作業時間を日ごとに合計した情報を出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとの実績作業時間（合計）を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list_daily_total --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "actual_working_hours": 7.716666666666667
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_hours_daily_total.add_parser
   :prog: annoworkcli actual_working_time list_daily_total
   :nosubcommands:
   :nodefaultconst:
