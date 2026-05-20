from cmdbox.app import common, client, filer
from cmdbox.app.commons import resdata, validator
from cmdbox.app.features.cli.cmdbox import cmdbox_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic


class CmdboxInitdataInstall(cmdbox_base.CmdboxBase, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'cmdbox'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'initdata_install'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja="クライアント側やサーバー側に初期データを登録します。",
            description_en="Registers initial data on the client or server side.",
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
                     description_ja="サーバーのデータフォルダ以下のアップロード先パスを指定します。",
                     description_en="Specify the destination path under the server's data folder."),
                dict(opt="fwpath", type=Options.T_FILE, default=None, required=True, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。",
                     description_en="Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."),
                dict(opt="rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="scope", type=Options.T_STR, default="client", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="参照先スコープを指定します。指定可能なスコープは `client` , `current` , `server` です。",
                     description_en="Specifies the scope to be referenced. Possible values are `client`, `current`, and `server`.",
                     choice_show=dict(client=["client_data"])),
                dict(opt="initdata_path", type=Options.T_DIR, default=None, required=True, multi=True, hide=False, choice=None, fileio="in",
                     description_ja="インストールする初期データファイルのパスを指定します。複数指定可能です。",
                     description_en="Specify the path(s) of the initial data file(s) to install. Multiple paths can be specified."),
                dict(opt="client_data", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                     description_en="Specify the path of the data folder when local is referenced."),
                dict(opt="mkdir", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="中間フォルダがない場合作成します。",
                     description_en="If there is no in between folder, create one."),
                dict(opt="overwrite", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="アップロード先に存在していても上書きします。",
                     description_en="Overwrites the file even if it exists at the upload destination."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=60, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
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
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        client_data = Path(args.client_data.replace('"', '')) if args.client_data is not None else None
        initdata_paths = [Path(p.replace('"', '')) for p in args.initdata_path] if args.initdata_path is not None else []
        fwpaths = [p.replace('"', '') for p in args.fwpath] if args.fwpath is not None else ["/"]
        rjpaths = [p.replace('"', '') for p in args.rjpath] if args.rjpath is not None else []
        svpath = args.svpath.replace('"', '')

        results = []
        has_warn = False
        for upload_file in initdata_paths:
            ret = cl.file_upload(svpath, upload_file, scope=args.scope, client_data=client_data,
                                 fwpaths=fwpaths, rjpaths=rjpaths, mkdir=args.mkdir, orverwrite=args.orverwrite,
                                 retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
            results.append(dict(file=str(upload_file), result=ret))
            if 'success' not in ret:
                has_warn = True

        msg = dict(success=results) if not has_warn else dict(warn=results)
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if has_warn:
            return self.RESP_WARN, msg, cl

        return self.RESP_SUCCESS, msg, cl

    def output_schema(self) -> type:
        class FileResult(resdata.Base):
            file: str = pydantic.Field(default=None, description="アップロードしたファイルパス")
            result: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="アップロード結果")
        class Result(resdata.Result):
            success: Union[List[FileResult], None] = pydantic.Field(default=None, description="成功した場合の結果リスト")
        return Result
