==========================================
Configurations
==========================================

Annoworkの認証情報
==========================================

ユーザーIDとパスワードを、次の優先順位で取得します。

1. コマンドライン引数
2. 環境変数 ``ANNOWORK_USER_ID`` と ``ANNOWORK_PASSWORD`` の組
3. ``.netrc`` ファイル
4. 対話入力

コマンドライン引数
------------------------------------------

共通オプションはサブコマンドの後に指定します。

.. code-block:: bash

    annoworkcli my get --annowork_user_id YOUR_USER_ID --annowork_password YOUR_PASSWORD

``--annowork_user_id`` のみ指定すると、パスワードの対話入力を求められます。
この場合は環境変数にパスワードがあっても対話入力になります。
``--annowork_password`` のみを指定するとエラーになります。

環境変数
------------------------------------------

.. code-block:: bash

    export ANNOWORK_USER_ID='YOUR_USER_ID'
    export ANNOWORK_PASSWORD='YOUR_PASSWORD'

両方が設定されている場合に使用されます。片方しかない場合は ``.netrc`` を探します。

.netrc ファイル
------------------------------------------

ホームディレクトリの ``.netrc`` に次の内容を記載します。
Linux/macOSでは ``$HOME/.netrc`` 、Windowsでは ``%USERPROFILE%\.netrc`` です。

.. code-block:: text
    :caption: .netrc

    machine annowork.com
    login YOUR_USER_ID
    password YOUR_PASSWORD

Linux/macOSではファイルの権限を設定します。

.. code-block:: bash

    chmod 600 ~/.netrc

対話入力と自動実行
------------------------------------------

認証情報が設定されていなければ、ユーザーIDとパスワードの入力を求められます。

.. code-block:: console

    $ annoworkcli my get
    Enter Annowork User ID: YOUR_USER_ID
    Enter Annowork Password:

AIやバッチから実行する場合は、実行環境に認証情報を設定してからコマンドを実行してください。
認証情報がない状態では対話入力が発生します。

ワークスペースID
==========================================

ワークスペースを必須とするコマンドでは、 ``--workspace_id`` が未指定の場合に環境変数 ``ANNOWORK_WORKSPACE_ID`` を使用します。
指定方法とIDの調べ方は :doc:`command_line_options` を参照してください。

Annofab連携の認証情報
==========================================

``annoworkcli annofab`` のうちAnnofab APIにアクセスするコマンドでは、Annoworkに加えてAnnofabの認証情報が必要です。
Annofabのアカウントと、対象プロジェクトなどへのアクセス権限を用意してください。

パーソナルアクセストークン（PAT）を環境変数で設定できます。
Annofabの画面での作成手順は `AnnofabのPAT作成手順 <https://annofab.readme.io/docs/profile-personal_access_token>`_ を参照してください。
発行済みのPATがあれば、以下の設定でCLIから利用できます。

.. code-block:: bash

    export ANNOFAB_PAT='YOUR_PERSONAL_ACCESS_TOKEN'
    annoworkcli annofab list_job --workspace_id YOUR_WORKSPACE_ID --format json

ユーザーIDとパスワードで認証する場合は、次の環境変数を両方設定します。

.. code-block:: bash

    export ANNOFAB_USER_ID='YOUR_ANNOFAB_USER_ID'
    export ANNOFAB_PASSWORD='YOUR_ANNOFAB_PASSWORD'

認証情報の優先順位は、コマンドライン引数、環境変数、 ``.netrc`` 、対話入力の順です。
コマンドラインでは ``--annofab_pat`` 、または ``--annofab_user_id`` と ``--annofab_password`` の組を指定できます。
``--annofab_pat`` が指定されていれば、引数のユーザーIDとパスワードより優先されます。
環境変数でも ``ANNOFAB_PAT`` がユーザーIDとパスワードより優先されます。
AnnofabのユーザーIDとパスワードの引数は両方指定してください。

``.netrc`` を使う場合は、Annoworkの設定と同じファイルに次の項目を追加します。

.. code-block:: text

    machine annofab.com
    login YOUR_ANNOFAB_USER_ID
    password YOUR_ANNOFAB_PASSWORD

ユーザーIDとパスワードによる認証では、多要素認証のコードの入力を求められる場合があります。
自動実行ではPATを設定してください。
ジョブやアカウントとAnnofabの対応付けについては :doc:`../command_reference/annofab/index` を参照してください。

AnnoworkのエンドポイントURL（開発者用）
==========================================

次の優先順位で設定されます。

1. コマンドライン引数 ``--endpoint_url``
2. 環境変数 ``ANNOWORK_ENDPOINT_URL``
3. 既定値 ``https://annowork.com``

.. code-block:: bash

    annoworkcli my get --endpoint_url http://localhost:8080

``.netrc`` の ``machine`` には、設定したURLのホスト名を指定してください。
``--endpoint_url`` はAnnoworkの接続先を指定するオプションです。
