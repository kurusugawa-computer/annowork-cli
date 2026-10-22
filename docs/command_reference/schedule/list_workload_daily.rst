=========================================
schedule list_workload_daily
=========================================

Description
=================================
取得期間の指定・省略時の動作は :ref:`schedule-list-date-range` を参照してください。

全ユーザーを対象に、日ごとの予定稼働時間と親ジョブ別のアサイン時間を比較します。
指定期間の全日を日付順に出力します。開始日・終了日を含みます。
終了日を省略した場合は、対象期間内の作業計画・予定稼働時間の最終日までを出力します。
対象データがなければ、JSONは空配列、CSVはヘッダー行だけを出力します。


共通の集計値
---------------------------------

* ``expected_working_hours``: 未アサインのユーザーも含む、登録済みの予定稼働時間の合計。
* ``assigned_working_hours``: 全親ジョブへのアサイン時間の合計。
* ``remaining_working_hours``: 予定稼働時間の合計からアサイン合計を引いた値。超過時は負数。

全体の差分は、個人の超過と余裕を相殺した値です。
予定稼働時間の未登録は補完せず、登録済みの値だけを全体の予定稼働時間に含めます。
割合指定のアサインは各ユーザーの当日の予定稼働時間から換算します。
未登録で換算できない場合は、そのアサイン時間と、それを含むユーザー別・親ジョブ別・日別の
アサイン合計を不明とします。不明なアサイン合計から計算する差分も不明です。

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。

CSV形式
---------------------------------

1日1行で、共通の集計値の後ろに親ジョブ名の列を追加します。
各親ジョブ列の値は、その日のアサイン時間です。
指定期間にアサインがある親ジョブを、``parent_job_id`` 順に並べます。
アサインがない日は0、計算不能な値は空欄です。
予定・アサインのない日も出力します。親ジョブがなければ固定の4列だけを出力します。

集計はIDごとに行い、列名だけに親ジョブ名を使います。
別IDのジョブ名が重複する場合、固定列名と衝突する場合、ジョブ名が未取得または空の場合は
エラーにします。この場合は ``--format json`` を使ってください。
ユーザー別内訳はCSVには含めません。

.. code-block:: console

    $ annoworkcli schedule list_workload_daily --workspace_id org \
      --start_date 2026-11-02 --end_date 2026-11-02 --format csv --output workload.csv

.. csv-table:: workload.csv
   :file: list_workload_daily/workload.csv
   :header-rows: 1

JSON形式
---------------------------------

1日1オブジェクトの配列です。全体の集計値に加えて、次の内訳を常に出力します。

* ``members``: ユーザー情報と、その日の予定稼働時間・アサイン合計・差分・``status``。
  その日に予定稼働時間の登録またはアサインがあるユーザーを含めます。0時間の登録も含みます。
* ``assignments``: 親ジョブごとのアサイン合計と、``members`` による担当者別の内訳。
  担当者別の時間は、その親ジョブへのアサイン時間です。

ユーザー情報は、どちらの ``members`` にも ``workspace_member_id``、``user_id``、``username`` を持たせます。
メンバーは ``workspace_member_id`` 順、親ジョブは ``parent_job_id`` 順に並べます。
個人の予定稼働時間が未登録の場合、その予定稼働時間と差分は ``null`` です。
計算不能なアサイン時間と、それを含む合計・差分も ``null`` です。
削除済みなどで取得できないユーザー情報・親ジョブ名も ``null`` です。
データがない日は各合計を0、``members`` と ``assignments`` を空配列にします。
個人の ``status`` の意味は :doc:`list_workload_daily_by_user` を参照してください。

.. code-block:: console

    $ annoworkcli schedule list_workload_daily --workspace_id org \
      --start_date 2026-11-02 --end_date 2026-11-02 --format json --output workload.json

.. code-block:: json
   :caption: workload.json

    [
      {
        "date": "2026-11-02",
        "expected_working_hours": 16,
        "assigned_working_hours": 9,
        "remaining_working_hours": 7,
        "members": [
          {
            "workspace_member_id": "member-1",
            "user_id": "alice",
            "username": "Alice",
            "expected_working_hours": 8,
            "assigned_working_hours": 9,
            "remaining_working_hours": -1,
            "status": "overloaded"
          },
          {
            "workspace_member_id": "member-2",
            "user_id": "bob",
            "username": "Bob",
            "expected_working_hours": 8,
            "assigned_working_hours": 0,
            "remaining_working_hours": 8,
            "status": "unassigned"
          }
        ],
        "assignments": [
          {
            "parent_job_id": "job-a",
            "parent_job_name": "ジョブA",
            "assigned_working_hours": 9,
            "members": [
              {
                "workspace_member_id": "member-1",
                "user_id": "alice",
                "username": "Alice",
                "assigned_working_hours": 9
              }
            ]
          }
        ]
      }
    ]

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_workload_daily.add_parser
   :prog: annoworkcli schedule list_workload_daily
   :nosubcommands:
   :nodefaultconst:
