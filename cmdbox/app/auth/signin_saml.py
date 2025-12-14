from cmdbox.app.auth.signin import Signin
from fastapi import Request, Response
from typing import Any, Dict, Tuple
import copy
import logging


class SigninSAML(Signin):

    def jadge(self, email:str) -> Tuple[bool, Dict[str, Any]]:
        """
        サインインを成功させるかどうかを判定します。
        返すユーザーデータには、uid, name, email, groups, hash が必要です。

        Args:
            email (str): メールアドレス

        Returns:
            Tuple[bool, Dict[str, Any]]: (成功かどうか, ユーザーデータ)
        """
        copy_signin_data = copy.deepcopy(self.signin_file_data)
        users = [u for u in copy_signin_data['users'] if u['email'] == email and u['hash'] == 'saml']
        return len(users) > 0, users[0] if len(users) > 0 else None

    async def make_saml(self, prov:str, next:str, form_data:Dict[str, Any], req:Request, res:Response) -> Any:
        """
        SAML認証のリダイレクトURLを取得する
        Args:
            prov (str): プロバイダ名
            next (str): リダイレクト先のURL
            req (Request): リクエスト
            res (Response): レスポンス
        Returns:
            OneLogin_Saml2_Auth: SAML認証オブジェクト
        """
        sd = self.signin_file_data
        saml_settings = dict(
            strict=False,
            debug=self.logger.level==logging.DEBUG,
            idp=sd['saml']['providers'][prov]['idp'],
            sp=sd['saml']['providers'][prov]['sp'])
        # SAML認証のリダイレクトURLを取得
        request_data = dict(
            https='on' if req.url.scheme=='https' else 'off',
            http_host=req.client.host,
            server_port=req.url.port,
            script_name=f'{req.url.path}?next={next}',
            post_data=dict(),
            get_data=dict(),
        )
        if (req.query_params):
            request_data["get_data"] = req.query_params,
        if "SAMLResponse" in form_data:
            SAMLResponse = form_data["SAMLResponse"]
            request_data["post_data"]["SAMLResponse"] = SAMLResponse
        if "RelayState" in form_data:
            RelayState = form_data["RelayState"]
            request_data["post_data"]["RelayState"] = RelayState
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
        auth = OneLogin_Saml2_Auth(request_data=request_data, old_settings=saml_settings)
        return auth
