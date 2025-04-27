from cmdbox.app.auth.signin import Signin
from fastapi import Request, Response
from typing import Any, Dict
import requests
import urllib.parse


class GithubSignin(Signin):
    @classmethod
    def get_email(cls, data:Any) -> str:
        user_info_resp = requests.get(
            url='https://api.github.com/user/emails',
            headers={'Authorization': f'Bearer {data}'}
        )
        user_info_resp.raise_for_status()
        user_info_json = user_info_resp.json()
        if type(user_info_json) == list:
            email = 'notfound'
            for u in user_info_json:
                if u['primary']:
                    email = u['email']
                    break
            return email
        return 'notfound'

    def request_access_token(self, conf:Dict, req:Request, res:Response) -> str:
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'}
        data = {'code': req.query_params['code'],
                'client_id': conf['client_id'],
                'client_secret': conf['client_secret'],
                'redirect_uri': conf['redirect_uri']}
        query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
        # アクセストークン取得
        token_resp = requests.post(url='https://github.com/login/oauth/access_token', headers=headers, data=query)
        token_resp.raise_for_status()
        token_json = token_resp.json()
        return token_json['access_token']
