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





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.reshape_working_hours.add_parser
   :prog: annoworkcli annofab reshape_working_hours
   :nosubcommands:
   :nodefaultconst: