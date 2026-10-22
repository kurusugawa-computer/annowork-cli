=========================================
schedule list_workload_daily_by_user
=========================================

Description
=================================
全体の日別集計は :doc:`list_workload_daily` を使ってください。

日付・メンバーごとに、予定稼働時間と全親ジョブのアサイン時間を比較し、内訳とともに出力します。
予定稼働時間が登録されていれば、未アサインのメンバーも出力します。
0時間の登録も含みます。予定稼働時間の登録もアサインもない日・メンバーの行は出力しません。
開始日・終了日を含み、日付・``workspace_member_id`` 順に出力します。
開始日が終了日より後の場合はエラーです。

``remaining_working_hours`` は予定稼働時間からアサイン合計を引いた値です。
負数は超過を表します。合計すると差し引きの余力になるため、追加アサイン可能な時間だけを
集計する場合は正数の行を合計してください。

``assignments`` は親ジョブごとのアサイン時間の内訳です。同じ親ジョブの複数のスケジュールは合算します。
JSON出力では配列として出力し、未アサインの場合は空配列です。
CSVは日付・メンバーごとに1行で、ユーザー情報・時間・``status`` の後ろに親ジョブ名の列を追加します。
親ジョブ列の並び順、未アサイン時の0、計算不能時の空欄、列名の検証は
:doc:`list_workload_daily` のCSV形式と同じです。対象はユーザー・状態の絞り込み後の行に含まれる親ジョブです。
0件の場合も固定列のヘッダーを出力します。

割合指定のスケジュールは当日の予定稼働時間から換算します。
予定稼働時間が未登録の場合は ``expected_working_hours`` と ``remaining_working_hours`` を
JSONでは ``null``、CSVでは空欄にします。割合指定が含まれる場合は、該当する親ジョブの
アサイン時間とアサイン合計も不明とします。

``status`` は次の値です。``--status`` で複数指定して絞り込めます。

* ``overloaded``: 予定稼働時間を超過
* ``under_assigned``: 一部アサイン済みで空きあり
* ``unassigned``: 予定稼働時間が正でアサイン時間が0
* ``full``: 予定稼働時間とアサイン時間が一致
* ``unknown``: 予定稼働時間またはアサイン時間が不明で判定不能

CLIの共通引数（``--workspace_id``、``--start_date``、``--end_date``、``--format``、``--output``）は
:doc:`list_workload_daily` と同じです。このコマンドでは追加で ``--user_id`` と ``--status`` による絞り込みができます。
``--user_id`` は複数指定でき、省略時は全ユーザーを対象にします。

Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

.. code-block:: console

    $ annoworkcli schedule list_workload_daily_by_user --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-30 --format json --output workload.json

.. code-block:: json
   :caption: workload.json

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


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli schedule list_workload_daily_by_user --workspace_id org \
      --start_date 2026-11-01 --end_date 2026-11-30 --format csv --output out.csv

.. csv-table:: out.csv
   :file: list_workload_daily_by_user/out.csv
   :header-rows: 1

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
