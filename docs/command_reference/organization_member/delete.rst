=========================================
workspace_member delete
=========================================

Description
=================================
ワークスペースメンバを削除します。



Examples
=================================


以下のコマンドは、ユーザalice, bobをワークスペースorgのワークスペースメバから削除します。

.. code-block:: 

    $ annoworkcli my list_workspace_member delete --workspace_id org \
     --user_id alice bob



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.delete_workspace_member.add_parser
   :prog: annoworkcli workspace_member delete
   :nosubcommands:
   :nodefaultconst: