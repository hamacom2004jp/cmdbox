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
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
                dict(opt="initdata_path", type=Options.T_DIR, default=None, required=False, multi=True, hide=False, choice=None, fileio="in",
                     description_ja="インストールする初期データファイルのパスを指定します。",
                     description_en="Specify the path(s) of the initial data file(s) to install."),
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

        client_data = Path(args.client_data.replace('"', '')).resolve() if args.client_data is not None else None
        initdata_paths = [Path(p.replace('"', '')) for p in args.initdata_path] if args.initdata_path is not None else []
        fwpaths = [p.replace('"', '') for p in args.fwpath] if args.fwpath is not None else ["/"]
        rjpaths = [p.replace('"', '') for p in args.rjpath] if args.rjpath is not None else []
        svpath = args.svpath.replace('"', '')

        results = []
        has_warn = False
        upload_paths = dict()
        for path in initdata_paths:
            if not path.exists():
                results.append(dict(file=str(path), result=dict(error="Path not found")))
                has_warn = True
                continue
            _path = str(path.resolve())
            if path.is_dir():
                for p in path.rglob("*"):
                    if p.is_file():
                        _p = str(p.resolve())
                        _p = _p[len(_path):].lstrip("/\\")
                        _p = str(Path(svpath) / _p).replace("\\", "/")
                        upload_paths[_p] = p
            else:
                # ディレクトリ以外が指定された場合はエラーとする
                msg = dict(warn=f"{str(path)} is not a directory.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, cl
        if has_warn:
            msg = dict(warn=results)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl
        for svp in upload_paths:
            ret = cl.file_upload(svp, upload_paths[svp], scope=args.scope, client_data=client_data,
                                 fwpaths=fwpaths, rjpaths=rjpaths, mkdir=args.mkdir, overwrite=args.overwrite,
                                 retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
            msg = dict(file=str(upload_paths[svp]))
            if 'success' not in ret:
                has_warn = True
                msg['msg'] = ret.get('warn', 'Unknown warning')
            results.append(msg)

        msg = dict(success=results) if not has_warn else dict(warn=results)
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if has_warn:
            return self.RESP_WARN, msg, cl

        return self.RESP_SUCCESS, msg, cl

    def output_schema(self) -> type:
        class FileResult(resdata.Base):
            file: str = pydantic.Field(default=None, description="アップロードしたファイルパス")
            result: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="アップロード結果")
        class Data(resdata.Data):
            data: Union[List[FileResult], None] = pydantic.Field(default=None, description="アップロード結果リスト")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
