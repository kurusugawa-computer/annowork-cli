=========================================
my list_workspace_member
=========================================

Description
=================================
所属しているワークスペースでの自分自身のメンバー情報を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。


以下のコマンドは、自身のワークスペースメンバの一覧を出力します。

.. code-block:: console

    $ annoworkcli my list_workspace_member \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "a5cd6a09-e740-4c34-8981-fe3d1b0e0bde",
         "workspace_id": "org",
         "account_id": "0a998d6f-9b53-4d96-ba89-14edccd9ce0b",
         "user_id": "alice",
         "username": "Alice",
         "role": "owner",
         "status": "active",
         "created_datetime": "2022-01-11T08:16:58.373Z",
         "updated_datetime": "2022-01-11T08:16:58.373Z"
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli my list_workspace_member \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_workspace_member/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.my.list_my_workspace_member.add_parser
   :prog: annoworkcli my list_workspace_member
   :nosubcommands:
   :nodefaultconst:
