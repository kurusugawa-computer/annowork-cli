==================================================
schedule
==================================================

Description
=================================
作業計画関係のサブコマンド

作業計画のアサイン先は、実績を記録するジョブの1階層上の親ジョブです。
引数には ``--parent_job_id`` / ``-pj``、出力には ``parent_job_id`` / ``parent_job_name`` を使用します。
指定するIDはアサイン先自身のIDです。そこからさらに親ジョブをたどることはありません。

.. warning::

   旧引数 ``--job_id`` / ``-j``、旧出力名 ``job_id`` / ``job_name``、
   旧コマンド ``list_daily_by_job`` は廃止しました。
   集計には ``list_daily_by_parent_job`` を使用してください。
   既存のスクリプトやCSV・JSONを使用する処理も更新が必要です。


Available Commands
=================================

.. toctree::
   :maxdepth: 1
   :titlesonly:

   create
   delete
   list
   list_daily
   list_daily_by_parent_job
   list_daily_groupby_tag
   list_weekly
   update
   update_start_date

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.subcommand.add_parser
   :prog: annoworkcli schedule
   :nosubcommands:
