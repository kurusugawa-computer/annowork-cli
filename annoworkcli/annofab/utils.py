from typing import Optional

import annofabapi
from annofabapi import build as build_annofabapi
from annofabapi.exceptions import MfaEnabledUserExecutionError as AnnofabApiMfaEnabledUserExecutionError


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

    service = build_annofabapi(annofab_login_user_id, annofab_login_password)

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
