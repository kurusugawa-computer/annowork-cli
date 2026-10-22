=========================================
schedule delete
=========================================

Description
=================================
単一の親ジョブを指定し、条件に一致する作業計画全体を削除します。
``--parent_job_id`` は必須です。アサイン先IDの意味は :doc:`index` を参照してください。

終了日が昨日以前の計画は常に対象外です。「今日」は実行環境のローカル日付で判定します。
過去に開始して継続中の計画や今日終了する計画は対象になります。
期間の短縮・分割は行わず、過去の部分も含めて計画全体を削除します。

* ``--user_id``: 対象ユーザーを限定します。複数指定、または ``file://`` による1行1IDの一覧ファイルを指定できます。省略時は全員が対象です。
* ``--from_start_date``: 開始日が指定日以降の計画を対象にします。
* ``--to_start_date``: 開始日が指定日以前の計画を対象にします。

異なる引数の条件はすべてAND、複数のユーザーIDはORです。
日付はYYYY-MM-DD形式で境界日を含み、片方だけでも指定できます。
不正な日付や、開始日の下限が上限より後の場合はエラーになります。
開始日の範囲を省略すると、終了日が今日以降の計画すべてが対象です。


Examples
=================================

親ジョブのうち終了日が今日以降の計画を削除します。

.. code-block:: bash

    annoworkcli schedule delete --workspace_id org --parent_job_id parent1

11月に開始するaliceとbobの計画を対象に、削除予定を確認します。
12月以降に終了する計画も対象になります。

.. code-block:: bash

    annoworkcli schedule delete --workspace_id org --parent_job_id parent1 \
      --user_id alice bob --from_start_date 2026-11-01 --to_start_date 2026-11-30 --dry_run

.. _schedule-delete-common-behavior:

Common Behavior
=================================
削除前に対象条件・一覧・件数をinfoログに表示し、全件について1回だけ確認します。
拒否すると全件をスキップします。``--yes`` は確認を省略するだけです。
``--dry_run`` は確認も削除も行わず、対象一覧と件数を表示します。``--yes`` と併用しても削除しません。
対象が0件の場合はその旨を表示して正常終了します。

成功・スキップ・失敗の件数を最後にinfoログへ出力します。
削除APIのエラーが発生しても残りを処理し、最後に非0で終了します。成功した削除は取り消しません。

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.delete_schedule.add_parser
   :prog: annoworkcli schedule delete
   :nosubcommands:
   :nodefaultconst:
