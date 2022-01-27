=========================================
annofab put_account_external_linkage_info
=========================================

Description
=================================
アカウントの外部連携情報に、AnnoFabから取得したaccount_idを設定します。
AnnoFabのuser_idはAnnoWorkのuser_idと一致している必要があります。



Examples
=================================

以下のコマンドは、ユーザ ``alice`` の外部連携情報に、AnnoFab組織 ``af_org`` に所属するユーザ ``alice`` の情報を設定します。


.. code-block:: 

    $ annoworkcli annofab put_account_external_linkage_info --user_id alice \
     --annofab_organization_name af_org



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.put_account_external_linkage_info.add_parser
   :prog: annoworkcli annofab put_account_external_linkage_info
   :nosubcommands:
   :nodefaultconst: