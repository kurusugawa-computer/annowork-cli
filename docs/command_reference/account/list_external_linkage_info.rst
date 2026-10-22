======================================
account list_external_linkage_info
======================================

Description
=================================
アカウント外部連携情報取得の一覧を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、ユーザID'alice'の外部連携情報を出力します。

.. code-block:: console

    $ annoworkcli account list_external_linkage_info  --user_id alice \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "external_linkage_info": {
            "annofab": {
            "account_id": "00589ed0-dd63-40db-abb2-dfe5e13c8299"
            }
         },
         "updated_datetime": "2021-10-29T00:46:19.964Z",
         "user_id": "alice"
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli account list_external_linkage_info  --user_id alice \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_external_linkage_info/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.account.list_external_linkage_info.add_parser
   :prog: annoworkcli account list_external_linkage_info
   :nosubcommands:
   :nodefaultconst:
