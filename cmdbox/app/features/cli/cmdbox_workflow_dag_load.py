from cmdbox.app import common, client, feature
from cmdbox.app.commons import cache, convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class WorkflowDagLoad(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language=None):
        super().__init__(appcls, ver, language)
        self._cache = cache.MemoryCache()

    def get_mode(self) -> Union[str, List[str]]:
        return 'workflow'

    def get_cmd(self) -> str:
        return 'dag_load'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="保存されたDAGワークフロー定義を読み込みます。",
            description_en="Loads a saved DAG workflow definition.",
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
                dict(opt="dag_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('workflow','dag_list',{},(res)=>{"
                            + "const val = $(\"[name='dag_name']\").val();"
                            + "$(\"[name='dag_name']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='dag_name']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='dag_name']\").val(val);"
                            + "},$(\"[name='title']\").val(),'dag_name');"
                            + "}",
                    description_ja="読み込むDAGの名前を指定します。",
                    description_en="Specify the name of the DAG to load."),
                dict(opt="cache_timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=False, choice=None,
                    description_ja="設定をキャッシュする時間を秒数で指定します。",
                    description_en="Specify the duration, in seconds, for which settings should be cached."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        cached = self._cache.get(args.dag_name)
        if cached is not None:
            ret = dict(success=cached)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, ret, None

        payload = dict(dag_name=args.dag_name)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        self._cache.set(args.dag_name, ret.get('success', None), args.cache_timeout)
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class DAGData(resdata.Base):
            dag_name: str = pydantic.Field(..., description="DAGの名前")
            dag_yaml: str = pydantic.Field(..., description="DAG YAML定義テキスト")
        class Data(resdata.Data):
            data: Union[DAGData, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            name = payload.get('dag_name')
            dag_path = data_dir / ".workflow" / f"dag-{name}.yml"
            if not dag_path.exists():
                redis_cli.rpush(reskey, dict(warn=f"DAG '{name}' not found."))
                return self.RESP_WARN
            with dag_path.open('r', encoding='utf-8') as f:
                dag_yaml_str = f.read()
            redis_cli.rpush(reskey, dict(success=dict(data=dict(dag_name=name, dag_yaml=dag_yaml_str))))
            return self.RESP_SUCCESS
        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}"))
            return self.RESP_WARN
