from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import yaml


class WorkflowDagSave(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'workflow'

    def get_cmd(self) -> str:
        return 'dag_save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="DAG (Directed Acyclic Graph) ワークフロー定義をYAML形式で保存します。"
                           "DAGのノードには実行するコマンド情報と依存関係を記述します。",
            description_en="Saves a DAG (Directed Acyclic Graph) workflow definition in YAML format. "
                           "DAG nodes contain command information and dependency relationships.",
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
                dict(opt="dag_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="保存するDAGの名前を指定します。",
                    description_en="Specify the name of the DAG to save."),
                dict(opt="dag_yaml", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="DAG定義をYAML形式のテキストで指定します。"
                                  "ノードには id, type(command/python), mode, cmd, params, depends_on を記述します。"
                                  "例:\n"
                                  "dag_name: example\n"
                                  "description: サンプルDAG\n"
                                  "nodes:\n"
                                  "  - id: step1\n"
                                  "    type: command\n"
                                  "    mode: client\n"
                                  "    cmd: file_read\n"
                                  "    params:\n"
                                  "      svpath: /data/input.txt\n"
                                  "  - id: step2\n"
                                  "    type: python\n"
                                  "    code: |\n"
                                  "      result = inputs['step1']['content'].upper()\n"
                                  "    depends_on: [step1]",
                    description_en="Specify the DAG definition as YAML text. "
                                  "Nodes contain id, type(command/python), mode, cmd, params, depends_on."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        # YAML形式の検証
        try:
            dag_def = yaml.safe_load(args.dag_yaml)
        except yaml.YAMLError as e:
            msg = dict(warn=f"dag_yaml is not valid YAML: {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        payload = dict(dag_name=args.dag_name, dag_yaml=args.dag_yaml)
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
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
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
            dag_yaml_str = payload.get('dag_yaml', '')
            if not name:
                redis_cli.rpush(reskey, dict(warn="dag_name is required."))
                return self.RESP_WARN
            workflow_dir = data_dir / ".workflow"
            workflow_dir.mkdir(parents=True, exist_ok=True)
            dag_path = workflow_dir / f"dag-{name}.yml"
            with dag_path.open('w', encoding='utf-8') as f:
                f.write(dag_yaml_str)
            redis_cli.rpush(reskey, dict(success=f"DAG saved to '{str(dag_path)}'."))
            return self.RESP_SUCCESS
        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}"))
            return self.RESP_WARN
