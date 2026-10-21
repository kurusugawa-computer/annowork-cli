=========================================
schedule update
=========================================

Description
=================================
既存の作業計画の期間・割当量を更新します。
``--schedule_id`` には複数のID、または ``file://`` によるID一覧ファイルを指定できます。
重複したIDは1件にまとめます。

``--start_date``、``--end_date``、``--hours``、``--percentage`` のうち1つ以上を指定してください。
指定した項目だけを対象の全計画に適用し、未指定の項目は現在値を維持します。
開始日を省略しても今日には変更せず、割当量を省略しても100%には変更しません。

``--hours`` を指定すると固定時間形式、``--percentage`` を指定すると割合形式に切り替えます。
単位・値の範囲、確認・失敗時の動作は :doc:`create` を参照してください。
対象が複数あっても、全計画の更新前に1回だけ確認します。

親ジョブと担当者は変更できません。変更する場合は :doc:`delete` と :doc:`create` を使用してください。
存在しない作業計画を新規作成することはありません。
現在値と同じ指定はスキップします。
更新日時を送信して競合を検出し、競合した場合は上書きせず失敗として扱います。

Examples
=================================

2件の計画の終了日と割当割合を更新します。

.. code-block:: bash

    annoworkcli schedule update --workspace_id org \
      --schedule_id id1 id2 --end_date 2026-11-30 --percentage 50

固定時間に切り替えます。

.. code-block:: bash

    annoworkcli schedule update --workspace_id org \
      --schedule_id file://schedule_ids.txt --hours 4

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.update_schedule.add_parser
   :prog: annoworkcli schedule update
   :nosubcommands:
   :nodefaultconst:
