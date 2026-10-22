=========================================
workspace_tag create
=========================================

Description
=================================
ワークスペースタグを作成します。同じIDのタグが存在する場合はエラーになります。
``--workspace_tag_id`` を省略するとUUIDを生成します。



Examples
=================================

以下のコマンドは、``company:来栖川電算`` という名前のワークスペースタグを作成します。

.. code-block::

    $ annoworkcli workspace_tag create --workspace_id ws \
     --workspace_tag_name "company:来栖川電算" --workspace_tag_id company_kurusugawa

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_tag.create_workspace_tag.add_parser
   :prog: annoworkcli workspace_tag create
   :nosubcommands:
   :nodefaultconst:
