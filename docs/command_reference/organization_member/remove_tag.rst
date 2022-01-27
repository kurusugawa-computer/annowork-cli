=========================================
organization_member remove_tag
=========================================

Description
=================================
組織メンバから組織タグを削除します。



Examples
=================================

以下のコマンドは、ユーザalice, bobから、組織タグtag1, tag2を除去します。

.. code-block:: 

    $ annoworkcli my list_organization_member remove_tag --organization_id org \
     --user_id alice bob --organization_tag_id tag1 tag2




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.remove_tag_to_organization_member.add_parser
   :prog: annoworkcli organization_member remove_tag
   :nosubcommands:
   :nodefaultconst: