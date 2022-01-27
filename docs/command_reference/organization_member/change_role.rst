=========================================
organization_member change_role
=========================================

Description
=================================
組織メンバのロールを変更します。


Examples
=================================

以下のコマンドは、ユーザalice, bobのロールを"ワーカ"に変更します。

.. code-block:: 

    $ annoworkcli my list_organization_member change_role --organization_id org \
     --user_id alice bob --role worker



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.change_role_of_organization_member.add_parser
   :prog: annoworkcli organization_member change_role
   :nosubcommands:
   :nodefaultconst: