from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic
import requests


class A2asvReload(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "a2asv"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return "reload"

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="A2A サーバーのエージェントを再読み込みします。",
            description_en="Reload agents on the A2A server.",
            choice=[
                dict(opt="a2asv_reload_url", type=Options.T_STR, default="http://localhost:8071/a2a_reload", required=True, multi=False, hide=False, choice=None,
                     description_ja="A2A Serverの再読み込みURLを指定します。例: http://localhost:8071/a2a_reload",
                     description_en="Specify the base URL of the A2A server. e.g. http://localhost:8071/a2a_reload"),
                dict(opt="a2asv_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="A2A ServerのAPI Keyを指定します。",
                     description_en="Specify the API Key of the A2A server."),
                dict(opt="send_method", type=Options.T_STR, default="POST", required=True, multi=False, hide=False, choice=["GET", "POST"],
                     description_ja="`/a2a_reload` に送信するHTTPメソッドを指定します。",
                     description_en="Specify the HTTP method to send to `/a2a_reload`."),
                dict(opt="send_verify", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[False, True],
                     description_ja="HTTPS証明書の検証を有効化するかどうかを指定します。",
                     description_en="Specify whether to enable HTTPS certificate verification."),
                dict(opt="send_timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="A2Aサーバーの応答待ちタイムアウト秒数を指定します。",
                     description_en="Specify timeout seconds waiting for A2A server response."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float,
               pf:List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        url = str(args.a2asv_reload_url).rstrip("/")
        headers = {}
        if getattr(args, "a2asv_apikey", None):
            headers["Authorization"] = f"Bearer {args.a2asv_apikey}"
        try:
            res = requests.request(method=args.send_method, url=url, headers=headers,
                                   verify=args.send_verify, timeout=args.send_timeout)
        except Exception as e:
            msg = dict(warn=f"Failed request to A2A server. {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        content_type = (res.headers.get("Content-Type") or "").lower()
        body:Any
        if content_type.startswith("application/json"):
            try:
                body = res.json()
            except ValueError:
                body = res.text
        else:
            body = res.text

        if res.status_code != 200:
            msg = dict(warn=dict(status_code=res.status_code, url=url, body=body))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        msg = dict(success=dict(status_code=res.status_code, url=url, data=body))
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS, msg, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            status_code: Union[int, None] = pydantic.Field(default=None, description="HTTPステータスコード")
            url: Union[str, None] = pydantic.Field(default=None, description="呼び出したURL")
            data: Union[Dict[str, Any], str, None] = pydantic.Field(default=None, description="レスポンスデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
