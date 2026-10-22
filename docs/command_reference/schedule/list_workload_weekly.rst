============================================================
schedule list_workload_weekly
============================================================

Description
=================================

取得期間の指定・省略時の動作は :ref:`planned-list-date-range` を参照してください。

全ユーザーの予定稼働時間と親ジョブ別のアサイン時間を週ごとに比較します。
JSONには週ごとのユーザー別集計と、親ジョブごとの担当者別内訳も含めます。
CSVは1週1行で、ユーザー別内訳は含めません。
指定期間に含まれる全週を出力します。データがない週は各合計を0、内訳を空配列にします。
終了日省略時は、作業計画・予定稼働時間の最終データが属する週まで出力します。
終了日省略時に対象データがなければ、JSONは空配列、CSVは固定列のヘッダーだけを出力します。

週の区切りと集計方法
---------------------------------

既存の :doc:`list_weekly` と同じく、日曜日から土曜日までを1週とします。
``start_date`` と ``end_date`` は、その週の日曜日と土曜日です。
指定期間の端が週の途中でも週の日付を表示し、合計するのは指定期間内の日だけです。
たとえば ``--start_date 2026-11-02 --end_date 2026-11-04`` では、
週の日付は ``2026-11-01`` ～ ``2026-11-07``、集計対象は11月2日～4日です。

割合指定のアサインは、各ユーザーの当日の予定稼働時間から日別に時間換算してから合計します。
予定稼働時間の未登録、0時間の登録、時間指定の扱いは :doc:`list_workload_daily` と同じです。
``remaining_working_hours`` は週の予定稼働時間合計からアサイン時間合計を引いた値です。
週の差分は日ごとの超過と余裕を相殺し、全体の差分はユーザー間の超過と余裕も相殺します。
週の差分が正でも特定の日やユーザーには超過がある場合があるため、
詳細の確認には :doc:`list_workload_daily_by_user` を使ってください。

親ジョブはIDで合算してID順に、メンバーは ``workspace_member_id`` 順に並べます。
週は開始日順です。JSONのユーザー・親ジョブの情報とCSVの親ジョブ列の仕様は
:doc:`list_workload_daily` と同じです。ただしCSVの固定日付列は ``date`` から
``start_date`` と ``end_date`` に置き換わります。親ジョブ名は週次版の固定列名との衝突も検証します。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

.. code-block:: console

    $ annoworkcli schedule list_workload_weekly --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-07 --format csv --output workload.csv

.. csv-table:: workload.csv
   :file: list_workload_weekly/workload.csv
   :header-rows: 1

.. code-block:: console

    $ annoworkcli schedule list_workload_weekly --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-07 --format json --output workload.json

.. code-block:: json
   :caption: workload.json

    [
      {
        "start_date": "2026-11-01",
        "end_date": "2026-11-07",
        "expected_working_hours": 40,
        "assigned_working_hours": 30,
        "remaining_working_hours": 10,
        "members": [
          {
            "workspace_member_id": "member-1",
            "user_id": "alice",
            "username": "Alice",
            "expected_working_hours": 40,
            "assigned_working_hours": 30,
            "remaining_working_hours": 10
          }
        ],
        "assignments": [
          {
            "parent_job_id": "job-a",
            "parent_job_name": "ジョブA",
            "assigned_working_hours": 30,
            "members": [
              {
                "workspace_member_id": "member-1",
                "user_id": "alice",
                "username": "Alice",
                "assigned_working_hours": 30
              }
            ]
          }
        ]
      }
    ]

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_workload_weekly.add_parser
   :prog: annoworkcli schedule list_workload_weekly
   :nosubcommands:
   :nodefaultconst:
