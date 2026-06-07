from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LLMEmbed(feature.OneshotResultEdgeFeature, validator.Validator, limiter.LimitedFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'llm'

    def get_cmd(self) -> str:
        return 'embed'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
            description_ja="LLMに対しテキストのエンベディングを要求します。",
            description_en="Request text embedding from the LLM.",
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
                dict(opt="timeout", type=Options.T_INT, default="600", required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="llmname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                            + "const val = $(\"[name='llmname']\").val();"
                            + "$(\"[name='llmname']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llmname']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llmname']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llmname');"
                            + "}",
                    description_ja="読み込むLLM設定の名前を指定します。",
                    description_en="Specify the name of the LLM configuration to load."),
                dict(opt="input_text", type=Options.T_TEXT, default=None, required=True, multi=True, hide=False, choice=None,
                    description_ja="エンベディングするテキストを指定します。複数指定可能です。",
                    description_en="Specify the text to embed. Multiple values can be specified."),
            ]
        )

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:

        payload = dict(llmname=args.llmname, input_text=args.input_text,)
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[Any, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, str, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    @limiter.svrun_check_limit
    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        """
        サーバー側で受け取ったembedコマンドを処理します。
        """
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            llmname = payload.get('llmname')

            st, msg = self.embed(data_dir, logger, llmname, input_text=payload.get('input_text', []),)
            redis_cli.rpush(reskey, msg)
            return st

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def embed(self, data_dir: Path, logger: logging.Logger, llmname: str, *,
              input_text: Union[str, List[str]] = None) -> Tuple[int, Dict[str, Any]]:
        """
        LLMにテキストのエンベディングを要求します。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            llmname (str): LLM設定の名前
            input_text (Union[str, List[str]], optional): エンベディングするテキスト。文字列またはリストで指定します。

        Returns:
            Tuple[int, Dict[str, Any]]: (ステータスコード, エンベディング結果)
        """

        configure_path = data_dir / ".agent" / f"llm-{llmname}.json"
        if not configure_path.exists():
            msg = dict(warn=f"Specified LLM configuration '{llmname}' not found on server at '{str(configure_path)}'.")
            return self.RESP_WARN, msg
        configure = common.load_file(configure_path, lambda x: json.load(x), mode='r', encoding='utf-8', nolock=True)
        if 'llmtype' in configure and (configure['llmtype'] is None or configure['llmtype'] != 'embedding'):
            msg = dict(warn=f"LLM configuration '{llmname}' is not an embedding type.")
            return self.RESP_WARN, msg

        if not input_text:
            msg = dict(warn="input_text is required.")
            return self.RESP_WARN, msg
        if isinstance(input_text, str):
            input_text = [input_text]

        import litellm
        llmprov = configure.get('llmprov', None)
        if llmprov == 'openai':
            llmmodel = configure.get('llmmodel', None)
            llmapikey = configure.get('llmapikey', None)
            llmendpoint = configure.get('llmendpoint', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmapikey is None: raise ValueError("llmapikey is required.")
            response = litellm.embedding(
                model=llmmodel,
                input=input_text,
                api_key=llmapikey,
                api_base=llmendpoint,
            )
            res = [dict(index=item.get("index"), embedding=item.get("embedding")) for item in response.get("data", [])]
        elif llmprov == 'azureopenai':
            llmmodel = configure.get('llmmodel', None)
            llmapikey = configure.get('llmapikey', None)
            llmendpoint = configure.get('llmendpoint', None)
            llmapiversion = configure.get('llmapiversion', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmendpoint is None: raise ValueError("llmendpoint is required.")
            if "/openai/deployments" in llmendpoint:
                llmendpoint = llmendpoint.split("/openai/deployments")[0]
            if llmapikey is None: raise ValueError("llmapikey is required.")
            if llmapiversion is None: raise ValueError("llmapiversion is required.")
            if not llmmodel.startswith("azure/"):
                llmmodel = f"azure/{llmmodel}"
            response = litellm.embedding(
                model=llmmodel,
                input=input_text,
                api_key=llmapikey,
                api_base=llmendpoint,
                api_version=llmapiversion,
            )
            res = [dict(index=item.get("index"), embedding=item.get("embedding")) for item in response.get("data", [])]
        elif llmprov == 'vertexai':
            llmprojectid = configure.get('llmprojectid', None)
            llmsvaccountfile = configure.get('llmsvaccountfile', None)
            llmmodel = configure.get('llmmodel', None)
            llmlocation = configure.get('llmlocation', None)
            llmsvaccountfile_data = configure.get('llmsvaccountfile_data', {})
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmlocation is None: raise ValueError("llmlocation is required.")
            if llmsvaccountfile_data is None: raise ValueError("llmsvaccountfile_data is required.")
            response = litellm.embedding(
                model=llmmodel,
                input=input_text,
                vertex_credentials=llmsvaccountfile_data,
                vertex_location=llmlocation,
            )
            res = [dict(index=item.get("index"), embedding=item.get("embedding")) for item in response.get("data", [])]
        elif llmprov == 'ollama':
            llmmodel = configure.get('llmmodel', None)
            llmendpoint = configure.get('llmendpoint', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if not llmmodel.startswith("ollama/"):
                llmmodel = f"ollama/{llmmodel}"
            response = litellm.embedding(
                model=llmmodel,
                input=input_text,
                api_base=llmendpoint,
            )
            res = [dict(index=item.get("index"), embedding=item.get("embedding")) for item in response.get("data", [])]
        else:
            raise ValueError(f"Unsupported LLM provider: {llmprov}")
        return self.RESP_SUCCESS, dict(success=dict(data=res))
