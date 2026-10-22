==================================================
schedule
==================================================

Description
=================================
作業計画関係のサブコマンド

作業計画のアサイン先は、実績を記録するジョブの1階層上の親ジョブです。
引数には ``--parent_job_id`` / ``-pj``、出力には ``parent_job_id`` / ``parent_job_name`` を使用します。
指定するIDはアサイン先自身のIDです。そこからさらに親ジョブをたどることはありません。


一覧・集計コマンドの取得期間は :ref:`planned-list-date-range` を参照してください。


Available Commands
=================================

.. toctree::
   :maxdepth: 1
   :titlesonly:

   create
   delete
   delete_by_schedule_id
   list
   list_daily
   list_daily_by_parent_job
   list_daily_groupby_tag
   list_weekly
   list_workload_daily
   list_workload_daily_by_user
   update
   update_end_date
   update_start_date

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.subcommand.add_parser
   :prog: annoworkcli schedule
   :nosubcommands:
