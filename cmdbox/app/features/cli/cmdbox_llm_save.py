from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import re


class LLMSave(feature.OneshotResultEdgeFeature, validator.Validator, limiter.LimitedFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'llm'

    def get_cmd(self) -> str:
        return 'save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="LLM 設定を保存します。",
            description_en="Saves LLM configuration.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="llmname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="保存するLLM設定の名前を指定します。",
                     description_en="Specify the name of the LLM configuration to save."),
                dict(opt="llmprov", type=Options.T_STR, default=None, required=True, multi=False, hide=False,
                     choice=["", "azureopenai", "openai", "vertexai", "ollama", "proxy", "custom"],
                     description_ja="llmのプロバイダを指定します。",
                     description_en="Specify llm provider.",
                     choice_show=dict(azureopenai=["llmapikey", "llmendpoint", "llmmodel", "llmapiversion"],
                                      openai=["llmapikey", "llmendpoint", "llmmodel"],
                                      vertexai=["llmprojectid", "llmsvaccountfile", "llmlocation", "llmmodel", "llmseed", "llmtemperature"],
                                      ollama=["llmendpoint", "llmmodel", "llmtemperature"],
                                      proxy=["llmendpoint", "llmmodel", "llmapikey"],
                                      custom=["llmprojectid", "llmsvaccountfile", "llmlocation",
                                              "llmapikey", "llmapiversion", "llmendpoint", "llmmodel", "llmseed", "llmtemperature"]),
                     ),
                dict(opt="llmtype", type=Options.T_STR, default="chat", required=False, multi=False, hide=False, choice=['chat', 'embedding'],
                     description_ja="保存するLLM設定のタイプを指定します。",
                     description_en="Specify the type of the LLM configuration to save."),
                dict(opt="llmprojectid", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのプロジェクトIDを指定します。",
                     description_en="Specify the project ID for llm's provider connection."),
                dict(opt="llmsvaccountfile", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="llmのプロバイダ接続のためのサービスアカウントファイルを指定します。",
                     description_en="Specifies the service account file for llm's provider connection."),
                dict(opt="llmlocation", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのロケーションを指定します。",
                     description_en="Specifies the location for llm provider connections."),
                dict(opt="llmapikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのAPIキーを指定します。",
                     description_en="Specify API key for llm provider connection."),
                dict(opt="llmapiversion", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのAPIバージョンを指定します。",
                     description_en="Specifies the API version for llm provider connections."),
                dict(opt="llmendpoint", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのエンドポイントを指定します。",
                     description_en="Specifies the endpoint for llm provider connections."),
                dict(opt="llmmodel", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="llmモデルを指定します。",
                     description_en="Specifies the llm model."),
                dict(opt="llmseed", type=Options.T_INT, default=13, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmモデルを使用するときのシード値を指定します。",
                     description_en="Specifies the seed value when using llm model."),
                dict(opt="llmtemperature", type=Options.T_FLOAT, default=0.1, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのモデルを使用するときのtemperatureを指定します。",
                     description_en="Specifies the temperature when using llm model."),
                dict(opt="llmpriority", type=Options.T_INT, default=1, required=True, multi=False, hide=False, choice=None,
                     description_ja="llmモデルを使用するときの優先度を指定します。小さい値ほど優先されます。",
                     description_en="Specifies the priority when using llm model. Lower values indicate higher priority."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None, web="mask",
                     description_ja="このユーザーグループでLLM設定の編集・保存を行うように指定します。",
                     description_en="Specify user groups used to authorize LLM configuration edit/save operations."),
                dict(opt="owner_groups", type=Options.T_MLIST, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('web','group_list',{},(res)=>{"
                              + "const val = $(\"[name='owner_groups']\").val();"
                              + "$(\"[name='owner_groups']\").empty().append('<option></option>');"
                              + "res['data'].map(elm=>{$(\"[name='owner_groups']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                              + "$(\"[name='owner_groups']\").val(val);"
                              + "},$(\"[name='title']\").val(),'owner_groups');"
                              + "}",
                     description_ja="このLLM設定の保存(save/del)を許可するグループを指定します。省略時はすべてのグループを許可します。",
                     description_en="Specify the groups that are allowed to save (save/del) this LLM configuration. If omitted, all groups are allowed."),
                dict(opt="user_groups", type=Options.T_MLIST, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('web','group_list',{},(res)=>{"
                              + "const val = $(\"[name='user_groups']\").val();"
                              + "$(\"[name='user_groups']\").empty().append('<option></option>');"
                              + "res['data'].map(elm=>{$(\"[name='user_groups']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                              + "$(\"[name='user_groups']\").val(val);"
                              + "},$(\"[name='title']\").val(),'user_groups');"
                              + "}",
                     description_ja="このLLM設定の使用(list/load)を許可するグループを指定します。省略時はすべてのグループを許可します。",
                     description_en="Specify the groups that are allowed to use this LLM configuration (list/load). If omitted, all groups are allowed."),
            ]
        )

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        owner_groups = [g for g in args.owner_groups if g] if hasattr(args, 'owner_groups') and isinstance(args.owner_groups, list) else args.owner_groups if hasattr(args, 'owner_groups') else None
        user_groups = [g for g in args.user_groups if g] if hasattr(args, 'user_groups') and isinstance(args.user_groups, list) else args.user_groups if hasattr(args, 'user_groups') else None
        groups = [g for g in args.groups if g] if hasattr(args, 'groups') and isinstance(args.groups, list) else args.groups if hasattr(args, 'groups') else None
        if owner_groups and len([g for g in owner_groups if g in groups]) <= 0:
            msg = dict(warn=f"Owner groups must be in the allowed groups. groups:{groups} , owner_groups:{owner_groups}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if user_groups and len([g for g in user_groups if g in groups]) <= 0:
            msg = dict(warn=f"User groups must be in the allowed groups. groups:{groups} , user_groups:{user_groups}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if owner_groups and user_groups and len([g for g in user_groups if g in owner_groups]) <= 0:
            msg = dict(warn=f"User groups must be in the owner groups. owner_groups:{owner_groups} , user_groups:{user_groups}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        configure = dict(
            llmname=args.llmname,
            llmprov=args.llmprov,
            llmtype=args.llmtype if hasattr(args, 'llmtype') and args.llmtype else 'chat',
            llmprojectid=args.llmprojectid if hasattr(args, 'llmprojectid') else None,
            llmsvaccountfile=args.llmsvaccountfile if hasattr(args, 'llmsvaccountfile') else None,
            llmlocation=args.llmlocation if hasattr(args, 'llmlocation') else None,
            llmapikey=args.llmapikey if hasattr(args, 'llmapikey') else None,
            llmapiversion=args.llmapiversion if hasattr(args, 'llmapiversion') else None,
            llmendpoint=args.llmendpoint if hasattr(args, 'llmendpoint') else None,
            llmmodel=args.llmmodel if hasattr(args, 'llmmodel') else None,
            llmseed=args.llmseed if hasattr(args, 'llmseed') else None,
            llmtemperature=args.llmtemperature if hasattr(args, 'llmtemperature') else None,
            llmpriority=args.llmpriority if hasattr(args, 'llmpriority') else None,
            owner_groups=owner_groups,
            user_groups=user_groups,
            groups=args.groups if hasattr(args, 'groups') else None,
            save_mode=args.save_mode if hasattr(args, 'save_mode') else None,
        )

        if hasattr(args, 'llmsvaccountfile') and args.llmsvaccountfile is not None:
            svaccount_path = Path(args.llmsvaccountfile)
            if not svaccount_path.exists():
                msg = dict(warn=f"The specified llmsvaccountfile '{args.llmsvaccountfile}' does not exist.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            try:
                with svaccount_path.open('r', encoding='utf-8') as f:
                    configure['llmsvaccountfile_data'] = json.load(f)
            except Exception as e:
                msg = dict(warn=f"Failed to load the specified llmsvaccountfile '{args.llmsvaccountfile}': {str(e)}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        configure_b64 = convert.str2b64str(common.to_str(configure))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [configure_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    @limiter.svrun_check_limit
    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))
            groups = configure.pop('groups', None)
            name = configure.get('llmname')
            configure_path = data_dir / ".agent" / f"llm-{name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            chk, msg = self.check_save_mode(name, configure, configure_path)
            if not chk:
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN
            if configure_path.exists():
                before = common.load_file(configure_path, lambda f: json.load(f), encoding='utf-8', nolock=False)
                if not self.is_allowed_by_groups(groups, before.get('owner_groups'), redis_cli):
                    msg = dict(warn=f"You do not have permission to edit LLM configuration '{name}'.")
                    redis_cli.rpush(reskey, msg)
                    return self.RESP_WARN
            common.save_file(configure_path, lambda f: json.dump(configure, f, indent=4),
                             encoding='utf-8', nolock=False)
            msg = dict(success=f"LLM configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def svrun_registrations(self, data_dir, logger, opt, msg):
        llm_dir = data_dir / '.agent'
        paths = llm_dir.glob(f"llm-*.json")
        count = len(list(paths))
        return count
