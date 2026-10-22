=====================
job list
=====================

Description
=================================
ジョブの一覧を出力します。


Examples
=================================

出力形式と出力先の指定方法は :doc:`../../user_guide/cli_usage_output` を参照してください。


以下のコマンドは、ジョブの一覧を出力します。


.. code-block:: console

    $ annoworkcli job list --workspace_id org \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "job_id": "00c1133d-791d-4bf5-8412-b4e2aca3f53e",
         "job_name": "MOON",
         "job_tree": "org/d2fb9245-5fcb-432f-9c40-a8ecfc5f3d7c/00c1133d-791d-4bf5-8412-b4e2aca3f53e",
         "status": "unarchived",
         "target_hours": null,
         "workspace_id": "org",
         "note": "",
         "external_linkage_info": {
            "url": "https://annofab.com/projects/00c1133d-791d-4bf5-8412-b4e2aca3f53e"
         },
         "created_datetime": "2021-10-27T14:51:20.196Z",
         "updated_datetime": "2021-10-27T14:51:20.196Z",
         "parent_job_id": "d2fb9245-5fcb-432f-9c40-a8ecfc5f3d7c",
         "parent_job_name": "PLANET"
      }
   ]


同じ条件でCSV形式に出力する例です。

.. code-block:: console

    $ annoworkcli job list --workspace_id org \
     --format csv --output out.csv

.. csv-table:: out.csv
   :file: list/out.csv
   :header-rows: 1

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.job.list_job.add_parser
   :prog: annoworkcli job list
   :nosubcommands:
   :nodefaultconst:
