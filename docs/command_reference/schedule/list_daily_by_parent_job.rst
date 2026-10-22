=========================================
schedule list_daily_by_parent_job
=========================================

Description
=================================
取得期間の指定・省略時の動作は :ref:`planned-list-date-range` を参照してください。

作業計画から求めたアサイン時間を日ごと・親ジョブごとに集計して出力します。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の日ごとのアサイン時間（親ジョブごと）を出力します。

.. code-block:: console

    $ annoworkcli schedule list_daily_by_parent_job --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "MOON",
         "assigned_working_hours": 12.0,
         "active_user_count": 4
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli schedule list_daily_by_parent_job --workspace_id org --start_date 2022-01-01 \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_daily_by_parent_job/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_by_parent_job.add_parser
   :prog: annoworkcli schedule list_daily_by_parent_job
   :nosubcommands:
   :nodefaultconst:
