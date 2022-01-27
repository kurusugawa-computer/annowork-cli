=========================================
organization list
=========================================

Description
=================================
組織の一覧を出力します。


Examples
=================================


以下のコマンドは、自分自身が所属している組織の一覧を出力します。

.. code-block:: 

    $ annoworkcli organization list \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "organization_id": "org",
         "organization_name": "SANDBOX",
         "email": "foo@example.com",
         "created_datetime": "2022-01-11T08:16:58.373Z",
         "updated_datetime": "2022-01-11T08:16:58.373Z"
      }
   ]



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization.list_organization.add_parser
   :prog: annoworkcli organization list
   :nosubcommands:
   :nodefaultconst: