=========================================
workspace create
=========================================

Description
=================================
ワークスペースを作成します。同じIDのワークスペースが存在する場合はエラーになります。


Examples
=================================

以下のコマンドは、ワークスペースID ``org`` のワークスペースを作成します。

.. code-block::

    $ annoworkcli workspace create --workspace_id org --workspace_name "SANDBOX" --email "alice@example.com"



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace.create_workspace.add_parser
   :prog: annoworkcli workspace create
   :nosubcommands:
   :nodefaultconst:
