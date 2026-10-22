============================================================
schedule list_workload_weekly_by_user
============================================================

Description
=================================

取得期間の指定・省略時の動作は :ref:`planned-list-date-range` を参照してください。

週・ユーザーごとに、予定稼働時間とアサイン時間を比較し、親ジョブ別の内訳を出力します。
全体の週別集計は :doc:`list_workload_weekly` を使ってください。

週の区切り、指定期間の端の扱い、時間の合計方法は :doc:`list_workload_weekly` と同じです。
予定稼働時間の登録またはアサインがある週・メンバーだけを出力します。0時間の登録も含みます。
週の開始日・``workspace_member_id`` 順に出力します。
JSONは1週・メンバーにつき1オブジェクト、CSVは1週・メンバーにつき1行です。
JSONのユーザー情報・親ジョブ別内訳とCSVの親ジョブ列の仕様は
:doc:`list_workload_daily_by_user` と同じです。ただし ``date`` は ``start_date`` と ``end_date`` に置き換わります。
親ジョブ名は週次版のCSV固定列名との衝突も検証します。
対象データがなければ、JSONは空配列、CSVは固定列のヘッダーだけを出力します。

共通引数は :doc:`list_workload_weekly` と同じです。
``--user_id`` による絞り込みは :doc:`list_workload_daily_by_user` を参照してください。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

.. code-block:: console

    $ annoworkcli schedule list_workload_weekly_by_user --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-07 --format csv --output workload.csv

.. csv-table:: workload.csv
   :file: list_workload_weekly_by_user/workload.csv
   :header-rows: 1

.. code-block:: console

    $ annoworkcli schedule list_workload_weekly_by_user --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-07 --format json --output workload.json

.. code-block:: json
   :caption: workload.json

    [
      {
        "start_date": "2026-11-01",
        "end_date": "2026-11-07",
        "workspace_member_id": "member-1",
        "user_id": "alice",
        "username": "Alice",
        "expected_working_hours": 40,
        "assigned_working_hours": 30,
        "remaining_working_hours": 10,
        "assignments": [
          {
            "parent_job_id": "job-a",
            "parent_job_name": "ジョブA",
            "assigned_working_hours": 30
          }
        ]
      }
    ]

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_workload_weekly_by_user.add_parser
   :prog: annoworkcli schedule list_workload_weekly_by_user
   :nosubcommands:
   :nodefaultconst:
