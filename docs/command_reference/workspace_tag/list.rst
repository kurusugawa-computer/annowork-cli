=========================================
workspace_tag list
=========================================

Description
=================================
ワークスペースタグの一覧を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、ワークスペースタグの一覧を出力します。

.. code-block:: console

    $ annoworkcli workspace_tag list --workspace_id ws \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_tag_id": "company_kurusugawa",
         "workspace_id": "ws",
         "workspace_tag_name": "company:来栖川電算",
         "created_datetime": "2022-03-14T04:15:05.243Z",
         "updated_datetime": "2022-03-14T04:15:05.243Z"
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli workspace_tag list --workspace_id ws \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_tag.list_workspace_tag.add_parser
   :prog: annoworkcli workspace_tag list
   :nosubcommands:
   :nodefaultconst:
