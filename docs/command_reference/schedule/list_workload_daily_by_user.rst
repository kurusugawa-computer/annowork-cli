=========================================
schedule list_workload_daily_by_user
=========================================

Description
=================================
旧 ``schedule list_workload_daily`` の日付・ユーザー単位の出力を引き継ぐコマンドです。
全体の日別集計は :doc:`list_workload_daily` を使ってください。

日付・メンバーごとに、予定稼働時間と全親ジョブのアサイン時間を比較し、内訳とともに出力します。
予定稼働時間が登録されていれば、未アサインのメンバーも出力します。
予定稼働時間が0でアサインもない日は省略します。

``remaining_working_hours`` は予定稼働時間からアサイン合計を引いた値です。
負数は超過を表します。合計すると差し引きの余力になるため、追加アサイン可能な時間だけを
集計する場合は正数の行を合計してください。

``assignments`` は親ジョブごとのアサイン時間の内訳です。同じ親ジョブの複数のスケジュールは合算します。
JSON出力では配列、CSV出力では配列をJSON文字列にしたセルとして出力します。
未アサインの場合は空配列です。CSVは日付・メンバーごとに1行なので、時間列を合計できます。

割合指定のスケジュールは当日の予定稼働時間から換算します。
予定稼働時間が未登録の場合は ``expected_working_hours`` と ``remaining_working_hours`` を
JSONでは ``null``、CSVでは空欄にします。割合指定が含まれる場合は、該当する親ジョブの
アサイン時間とアサイン合計も不明とします。

``status`` は次の値です。``--status`` で複数指定して絞り込めます。

* ``overloaded``: 予定稼働時間を超過
* ``under_assigned``: 一部アサイン済みで空きあり
* ``unassigned``: 予定稼働時間が正でアサイン時間が0
* ``full``: 予定稼働時間とアサイン時間が一致
* ``unknown``: 予定稼働時間が未登録で判定不能

Examples
=================================

.. code-block:: console

    $ annoworkcli schedule list_workload_daily_by_user --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-30 --format json --output workload.json

.. code-block:: json

    [
      {
        "date": "2026-11-02",
        "workspace_member_id": "member1",
        "user_id": "alice",
        "username": "Alice",
        "expected_working_hours": 6,
        "assigned_working_hours": 8,
        "remaining_working_hours": -2,
        "status": "overloaded",
        "assignments": [
          {"parent_job_id": "job-a", "parent_job_name": "ジョブA", "assigned_working_hours": 8}
        ]
      }
    ]

空きがあるメンバーだけCSVに出力する例です。

.. code-block:: console

    $ annoworkcli schedule list_workload_daily_by_user --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-30 \
      --status unassigned under_assigned --output workload.csv

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_workload_daily_by_user.add_parser
   :prog: annoworkcli schedule list_workload_daily_by_user
   :nosubcommands:
   :nodefaultconst:
