=========================================
workspace_member create
=========================================

Description
=================================
ワークスペースメンバを作成します。既存メンバは権限・タグを変更せずスキップします。
脱退済みメンバもスキップし、再招待しません。
``--workspace_tag_id`` を省略した場合、新規メンバにタグを付与しません。
権限の変更には :doc:`update_role` を、タグの変更には :doc:`append_tag` または :doc:`remove_tag` を使用してください。


Examples
=================================

以下のコマンドは、ユーザalice, bobをワークスペース`org`のメンバー（権限: owner）に追加します。

.. code-block::

    $ annoworkcli workspace_member create --workspace_id org \
     --user_id alice bob --role owner


ワークスペースタグも同時に付与する場合：

.. code-block::

    $ annoworkcli workspace_member create --workspace_id org \
     --user_id alice bob --role owner \
     --workspace_tag_id tag1 tag2



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.create_workspace_member.add_parser
   :prog: annoworkcli workspace_member create
   :nosubcommands:
   :nodefaultconst:
