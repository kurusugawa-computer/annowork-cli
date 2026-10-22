=========================================
expected_working_time list_groupby_tag
=========================================

Description
=================================
ワークスペースタグで集計した予定稼働時間を出力します。


``--user_id``、``--start_date``、``--end_date`` のいずれかを1つ以上指定してください。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、2022-01-01以降の予定稼働時間を、ワークスペースタグで集計した値を出力します。

.. code-block:: console

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


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli expected_working_time list_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_groupby_tag/out.csv
   :header-rows: 1

``expected_working_hours`` の ``total`` と ``by_tag`` の意味は :ref:`tag-grouped-output` を参照してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.list_expected_working_time_groupby_tag.add_parser
   :prog: annoworkcli expected_working_time list_groupby_tag
   :nosubcommands:
   :nodefaultconst:
