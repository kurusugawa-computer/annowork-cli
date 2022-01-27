=======================================
job change_status
=======================================

Description
=================================
ジョブのステータスを変更します。



Examples
=================================

以下のコマンドは、ジョブID ``job1`` , ``job2`` のステータスをアーカイブに変更します。


.. code-block:: 

    $ annoworkcli job change --organization_id org --job_id job --status archived




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.job.change_job_status.add_parser
   :prog: annoworkcli job change_status
   :nosubcommands:
   :nodefaultconst: