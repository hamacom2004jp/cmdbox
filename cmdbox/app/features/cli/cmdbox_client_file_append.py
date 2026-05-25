from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class ClientFileAppend(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'client'

    def get_cmd(self):
        return 'file_append'

    def get_option(self):
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="データフォルダ配下のテキストファイルにコンテンツを追記します。",
            description_en="Append content to a text file under the data folder.",
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
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="svpath", type=Options.T_FILE, default="/", required=True, multi=False, hide=False, choice=None,
                     description_ja="追記先ファイルのパスをデータフォルダ以下で指定します。",
                     description_en="Specify the path of the file to append to, relative to the data folder.",
                     test_true={"server":"/file_server/append.txt",
                                "client":"/file_client/append.txt",
                                "current":"/file_current/append.txt"}),
                dict(opt="fwpath", type=Options.T_FILE, default=None, required=True, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。",
                     description_en="Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."),
                dict(opt="rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="content", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="ファイルに追記するテキスト内容を指定します。",
                     description_en="Specify the text content to append to the file.",
                     test_true={"server":"appended content\n", "client":"appended content\n", "current":"appended content\n"}),
                dict(opt="encoding", type=Options.T_STR, default="utf-8", required=False, multi=False, hide=False, choice=None,
                     description_ja="テキストファイルの文字コードを指定します。省略時は `utf-8` を使用します。",
                     description_en="Specify the character encoding of the text file. If omitted, `utf-8` is used."),
                dict(opt="mkdir", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="中間フォルダがない場合作成します。",
                     description_en="If there is no in between folder, create one.",
                     test_true={"server":True, "client":True, "current":True}),
                dict(opt="scope", type=Options.T_STR, default="client", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="参照先スコープを指定します。`client` , `current` , `server` のいずれかです。",
                     description_en="Specifies the scope to be referenced. One of `client`, `current`, or `server`.",
                     choice_show=dict(client=["client_data"]),
                     test_true={"server":"server", "client":"client", "current":"current"}),
                dict(opt="client_data", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                     description_en="Specify the path of the data folder when local is referenced.",
                     test_true={"server":None,
                                "client":common.HOME_DIR / f".{self.ver.__appid__}",
                                "current":None}),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
            ]
        )

    def get_svcmd(self):
        return 'file_append'

    @validator.apprun_check
    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
        fwpaths = [p.replace('"','') for p in args.fwpath] if args.fwpath is not None else ["/"]
        rjpaths = [p.replace('"','') for p in args.rjpath] if args.rjpath is not None else []
        encoding = args.encoding if args.encoding is not None else 'utf-8'
        content = args.content if args.content is not None else ''
        ret = cl.file_append(args.svpath.replace('"',''), content=content, encoding=encoding,
                             mkdir=args.mkdir, scope=args.scope,
                             client_data=client_data, fwpaths=fwpaths, rjpaths=rjpaths,
                             retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Result(resdata.Result):
            success: Union[str, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return True

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        payload = json.loads(convert.b64str2str(msg[2]))
        svpath = payload.get("svpath")
        content = payload.get("content", "")
        encoding = payload.get("encoding", "utf-8")
        mkdir = payload.get("mkdir") == 'True' or payload.get("mkdir") is True
        fwpaths = payload.get("fwpaths")
        rjpaths = payload.get("rjpaths")
        f = filer.Filer(data_dir, logger)
        st, res_json = f.file_append(svpath, content, encoding, mkdir, fwpaths, rjpaths)
        redis_cli.rpush(msg[1], res_json)
        return st
