=========================================
schedule delete_by_schedule_id
=========================================

Description
=================================
``--schedule_id`` に指定した作業計画全体を削除します。
複数ID、または ``file://`` による1行1IDの一覧ファイルを指定できます。
同じIDは1回だけ処理します。親ジョブ・ユーザー・開始日による絞り込みは行いません。

通常は終了日が昨日以前の計画をスキップします。
``--allow_past_end_date`` を指定した場合のみ、終了日が昨日以前の計画も対象にします。
「今日」の判定基準と削除確認・dry_run・処理結果の動作は :ref:`schedule-delete-common-behavior` および :doc:`delete` を参照してください。
``--yes`` は過去の終了日の制限を解除しません。

存在しないIDは警告を出してスキップします。
それ以外の取得APIエラーは失敗として数え、残りを処理してから非0で終了します。

Examples
=================================

.. code-block:: bash

    annoworkcli schedule delete_by_schedule_id --workspace_id org --schedule_id id1 id2

誤作成の取り消し
=================================
:doc:`create` の ``--output_schedule_id`` で保存したID一覧を渡せます。
まず ``--dry_run`` で対象を確認してから、同じ指定で ``--dry_run`` を外して実行します。

.. code-block:: bash

    annoworkcli schedule delete_by_schedule_id --workspace_id org \
      --schedule_id file://created_schedule_ids.txt --allow_past_end_date --dry_run

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.delete_schedule_by_schedule_id.add_parser
   :prog: annoworkcli schedule delete_by_schedule_id
   :nosubcommands:
   :nodefaultconst:
