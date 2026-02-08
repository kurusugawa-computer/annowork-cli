=========================================
workspace_member put
=========================================

Description
=================================
ワークスペースメンバを登録します。



Examples
=================================

以下のコマンドは、ユーザalice, bobをワークスペース`org`のメンバー（権限: owner）に追加します。

.. code-block:: 

    $ annoworkcli workspace_member put --workspace_id org \
     --user_id alice bob --role owner


ワークスペースタグも同時に付与する場合：

.. code-block:: 

    $ annoworkcli workspace_member put --workspace_id org \
     --user_id alice bob --role owner \
     --workspace_tag_id tag1 tag2 



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.put_workspace_member.add_parser
   :prog: annoworkcli workspace_member put
   :nosubcommands:
   :nodefaultconst: