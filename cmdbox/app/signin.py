from typing import Dict, Any, Tuple, List, Union


class Signin(object):

    def __init__(self, appcls, ver):
        self.ver = ver
        self.appcls = appcls

    def jadge(self, access_token:str, email:str, signin_file_data:Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        サインインを成功させるかどうかを判定します。
        返すユーザーデータには、uid, name, email, groups, hash が必要です。

        Args:
            access_token (str): アクセストークン
            email (str): メールアドレス
            signin_file_data (Dict[str, Any]): サインインファイルデータ（変更不可）

        Returns:
            Tuple[bool, Dict[str, Any]]: (成功かどうか, ユーザーデータ)
        """
        users = [u for u in signin_file_data['users'] if u['email'] == email and u['hash'] == 'oauth2']
        return len(users) > 0, users[0] if len(users) > 0 else None

    def get_groups(self, access_token:str, user:Dict[str, Any], signin_file_data:Dict[str, Any]) -> Tuple[List[str], List[int]]:
        """
        ユーザーのグループを取得します

        Args:
            access_token (str): アクセストークン
            user (Dict[str, Any]): ユーザーデータ
            signin_file_data (Dict[str, Any]): サインインファイルデータ（変更不可）

        Returns:
            Tuple[List[str], List[int]]: (グループ名, グループID)
        """
        group_names = list(set(self.correct_group(user['groups'], None, signin_file_data)))
        gids = [g['gid'] for g in signin_file_data['groups'] if g['name'] in group_names]
        return group_names, gids

    def correct_group(self, group_names:List[str], master_groups:List[Dict[str, Any]], signin_file_data:Dict[str, Any]):
        """
        指定されたグループ名に属する子グループ名を収集します

        Args:
            group_names (List[str]): グループ名リスト
            master_groups (List[Dict[str, Any]], optional): 親グループ名. Defaults to None.
            signin_file_data (Dict[str, Any]): サインインファイルデータ（変更不可）
        """
        master_groups = signin_file_data['groups'] if master_groups is None else master_groups
        gns = []
        for gn in group_names.copy():
            gns = [gr['name'] for gr in master_groups if 'parent' in gr and gr['parent']==gn]
            gns += self.correct_group(gns, master_groups, signin_file_data)
        return group_names + gns
