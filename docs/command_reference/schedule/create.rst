=========================================
schedule create
=========================================

Description
=================================
1つの親ジョブに、指定したユーザーごとの作業計画を作成します。
``--parent_job_id`` は1個、``--user_id`` は複数指定できます。
アサイン先IDの意味は :doc:`index` を参照してください。

``--start_date`` を省略すると、実行環境のローカル日付の今日を使用します。
``--end_date`` は必須で、開始日・終了日の両方を期間に含みます。

``--hours`` と ``--percentage`` は同時指定できません。
両方省略すると、各ユーザーの予定稼働時間の100%を割り当てます。
予定稼働時間が未登録の日の割当時間は0時間です。
既存の作業計画を考慮して空き時間を計算する機能はありません。

``--hours`` は期間全体の合計ではなく、各ユーザーの1日あたりの時間です。
休日を除外せず、期間中の各日に適用します。指定範囲は0.01〜24時間です。
``--percentage`` の指定範囲は0.01〜100%です。

同一コマンド内で重複したユーザーIDは1人にまとめます。
既存計画の有無にかかわらず新しいIDで作成するため、再実行すると計画が追加されます。
作成した作業計画IDはinfoログに出力します。

Examples
=================================

今日から指定日まで、aliceとbobを100%でアサインします。

.. code-block:: bash

    annoworkcli schedule create --workspace_id org \
      --parent_job_id parent1 --user_id alice bob --end_date 2026-11-30

1人につき1日4時間の計画を作成します。

.. code-block:: bash

    annoworkcli schedule create --workspace_id org \
      --parent_job_id parent1 --user_id file://users.txt \
      --start_date 2026-11-02 --end_date 2026-11-06 --hours 4

Common Behavior
=================================

通常実行では、対象全体の処理前に1回だけ確認します。対象が複数あっても確認回数は変わりません。
確認で拒否すると全件をスキップします。``--yes`` / ``-y`` で確認を省略できます。

開始日が終了日より後になる入力や、範囲外・非有限の割当量はエラーです。
ID一覧ファイルは1行につき1つのIDを記載します。

成功・スキップ・失敗の件数を最後にinfoログへ出力します。
確認で拒否したユーザーはスキップ、存在しないユーザーやAPIエラーは失敗として集計します。
失敗した場合も、非0で終了する前に次の形式で結果を出力します。

.. code-block:: text

    成功: 0 件、スキップ: 0 件、失敗: 2 件

存在しない対象やAPIエラーで失敗した場合は、残りを処理してから非0で終了します。
成功した処理を取り消すことはありません。

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.create_schedule.add_parser
   :prog: annoworkcli schedule create
   :nosubcommands:
   :nodefaultconst:
