from cmdbox.app.auth import signin
from fastapi import Request, Response
from typing import Any, Dict, Tuple, Union
from fastapi.responses import RedirectResponse
import requests
import copy
import logging


class AzureSigninProxy(signin.Signin):

    def _check_authheader(self, req:Request, res:Response, signin_file_data:Dict[str, Any], logger:logging.Logger) -> Union[None, RedirectResponse]:
        """
        認証ヘッダーをチェックする

        Args:
            req (Request): リクエスト
            res (Response): レスポンス
            signin_file_data (Dict[str, Any]): サインインファイルデータ（変更不可）
            logger (logging.Logger): ロガー

        Returns:
            Union[None, RedirectResponse]: サインインエラーの場合はリダイレクトレスポンス
        """
        signin.Signin._enable_cors(req, res)
        if signin_file_data is None:
            res.headers['signin'] = 'success'
            return None

        if 'Authorization' not in req.headers:
            return RedirectResponse(url=f'/signin{req.url.path}?error=noauth')
        id_token = req.headers.get('X-MS-TOKEN-AAD-ID-TOKEN', None)
        access_token = req.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN', None)
        expires_on = req.headers.get('X-MS-TOKEN-AAD-EXPIRES-ON', None)
        refresh_token = req.headers.get('X-MS-TOKEN-AAD-REFRESH-TOKEN', None)
        if access_token is None:
            return RedirectResponse(url=f'/signin{req.url.path}?error=invalid')

        # ユーザー情報取得
        user_info_resp = requests.get(
            url='https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if not user_info_resp.ok and user_info_resp.text:
            return RedirectResponse(url=f'/signin{req.url.path}?error=notfound')
        user_info_resp.raise_for_status()
        user_info_json = user_info_resp.json()
        if not isinstance(user_info_json, dict):
            return RedirectResponse(url=f'/signin{req.url.path}?error=invalid')
        uid = user_info_json.get('id', None)
        email = user_info_json.get('mail', None)
        name = user_info_json.get('displayName', None)
        name = email.split('@')[0] if not name and email and '@' in email else 'unknown'
        if uid is None:
            return RedirectResponse(url=f'/signin{req.url.path}?error=notfound')

        # グループ情報取得
        groups_info_resp = requests.get(
            url='https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$Top=999',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if not groups_info_resp.ok and groups_info_resp.text:
            return RedirectResponse(url=f'/signin{req.url.path}?error=notfound')
        groups_info_resp.raise_for_status()
        groups_info_json = groups_info_resp.json()
        if not isinstance(groups_info_json, dict) or not isinstance(groups_info_json.get('value'), list):
            return RedirectResponse(url=f'/signin{req.url.path}?error=invalid')
        gids = [row['id'] for row in groups_info_json.get('value', [])]
        copy_signin_data = copy.deepcopy(self.signin_file_data)
        groups = [g for g in copy_signin_data['groups'] if g['gid'] in gids]
        group_names = [g["name"] for g in groups]
        group_homes = [g["home"] for g in groups]
        user = dict(uid=uid, name=name, home=f'.users/{name}', password='', email=email,
                    gids=gids, groups=group_names, group_homes=group_homes, apikey=access_token,
                    id_token=id_token, access_token=access_token, expires_on=expires_on, refresh_token=refresh_token)
        req.session['signin'] = user
        req.session['apikeys'] = [access_token]
        if logger.level == logging.DEBUG:
            logger.debug(f"find user: name={user['name']}, group_names={group_names}")
        # パスルールチェック
        return signin.Signin._check_path(req, res, user, signin_file_data, logger)

