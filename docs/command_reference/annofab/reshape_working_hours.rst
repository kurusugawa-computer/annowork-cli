=========================================
annofab reshape_working_hours
=========================================

Description
=================================
AnnoWorkの実績作業時間とアサイン時間、Annofabの作業時間を比較できるようなCSVファイルに成形します。



Examples
=================================

以下のコマンドは、2022-01-01から2022-01-31までの期間で、AnnoWorkの実績作業時間とアサイン時間、AnnoFabの作業時間を、ユーザごとに比較したCSVを出力します。
出力結果詳細は後述を参照してください。

.. code-block:: 

    $ annoworkcli annofab reshape_working_hours --organization_id org --shape_type total_by_user \
     --start_date 2022-01-01 --end_date 2022-01-31 --output total_by_user.csv


``annoworkcli annofab list_working_hours`` コマンドと ``annoworkcli schedule list_daily`` コマンドの出力結果を用いて、``annoworkcli annofab reshape_working_hours`` コマンドを実行することもとできます。


.. code-block:: 

    $ annoworkcli annofab list_working_hours --organization_id org \
     --start_date 2022-01-01 --end_date 2022-01-31 --output actual.csv

    $ annoworkcli  schedule list_daily --organization_id org \
     --start_date 2022-01-01 --end_date 2022-01-31 --output assigned.csv

    $ annoworkcli annofab reshape_working_hours --organization_id org \ 
     --actual_file actual.csv --assigned_file assigned.csv --shape_type total_by_user --output total_by_user.csv



出力結果
=================================

列名
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
列名の内容は以下の通りです。


* assigned_working_hours : AnnoWorkのアサイン時間
* actual_working_hours : AnnoWorkの実績時間
* monitored_working_hours : AnnoFabの作業時間（AnnoFabのアノテーションエディタで計測された作業時間）
* activity_rate : アサイン時間に対する実績作業時間の比率（ ``= actual_working_hours / assigned_working_hours`` ）
* activity_diff : アサインに対する実績作業時間の差分（ ``= assigned_working_hours - actual_working_hours`` ）
* monitor_rate : 実績作業時間に対する計測作業時間の比率（ ``= monitored_working_hours / actual_working_hours`` ）
* monitor_diff : 実績作業時間に対する計測作業時間の差分（ ``= actual_working_hours - monitored_working_hours`` ）


``--shape_type details``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
日付ごとユーザごとに作業時間を集計したファイルです。
行方向に日付、列方向にユーザが並んでいます。


.. csv-table:: details.csv
   :file: reshape_working_hours/details.csv



total_by_user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ユーザごとに作業時間を集計します。


.. csv-table:: out.csv
   :header: user_id,username,company,assigned_working_hours,actual_working_hours,monitored_working_hours,activity_rate,activity_diff,monitor_rate,monitor_diff

    alice,Alice,U.S.,44.0,81.0,76.8,1.84,0.54,0.95,4.2
    bob,Bob,Japan,0.0,77.0,73.82,inf,0.0,0.96,3.18


total_by_job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ジョブごとに作業時間を集計します。 


.. csv-table:: out.csv
   :header: job_id,job_name,annofab_project_id,actual_working_hours,monitored_working_hours,monitor_rate,monitor_diff

    moon,MOON,af_moon,71.92,66.9,0.93,5.01
    mars,MARS,af_mars,190.32,176.76,0.93,13.55


total_by_parent_job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

親ジョブごとに作業時間を集計します。


.. csv-table:: out.csv
   :header: job_id,job_name,annofab_project_id,actual_working_hours,monitored_working_hours,monitor_rate,monitor_diff

    moon,MOON,af_moon,71.92,66.9,0.93,5.01
    mars,MARS,af_mars,190.32,176.76,0.93,13.55


total
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

作業時間を合計します。

.. csv-table:: out.csv
   :header: assigned_working_hours,actual_working_hours,monitored_working_hours,activity_rate,activity_diff,monitor_rate,monitor_diff

    3885.83,6722.83,8052.89,1.73,0.58,1.2,-1330.06





list_by_date_user_job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
作業時間の一覧を日付、ユーザ、ジョブ単位で出力します。

.. csv-table:: out.csv
   :header: date,user_id,username,job_id,job_name,annofab_project_id,actual_working_hours,monitored_working_hours,monitor_rate,monitor_diff,notes

    2021-01-01,alice,Alice,moon,MOON,af_moon,0.0,0.74,inf,-0.74,
    2021-01-01,bob,Bob,mars,MARS,af_mars,3.83,2.36,0.62,1.47,



list_by_date_user_parent_job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
作業時間の一覧を日付、ユーザ、親ジョブ単位で出力します。 --assigned_file は不要です。


.. csv-table:: out.csv
   :header: date,user_id,username,parent_job_id,parent_job_name,actual_working_hours,monitored_working_hours,monitor_rate,monitor_diff

    2021-01-01,alice,Alice,planet,PLANET,0.0,0.74,inf,-0.74
    2021-01-01,bob,Bob,planet,PLANET,3.83,2.36,0.62,1.47


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.reshape_working_hours.add_parser
   :prog: annoworkcli annofab reshape_working_hours
   :nosubcommands:
   :nodefaultconst: