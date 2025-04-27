from cmdbox.app.auth.signin import Signin
from fastapi import Request, Response
from typing import Any, Dict
import requests
import urllib.parse


class GoogleSignin(Signin):
    @classmethod
    def get_email(cls, data:Any) -> str:
        user_info_resp = requests.get(
            url='https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {data}'}
        )
        user_info_resp.raise_for_status()
        user_info_json = user_info_resp.json()
        return user_info_json['email'] if 'email' in user_info_json else 'notfound'

    def request_access_token(self, conf:Dict, req:Request, res:Response) -> str:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        next = req.query_params['state']
        data = {'code': req.query_params['code'],
                'client_id': conf['client_id'],
                'client_secret': conf['client_secret'],
                'redirect_uri': conf['redirect_uri'],
                'grant_type': 'authorization_code'}
        query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
        # アクセストークン取得
        token_resp = requests.post(url='https://oauth2.googleapis.com/token', headers=headers, data=query)
        token_resp.raise_for_status()
        token_json = token_resp.json()
        return token_json['access_token']
