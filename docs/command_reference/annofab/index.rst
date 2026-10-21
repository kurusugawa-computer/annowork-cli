==================================================
annofab
==================================================

Description
=================================
Annofab連携に関するサブコマンドです。
``list_assigned_hours`` と、``--actual_file`` を指定した ``reshape_working_hours`` は、Annofab APIにアクセスしないためAnnofabの認証は不要です。
これらの操作にもAnnoworkの認証は必要です。


Available Commands
=================================

Annofab APIにアクセスするコマンドには、AnnoworkとAnnofabの認証情報が必要です。
設定方法は :doc:`../../user_guide/configurations` を参照してください。

.. toctree::
   :maxdepth: 1
   :titlesonly:

   list_assigned_hours
   list_job
   list_working_hours
   put_account_external_linkage_info
   put_job
   reshape_working_hours
   visualize_statistics

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.subcommand.add_parser
   :prog: annoworkcli annofab
   :nosubcommands: