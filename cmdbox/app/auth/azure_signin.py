from cmdbox.app.auth.signin import Signin
from fastapi import Request, Response
from typing import Any, Dict, Tuple
import requests
import urllib
import copy


class AzureSignin(Signin):
    @classmethod
    def get_email(cls, data:Any) -> str:
        user_info_resp = requests.get(
            url='https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {data}'}
        )
        if not user_info_resp.ok and user_info_resp.text:
            raise requests.exceptions.HTTPError(user_info_resp.text, response=user_info_resp)
        user_info_resp.raise_for_status()
        user_info_json = user_info_resp.json()
        if isinstance(user_info_json, dict):
            email = user_info_json.get('mail', 'notfound')
            return email
        return 'notfound'

    def jadge(self, data:Any, email:str) -> Tuple[bool, Dict[str, Any]]:
        """
        サインインを成功させるかどうかを判定します。
        返すユーザーデータには、uid, name, email, groups, hash が必要です。

        Args:
            data (str): アクセストークン又は属性データ
            email (str): メールアドレス

        Returns:
            Tuple[bool, Dict[str, Any]]: (成功かどうか, ユーザーデータ)
        """
        user_info_resp = requests.get(
            url='https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {data}'}
        )
        if not user_info_resp.ok and user_info_resp.text:
            raise requests.exceptions.HTTPError(user_info_resp.text, response=user_info_resp)
        user_info_resp.raise_for_status()
        user = user_info_resp.json()

        groups_info_resp = requests.get(
            url='https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$Top=999',
            headers={'Authorization': f'Bearer {data}'}
        )
        if not groups_info_resp.ok and groups_info_resp.text:
            raise requests.exceptions.HTTPError(groups_info_resp.text, response=groups_info_resp)
        groups_info_resp.raise_for_status()
        groups_info_json = groups_info_resp.json()
        if isinstance(groups_info_json, dict) and isinstance(groups_info_json.get('value'), list):
            gids = [row['id'] for row in groups_info_json.get('value', [])]
            copy_signin_data = copy.deepcopy(self.signin_file_data)
            groups = [g for g in copy_signin_data['groups'] if g['gid'] in gids]
            group_names = [g["name"] for g in groups]
            group_homes = [g["home"] for g in groups]
            name = email.split('@')[0] if email and '@' in email else user['displayName']
            user = dict(uid=user['id'], name=name, home=f'.users/{name}', password='',
                        gids=gids, groups=group_names, group_homes=group_homes, email=email)
            return len(groups) > 0, user
        return False, None

    def request_access_token(self, conf:Dict, req:Request, res:Response) -> str:
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'}
        data = {'tenant': conf['tenant_id'],
                'code': req.query_params['code'],
                'scope': " ".join(conf['scope']),
                'client_id': conf['client_id'],
                'client_secret': conf['client_secret'],
                'redirect_uri': conf['redirect_uri'],
                'grant_type': 'authorization_code'}
        query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
        # アクセストークン取得
        token_resp = requests.post(url=f'https://login.microsoftonline.com/{conf["tenant_id"]}/oauth2/v2.0/token', headers=headers, data=query)
        if not token_resp.ok and token_resp.text:
            raise requests.exceptions.HTTPError(token_resp.text, response=token_resp)
        token_resp.raise_for_status()
        token_json = token_resp.json()
        return token_json['access_token']
