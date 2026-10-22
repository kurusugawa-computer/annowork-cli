=========================================
workspace_member list
=========================================

Description
=================================
メンバの一覧を出力します。無効化されたメンバも出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

以下のコマンドは、メンバーの一覧を出力します。

.. code-block:: console

    $ annoworkcli workspace_member list --workspace_id org \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "e2d334cf-dfe8-411e-acd6-fe4e39687fea",
         "workspace_id": "org",
         "account_id": "b7d76c01-4a10-438e-a516-d5768afb7709",
         "user_id": "alice",
         "username": "Alice",
         "role": "manager",
         "status": "active",
         "created_datetime": "2021-10-31T14:49:59.841Z",
         "updated_datetime": "2021-11-02T05:28:36.714Z"
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli workspace_member list --workspace_id org \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list/out.csv
   :header-rows: 1

``--show_workspace_tag`` を付けると、メンバーに付与されているタグの情報も出力します。

.. code-block:: console

    $ annoworkcli workspace_member list --workspace_id org --show_workspace_tag \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "e2d334cf-dfe8-411e-acd6-fe4e39687fea",
         "workspace_id": "org",
         "account_id": "b7d76c01-4a10-438e-a516-d5768afb7709",
         "user_id": "alice",
         "username": "Alice",
         "role": "manager",
         "status": "active",
         "created_datetime": "2021-10-31T14:49:59.841Z",
         "updated_datetime": "2021-11-02T05:28:36.714Z",
         "workspace_tag_ids": [
            "tag"
         ],
         "workspace_tag_names": [
            "TAG"
         ]         
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli workspace_member list --workspace_id org --show_workspace_tag \
     --format csv --output with_tags.csv

.. csv-table:: with_tags.csv
   :file: list/with_tags.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.list_workspace_member.add_parser
   :prog: annoworkcli workspace_member list
   :nosubcommands:
   :nodefaultconst:
