from cmdbox.app.auth.signin_saml import SigninSAML
from typing import Any


class AzyreSigninSAML(SigninSAML):
    @classmethod
    def get_email(cls, data:Any) -> str:
        user_info_json = data.get_attributes()
        if isinstance(user_info_json, dict):
            email = user_info_json.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', ['notfound'])
            return email[0] if len(email) > 0 else 'notfound'
        return 'notfound'
