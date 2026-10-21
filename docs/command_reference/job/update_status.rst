=======================================
job update_status
=======================================

Description
=================================
ジョブのステータスを変更します。



Examples
=================================

以下のコマンドは、ジョブID ``job1`` , ``job2`` のステータスをアーカイブに変更します。


.. code-block:: 

    $ annoworkcli job update_status --workspace_id org --job_id job1 job2 --status archived




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.job.update_job_status.add_parser
   :prog: annoworkcli job update_status
   :nosubcommands:
   :nodefaultconst: