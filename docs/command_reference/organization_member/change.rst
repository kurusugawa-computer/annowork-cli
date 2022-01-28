=========================================
organization_member change
=========================================

Description
=================================
組織メンバの情報（ロールなど）を変更します。


Examples
=================================

以下のコマンドは、ユーザalice, bobのロールを"ワーカ"に変更します。

.. code-block:: 

    $ annoworkcli my list_organization_member change --organization_id org \
     --user_id alice bob --role worker



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.change_organization_member_properties.add_parser
   :prog: annoworkcli organization_member change
   :nosubcommands:
   :nodefaultconst: