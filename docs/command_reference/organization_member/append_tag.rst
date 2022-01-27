=========================================
organization_member append_tag
=========================================

Description
=================================
組織メンバに組織タグを追加します。



Examples
=================================


以下のコマンドは、ユーザalice, bobに、組織タグtag1, tag2を付与します。

.. code-block:: 

    $ annoworkcli my list_organization_member append_tag --organization_id org \
     --user_id alice bob --organization_tag_id tag1 tag2





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.append_tag_to_organization_member.add_parser
   :prog: annoworkcli organization_member append_tag
   :nosubcommands:
   :nodefaultconst: