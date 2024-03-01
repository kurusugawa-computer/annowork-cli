import getpass
from typing import Optional

import annofabapi
from annofabapi import build as build_annofabapi
from annofabapi.exceptions import CredentialsNotFoundError
from annofabapi.exceptions import MfaEnabledUserExecutionError as AnnofabApiMfaEnabledUserExecutionError


def _get_annofab_user_id_from_stdin() -> str:
    """標準入力からAnnofabにログインする際のユーザーIDを取得します。"""
    login_user_id = ""
    while login_user_id == "":
        login_user_id = input("Enter Annofab User ID: ")
    return login_user_id


def _get_annofab_password_from_stdin() -> str:
    """標準入力からAnnofabにログインする際のパスワードを取得します。"""
    login_password = ""
    while login_password == "":
        login_password = getpass.getpass("Enter Annofab Password: ")
    return login_password


def build_annofabapi_resource_and_login(
    *,
    annofab_login_user_id: Optional[str] = None,
    annofab_login_password: Optional[str] = None,
    mfa_code: Optional[str] = None
) -> annofabapi.Resource:
    """
    annofabapi.Resourceインスタンスを生成したあと、ログインする。

    Args:
        args: コマンドライン引数の情報

    Returns:
        annofabapi.Resourceインスタンス

    """
    try:
        service = build_annofabapi(annofab_login_user_id, annofab_login_password)
    except CredentialsNotFoundError:
        # 環境変数, netrcフィアルに認証情報が設定されていなかったので、標準入力から認証情報を入力させる。
        stdin_login_user_id = _get_annofab_user_id_from_stdin()
        stdin_login_password = _get_annofab_password_from_stdin()
        service = build_annofabapi(stdin_login_user_id, stdin_login_password)

    try:
        if mfa_code is not None:
            service.api.login(mfa_code=mfa_code)
        else:
            service.api.login()
        return service

    except AnnofabApiMfaEnabledUserExecutionError:
        # 標準入力からMFAコードを入力させる
        inputted_mfa_code = ""
        while inputted_mfa_code == "":
            inputted_mfa_code = input("Enter MFA Code for Annofab: ")

        service.api.login(mfa_code=inputted_mfa_code)
        return service
