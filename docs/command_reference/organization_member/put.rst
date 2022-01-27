=========================================
organization_member put
=========================================

Description
=================================
組織メンバを登録します。



Examples
=================================

以下のコマンドは、ユーザalice, bobを組織orgの組織メンバに追加します。

.. code-block:: 

    $ annoworkcli my list_organization_member put --organization_id org \
     --user_id alice bob 



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.organization_member.put_organization_member.add_parser
   :prog: annoworkcli organization_member put
   :nosubcommands:
   :nodefaultconst: