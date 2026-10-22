==============================================================
actual_working_time list_daily_groupby_tag
==============================================================

Description
=================================
日ごとの実績作業時間を、ワークスペースタグで集計した値を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の日ごとの実績作業時間情報を、ワークスペースタグで集計した値を出力します。

.. code-block:: console

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


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli actual_working_time list_daily_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_daily_groupby_tag/out.csv
   :header-rows: 1

``actual_working_hours`` の ``total`` と ``by_tag`` の意味は :ref:`tag-grouped-output` を参照してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_hours_daily_groupby_tag.add_parser
   :prog: annoworkcli actual_working_time list_daily_groupby_tag
   :nosubcommands:
   :nodefaultconst:
