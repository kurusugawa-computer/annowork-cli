=========================================
organization_member list
=========================================

Description
=================================
組織メンバの一覧を出力します。無効化されたメンバも出力します。


Examples
=================================

以下のコマンドは、組織面ンバの一覧を出力します。

.. code-block:: 

    $ annoworkcli organization_member list \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "organization_member_id": "e2d334cf-dfe8-411e-acd6-fe4e39687fea",
         "organization_id": "org",
         "account_id": "b7d76c01-4a10-438e-a516-d5768afb7709",
         "user_id": "alice",
         "username": "Alice",
         "role": "manager",
         "status": "active",
         "created_datetime": "2021-10-31T14:49:59.841Z",
         "updated_datetime": "2021-11-02T05:28:36.714Z"
      }
   ]


``--show_organization_tag`` を付けると、組織メンバに付与されている組織タグの情報も出力します。

.. code-block:: 

    $ annoworkcli organization_member list --show_organization_tag \
     --format json --output out.json



.. code-block:: json
   :caption: out.json

   [
      {
         "organization_member_id": "e2d334cf-dfe8-411e-acd6-fe4e39687fea",
         "organization_id": "org",
         "account_id": "b7d76c01-4a10-438e-a516-d5768afb7709",
         "user_id": "alice",
         "username": "Alice",
         "role": "manager",
         "status": "active",
         "created_datetime": "2021-10-31T14:49:59.841Z",
         "updated_datetime": "2021-11-02T05:28:36.714Z",
         "organization_tag_ids": [
            "tag"
         ],
         "organization_tag_names": [
            "TAG"
         ]         
      }
   ]








Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.list_organization_member.add_parser
   :prog: annoworkcli organization_member list
   :nosubcommands:
   :nodefaultconst: