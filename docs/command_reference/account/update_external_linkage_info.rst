========================================
account update_external_linkage_info
========================================

Description
=================================
アカウントの外部連携情報を指定したJSONで置き換えます。未指定の項目は引き継ぎません。
対象ユーザーの外部連携情報が取得できない場合はスキップします。



Examples
=================================


以下のコマンドは、ユーザID'alice'の外部連携情報を更新します。

.. code-block::

    $ annoworkcli account update_external_linkage_info  --user_id alice \
     --external_linkage_info '{"annofab": {"account_id": "xxx"}}'






Usage Details
=================================

.. argparse::
   :ref: annoworkcli.account.update_external_linkage_info.add_parser
   :prog: annoworkcli account update_external_linkage_info
   :nosubcommands:
   :nodefaultconst:
