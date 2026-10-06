==========================================
Examples
==========================================

以下はインストール済みで、 :doc:`../user_guide/configurations` の認証情報が設定されている環境で実行する例です。
``YOUR_WORKSPACE_ID`` や ``YOUR_JOB_ID`` は実際のIDに置き換えてください。

ワークスペースとジョブを確認する
==========================================

所属するワークスペースを取得し、出力にある ``workspace_id`` を設定します。

.. code-block:: bash

    annoworkcli my list_workspace_member --format json
    export ANNOWORK_WORKSPACE_ID='YOUR_WORKSPACE_ID'
    annoworkcli job list --format json --output jobs.json
    annoworkcli workspace_member list --format json --output members.json

``jobs.json`` の ``job_id`` を使えば、特定のジョブを取得できます。

.. code-block:: bash

    annoworkcli job list --job_id YOUR_JOB_ID --format json

実績作業時間をCSVに出力する
==========================================

2026年1月の実績作業時間を、日付・メンバー・ジョブごとに日本標準時で集計します。

.. code-block:: bash

    annoworkcli actual_working_time list_daily --workspace_id YOUR_WORKSPACE_ID \
      --start_date 2026-01-01 --end_date 2026-01-31 --timezone_offset 9 \
      --format csv --output out/actual_working_hours.csv

出力には ``date`` 、 ``job_id`` 、 ``user_id`` 、 ``actual_working_hours`` などの列が含まれます。
``actual_working_hours`` の単位は時間です。
出力列と集計の詳細は :doc:`../command_reference/actual_working_time/list_daily` を参照してください。

予定と実績を結合した累積作業時間を出力する
==========================================

親ジョブ配下について、前日までの実績と当日以降の予定を結合します。
``YOUR_PARENT_JOB_ID`` は ``job list`` で取得した親ジョブのIDに置き換えてください。

.. code-block:: bash

    annoworkcli schedule_actual list_daily --workspace_id YOUR_WORKSPACE_ID \
      --parent_job_id YOUR_PARENT_JOB_ID --start_date 2026-01-01 --end_date 2026-01-31 \
      --timezone_offset 9 --format csv --output out/schedule_actual.csv

累積作業時間など、出力の指標は :doc:`../command_reference/schedule_actual/list_daily` を参照してください。

Annofabプロジェクトの情報とジョブを取得する
==================================================

Annoworkの認証情報に加えて、AnnofabのPATを設定します。
ジョブの外部連携情報にAnnofabプロジェクトのURLが設定されている必要があります。

.. code-block:: bash

    export ANNOFAB_PAT='YOUR_PERSONAL_ACCESS_TOKEN'
    annoworkcli annofab list_job --workspace_id YOUR_WORKSPACE_ID \
      --job_id YOUR_JOB_ID --format json --output out/annofab_jobs.json

対応するプロジェクト情報はJSONの ``annofab`` に出力されます。
ジョブにAnnofabプロジェクトのURLがない場合や、プロジェクトを取得できない場合は ``null`` になります。
設定や出力の詳細は :doc:`../command_reference/annofab/list_job` を参照してください。
