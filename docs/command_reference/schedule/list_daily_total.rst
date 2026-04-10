=========================================
schedule list_daily_total
=========================================

Description
=================================
作業計画から求めたアサイン時間を日ごとに合計して出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとのアサイン時間（合計）を出力します。

.. code-block:: 

    $ annoworkcli schedule list_daily_total --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "assigned_working_hours": 12.0
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_total.add_parser
   :prog: annoworkcli schedule list_daily_total
   :nosubcommands:
   :nodefaultconst:
