=========================================
workspace list
=========================================

Description
=================================
ワークスペースの一覧を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。


以下のコマンドは、自分自身が所属しているワークスペースの一覧を出力します。

.. code-block:: console

    $ annoworkcli workspace list \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_id": "org",
         "workspace_name": "SANDBOX",
         "email": "foo@example.com",
         "created_datetime": "2022-01-11T08:16:58.373Z",
         "updated_datetime": "2022-01-11T08:16:58.373Z"
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli workspace list \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace.list_workspace.add_parser
   :prog: annoworkcli workspace list
   :nosubcommands:
   :nodefaultconst:
