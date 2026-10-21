=========================================
workspace_member update_role
=========================================

Description
=================================
ワークスペースメンバのロールを変更します。


Examples
=================================

以下のコマンドは、ユーザalice, bobのロールを"ワーカ"に変更します。

.. code-block:: 

    $ annoworkcli workspace_member update_role --workspace_id org \
     --user_id alice bob --role worker



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.update_workspace_member_role.add_parser
   :prog: annoworkcli workspace_member update_role
   :nosubcommands:
   :nodefaultconst: