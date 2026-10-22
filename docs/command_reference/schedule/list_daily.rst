=========================================
schedule list_daily
=========================================

Description
=================================
取得期間の指定・省略時の動作は :ref:`planned-list-date-range` を参照してください。

作業計画から求めたアサイン時間を日ごとに出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の日毎のアサイン時間を出力します。

.. code-block:: console

    $ annoworkcli schedule list_daily --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "MOON",
         "workspace_member_id": "50c5587a-219a-47d6-9641-0eb273996966",
         "user_id": "alice",
         "username": "Alice",
         "assigned_working_hours": 5.0
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli schedule list_daily --workspace_id org --start_date 2022-01-01 \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_daily/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily.add_parser
   :prog: annoworkcli schedule list_daily
   :nosubcommands:
   :nodefaultconst:
