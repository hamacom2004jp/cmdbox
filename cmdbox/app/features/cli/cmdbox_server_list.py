from cmdbox.app import common, feature, server
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic


class ServerList(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'server'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'list'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
            description_ja="起動中のサーバーの一覧を表示します。クライアント環境からの利用も可能です。",
            description_en="Displays a list of running inference servers. Can also be used from the client environment.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
            ]
        )

    @validator.apprun_check
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
        sv = server.Server(Path(args.data), logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname='server') # list取得なのでデフォルトのsvnameを指定
        ret = sv.list_server()
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, sv
        return self.RESP_SUCCESS, ret, sv

    def output_schema(self) -> type:
        class ServerRecord(resdata.Base):
            svname: Union[str, None] = pydantic.Field(default=None, description="サーバー名")
            status: Union[str, None] = pydantic.Field(default=None, description="ステータス")
            ctime: Union[str, None] = pydantic.Field(default=None, description="作成日時")
            receive_cnt: Union[int, None] = pydantic.Field(default=None, description="受信件数")
            success_cnt: Union[int, None] = pydantic.Field(default=None, description="成功件数")
            warn_cnt: Union[int, None] = pydantic.Field(default=None, description="警告件数")
            error_cnt: Union[int, None] = pydantic.Field(default=None, description="エラー件数")
        class Data(resdata.Data):
            data: Union[List[ServerRecord], None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
