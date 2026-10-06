=========================================
completion
=========================================

シェル補完スクリプトを標準出力に出力します。認証やWeb APIへのアクセスは不要で、ログも出力しません。
対応するシェルと設定方法は :ref:`shell-completion` を参照してください。

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.completion.subcommand_completion.add_parser
   :prog: annoworkcli completion
   :nosubcommands:
   :nodefaultconst:
