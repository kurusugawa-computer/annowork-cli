=========================================
workspace_member put
=========================================

Description
=================================
ワークスペースメンバを登録します。既存メンバの権限とタグも更新します。
``--workspace_tag_id`` はタグ一覧を置き換えます。未指定の場合は既存タグをすべて解除します。
タグの追加だけを行う場合は :doc:`append_tag` を、権限だけを変更する場合は :doc:`update_role` を使用してください。



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
