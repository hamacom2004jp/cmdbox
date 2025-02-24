from cmdbox.app import common, edge, feature
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class EdgeConfig(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'edge'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'config'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_MEIGHT,
            discription_ja="端末モードの設定を行います。",
            discription_en="Set the edge mode.",
            choice=[
                dict(opt="endpoint", type="str", default="http://localhost:8081", required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントのURLを指定します。",
                     discription_en="Specify the URL of the endpoint."),
                dict(opt="icon_path", type="str", default=Path(self.ver.__file__).parent / 'web' / 'assets' / self.ver.__appid__ / 'favicon.ico',
                     required=False, multi=False, hide=False, choice=None,
                     discription_ja="アイコン画像のパスを指定します。",
                     discription_en="Specify the path to the icon image."),
                dict(opt="auth_type", type="str", default="idpw", required=False, multi=False, hide=False, choice=["noauth", "idpw", "apikey", "oauth2"],
                     discription_ja="エンドポイント接続じの認証方式を指定します。",
                     discription_en="Specifies the authentication method for endpoint connections.",
                     choice_show=dict(idpw=["user","password"],
                                      apikey=["apikey"],
                                      oauth2=["oauth2","oauth2_port","oauth2_client_id","oauth2_client_secret"]),),
                dict(opt="user", type="str", default="user", required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントへの接続ユーザーを指定します。",
                     discription_en="Specifies the user connecting to the endpoint."),
                dict(opt="password", type="str", default="password", required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントへの接続パスワードを指定します。",
                     discription_en="Specify the password for connecting to the endpoint."),
                dict(opt="apikey", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントへの接続するためのAPIKEYを指定します。",
                     discription_en="Specify the APIKEY to connect to the endpoint."),
                dict(opt="oauth2", type="str", default=None, required=False, multi=False, hide=False, choice=["", "google", "github"],
                     discription_ja="OAuth2認証を使用してエンドポイントに接続します。",
                     discription_en="Connect to the endpoint using OAuth2 authentication."),
                dict(opt="oauth2_port", type="int", default="8091", required=False, multi=False, hide=False, choice=None,
                     discription_ja="OAuth2認証を使用する場合のコールバックポートを指定します。省略した時は `8091` を使用します。",
                     discription_en="Specifies the callback port when OAuth2 authentication is used. If omitted, `8091` is used."),
                dict(opt="oauth2_client_id", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="OAuth2認証を使用するときのクライアントIDを指定します。",
                     discription_en="Specifies the client ID when OAuth2 authentication is used."),
                dict(opt="oauth2_client_secret", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="OAuth2認証を使用するときのクライアントシークレットを指定します。",
                     discription_en="Specifies the client secret when OAuth2 authentication is used."),
                dict(opt="oauth2_timeout", type="int", default="60", required=False, multi=False, hide=False, choice=None,
                     discription_ja="OAuth2認証が完了するまでのタイムアウト時間を指定します。",
                     discription_en="Specify the timeout period before OAuth2 authentication completes."),
                dict(opt="data", type="file", default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=True, choice=None,
                     discription_ja=f"省略した時は f`$HONE/.{self.ver.__appid__}` を使用します。",
                     discription_en=f"When omitted, f`$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="svcert_no_verify", type="bool", default=False, required=False, multi=False, hide=True, choice=[False, True],
                     discription_ja="HTTPSリクエストの時にサーバー証明書の検証を行いません。",
                     discription_en="Do not verify server certificates during HTTPS requests."),
                dict(opt="timeout", type="int", default="30", required=False, multi=False, hide=True, choice=None,
                     discription_ja="リクエストが完了するまでのタイムアウト時間を指定します。",
                     discription_en="Specifies the timeout period before the request completes."),
            ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.data is None:
            args.data = common.HOME_DIR / f".{self.ver.__appid__}"
        app = edge.Edge(logger, args.data, self.appcls, self.ver)
        msg = app.configure(self.get_mode(), self.get_cmd(), args, tm, pf)
        common.print_format(msg, True, tm, None, False, pf=pf)
        return 0, msg, None
