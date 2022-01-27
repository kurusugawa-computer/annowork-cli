=========================================
organization_member delete
=========================================

Description
=================================
組織メンバを削除します。



Examples
=================================


以下のコマンドは、ユーザalice, bobを組織orgの組織メバから削除します。

.. code-block:: 

    $ annoworkcli my list_organization_member delete --organization_id org \
     --user_id alice bob



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.delete_organization_member.add_parser
   :prog: annoworkcli organization_member delete
   :nosubcommands:
   :nodefaultconst: