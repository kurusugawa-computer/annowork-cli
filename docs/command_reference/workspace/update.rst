=========================================
workspace update
=========================================

Description
=================================
ワークスペースを更新します。指定したIDが存在しない場合はエラーになります。
``--workspace_name`` と ``--email`` のうち、指定した項目のみ更新します。
少なくとも1項目を指定してください。未指定の項目は維持します。

Examples
=================================

.. code-block::

    $ annoworkcli workspace update --workspace_id org --workspace_name "新しい名前"

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace.update_workspace.add_parser
   :prog: annoworkcli workspace update
   :nosubcommands:
   :nodefaultconst:
