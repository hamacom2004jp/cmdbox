from cmdbox.app.auth.signin import Signin
from fastapi import Request, Response
from typing import Any, Dict
import requests
import urllib


class AzureSignin(Signin):
    @classmethod
    def get_email(cls, data:Any) -> str:
        user_info_resp = requests.get(
            url='https://graph.microsoft.com/v1.0/me',
            #url='https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$Top=999',
            headers={'Authorization': f'Bearer {data}'}
        )
        user_info_resp.raise_for_status()
        user_info_json = user_info_resp.json()
        if isinstance(user_info_json, dict):
            email = user_info_json.get('mail', 'notfound')
            return email
        return 'notfound'
    
    def request_access_token(self, conf:Dict, req:Request, res:Response) -> str:
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'}
        data = {'tenant': conf['tenant_id'],
                'code': req.query_params['code'],
                'scope': " ".join(conf['scope']),
                'client_id': conf['client_id'],
                #'client_secret': conf['client_secret'],
                'redirect_uri': conf['redirect_uri'],
                'grant_type': 'authorization_code'}
        query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
        # アクセストークン取得
        token_resp = requests.post(url=f'https://login.microsoftonline.com/{conf["tenant_id"]}/oauth2/v2.0/token', headers=headers, data=query)
        token_resp.raise_for_status()
        token_json = token_resp.json()
        return token_json['access_token']
