=========================================
workspace_tag update
=========================================

Description
=================================
ワークスペースタグを更新します。指定したIDが存在しない場合はエラーになります。
``--workspace_tag_id`` で指定したタグの名前を更新します。

Examples
=================================

.. code-block::

    $ annoworkcli workspace_tag update --workspace_id org --workspace_tag_id tag1 --workspace_tag_name "新しいタグ名"

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_tag.update_workspace_tag.add_parser
   :prog: annoworkcli workspace_tag update
   :nosubcommands:
   :nodefaultconst:
