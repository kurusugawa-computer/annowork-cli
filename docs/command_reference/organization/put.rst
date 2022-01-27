=========================================
organization put
=========================================

Description
=================================
組織を作成/更新します。


Examples
=================================

以下のコマンドは、組織ID ``org`` の組織を作成します。

.. code-block:: 

    $ annoworkcli organization put --organization_id org --email "alice@example.com" 



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization.put_organization.add_parser
   :prog: annoworkcli organization put
   :nosubcommands:
   :nodefaultconst: