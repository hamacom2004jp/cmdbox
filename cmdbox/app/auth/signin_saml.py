from cmdbox.app.auth.signin import Signin
from typing import Any, Dict, Tuple
import copy


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
