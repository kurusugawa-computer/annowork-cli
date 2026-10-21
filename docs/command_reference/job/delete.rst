===============================
job delete
===============================

Description
=================================
ジョブを削除します。
削除できるのはステータスが ``archived`` のジョブだけです。それ以外はスキップします。
必要に応じて :doc:`update_status` でアーカイブしてから実行してください。



Examples
=================================
以下のコマンドは、アーカイブ済みのジョブID ``job`` を削除します。


.. code-block:: 

    $ annoworkcli job delete --workspace_id org --job_id job 




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.job.delete_job.add_parser
   :prog: annoworkcli job delete
   :nosubcommands:
   :nodefaultconst: