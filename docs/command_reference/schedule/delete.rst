=========================================
schedule delete
=========================================

Description
=================================
作業計画情報を削除します。

終了日が昨日以前の計画は削除せず、理由をinfoログに出してスキップします。
``--allow_past_end_date`` を指定すると、終了済みの計画も削除できます。
``--yes`` は確認を省略するだけで、この制限を解除しません。
日付の基準は実行環境のローカル日付です。

終了日が今日以降なら、開始日が過去でも削除できます。
その場合は計画全体を削除するため、過去のアサインも削除されます。



Examples
=================================

``--schedule_id`` に削除したい作業計画のschedule_idを指定します。

.. code-block::

    $ annoworkcli schedule delete --workspace_id org --schedule_id id1 id2





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.delete_schedule.add_parser
   :prog: annoworkcli schedule delete
   :nosubcommands:
   :nodefaultconst: