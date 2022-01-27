=========================================
annofab get_dashboard
=========================================

Description
=================================
ダッシュボードとなる情報（タスク数など）をJSON形式で出力します。



Examples
=================================



以下のコマンドは、ジョブID ``job`` の、2022-01-26時点のダッシュボード情報を出力します。
ダッシュボード情報の内容は以下の通りです。

* ``remaining_task_count`` : 残タスク
* ``result.cumulation`` : 累計の生産量、作業時間、生産性
* ``result.today`` : 今日の生産量、作業時間、生産性
* ``result.week`` : 直近7日間の生産量、作業時間、生産性


.. code-block:: 

    $ annoworkcli annofab get_dashboard --organization_id org --job_id job --date 2022-01-26 -o out/out.json


.. code-block:: json
   :caption: out.json

   {
      "job_ids": [
         "job"
      ],
      "annofab_project_id": "af_prj",
      "annofab_project_title": "af_prj",
      "date": "2022-01-26",
      "measurement_datetime": "2022-01-27T11:07:34.484+09:00",
      "remaining_task_count": {
         "complete": 0,
         "annotation_not_started": 0,
         "inspection_not_started": 0,
         "acceptance_not_started": 0,
         "on_hold": 0,
         "other": 0
      },
      "result": {
         "cumulation": {
            "actual_worktime": 441.1833333333334,
            "task_count": 0,
            "input_data_count": 0,
            "velocity_per_task": null,
            "velocity_per_input_data": null,
            "monitored_worktime": 0,
            "annotation_monitored_worktime": null,
            "inspection_monitored_worktime": null,
            "acceptance_monitored_worktime": null
         },
         "today": {
            "actual_worktime": 5.483333333333333,
            "task_count": 0,
            "input_data_count": 0,
            "velocity_per_task": null,
            "velocity_per_input_data": null,
            "monitored_worktime": 0,
            "annotation_monitored_worktime": 0,
            "inspection_monitored_worktime": 0,
            "acceptance_monitored_worktime": 0
         },
         "week": {
            "actual_worktime": 39.849999999999994,
            "task_count": 0,
            "input_data_count": 0,
            "velocity_per_task": null,
            "velocity_per_input_data": null,
            "monitored_worktime": 0,
            "annotation_monitored_worktime": 0,
            "inspection_monitored_worktime": 0,
            "acceptance_monitored_worktime": 0
         }
      }
   }


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.get_dashboard.add_parser
   :prog: annoworkcli annofab get_dashboard
   :nosubcommands:
   :nodefaultconst: