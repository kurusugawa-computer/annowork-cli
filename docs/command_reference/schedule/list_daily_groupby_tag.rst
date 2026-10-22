=========================================
schedule list_daily_groupby_tag
=========================================

Description
=================================
日ごとのアサイン時間を、ワークスペースタグで集計した値を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の日毎のアサイン時間を、ワークスペースタグで集計した値を出力します。

.. code-block:: console

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


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli schedule list_daily_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_daily_groupby_tag/out.csv
   :header-rows: 1

``assigned_working_hours`` の ``total`` と ``by_tag`` の意味は :ref:`tag-grouped-output` を参照してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_groupby_tag.add_parser
   :prog: annoworkcli schedule list_daily_groupby_tag
   :nosubcommands:
   :nodefaultconst:
