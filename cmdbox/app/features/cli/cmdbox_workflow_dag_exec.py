from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class WorkflowDagExec(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'workflow'

    def get_cmd(self) -> str:
        return 'dag_exec'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="DAGワークフローを実行します。networkxライブラリを使用してDAGの依存関係を解析し、"
                           "各ノードを順次/並列実行します。commandノードはcmdboxコマンドとして、"
                           "pythonノードはサンドボックス内でPythonコードとして実行します。",
            description_en="Executes a DAG workflow. Uses the networkx library to analyze DAG dependencies "
                           "and executes each node sequentially/in parallel. Command nodes are executed as cmdbox commands, "
                           "and python nodes are executed as Python code in a sandbox.",
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
                dict(opt="timeout", type=Options.T_INT, default=600, required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="dag_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('workflow','dag_list',{},(res)=>{"
                            + "const val = $(\"[name='dag_name']\").val();"
                            + "$(\"[name='dag_name']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='dag_name']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='dag_name']\").val(val);"
                            + "},$(\"[name='title']\").val(),'dag_name');"
                            + "}",
                    description_ja="実行するDAGの名前を指定します。dag_yamlと排他指定です。",
                    description_en="Specify the name of the DAG to execute. Mutually exclusive with dag_yaml."),
                dict(opt="dag_yaml", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="直接DAG YAMLを指定して実行します。dag_nameと排他指定です。",
                    description_en="Specify DAG YAML directly for execution. Mutually exclusive with dag_name."),
                dict(opt="params", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="DAG実行時に渡す初期パラメータをJSON形式で指定します。",
                    description_en="Specify initial parameters to pass at DAG execution in JSON format."),
                dict(opt="use_docker", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="Trueにすると、pythonノードの実行にDockerサンドボックスを使用します。",
                    description_en="If True, uses Docker sandbox for executing python nodes."),
                dict(opt="docker_image", type=Options.T_STR, default='cmdbox-python-sandbox:latest', required=False, multi=False, hide=False, choice=None,
                    description_ja="Dockerサンドボックスで使用するイメージ名を指定します。use_docker=Trueの場合に有効です。",
                    description_en="Specify the image name to use in Docker sandbox. Effective when use_docker=True."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not args.dag_name and not args.dag_yaml:
            msg = dict(warn="Either dag_name or dag_yaml is required.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        payload = dict(
            dag_name=args.dag_name,
            dag_yaml=args.dag_yaml,
            params=args.params,
            use_docker=args.use_docker,
            docker_image=args.docker_image,
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class NodeResult(pydantic.BaseModel):
            node_id: str = pydantic.Field(description="ノードID")
            status: str = pydantic.Field(description="実行ステータス (success/warn/error)")
            output: Union[Any, None] = pydantic.Field(default=None, description="ノードの出力")
        class Data(resdata.Data):
            dag_name: Union[str, None] = pydantic.Field(default=None, description="DAG名")
            node_results: List[NodeResult] = pydantic.Field(default_factory=list, description="各ノードの実行結果")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            import networkx as nx
            import yaml as _yaml
        except ImportError as e:
            redis_cli.rpush(reskey, dict(warn=f"Required package not found: {e}. Please install networkx and pyyaml."))
            return self.RESP_WARN
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            dag_name = payload.get('dag_name')
            dag_yaml_str = payload.get('dag_yaml')
            params_str = payload.get('params')
            use_docker = payload.get('use_docker') == 'True' or payload.get('use_docker') is True
            docker_image = payload.get('docker_image', 'cmdbox-python-sandbox:latest')

            # 初期パラメータ
            initial_params: Dict[str, Any] = {}
            if params_str:
                try:
                    initial_params = json.loads(params_str)
                except Exception:
                    pass

            # DAG定義をロード
            if dag_yaml_str:
                dag_def = _yaml.safe_load(dag_yaml_str)
            elif dag_name:
                dag_path = data_dir / ".workflow" / f"dag-{dag_name}.yml"
                if not dag_path.exists():
                    redis_cli.rpush(reskey, dict(warn=f"DAG '{dag_name}' not found."))
                    return self.RESP_WARN
                with dag_path.open('r', encoding='utf-8') as f:
                    dag_def = _yaml.safe_load(f.read())
            else:
                redis_cli.rpush(reskey, dict(warn="Either dag_name or dag_yaml is required."))
                return self.RESP_WARN

            dag_name = dag_def.get('dag_name', dag_name or 'unknown')
            nodes = dag_def.get('nodes', [])

            # networkx DAG構築
            G = nx.DiGraph()
            node_map: Dict[str, Dict[str, Any]] = {}
            for node in nodes:
                nid = node['id']
                G.add_node(nid)
                node_map[nid] = node
                for dep in node.get('depends_on', []):
                    G.add_edge(dep, nid)

            if not nx.is_dag(G):
                redis_cli.rpush(reskey, dict(warn="The provided DAG definition contains cycles."))
                return self.RESP_WARN

            # 位相ソート順に実行
            outputs: Dict[str, Any] = {'__params__': initial_params}
            node_results: List[Dict[str, Any]] = []

            for nid in nx.topological_sort(G):
                node = node_map[nid]
                ntype = node.get('type', 'command')
                try:
                    if ntype == 'command':
                        result = self._exec_command_node(node, outputs, data_dir, logger)
                    elif ntype == 'python':
                        result = self._exec_python_node(node, outputs, logger, use_docker, docker_image)
                    else:
                        raise ValueError(f"Unknown node type: {ntype}")
                    outputs[nid] = result
                    node_results.append(dict(node_id=nid, status='success', output=result))
                    logger.info(f"DAG node '{nid}' executed successfully.")
                except Exception as e:
                    logger.warning(f"DAG node '{nid}' failed: {e}", exc_info=True)
                    node_results.append(dict(node_id=nid, status='error', output=str(e)))
                    redis_cli.rpush(reskey, dict(warn=f"DAG node '{nid}' failed: {e}",
                                                 node_results=node_results))
                    return self.RESP_WARN

            redis_cli.rpush(reskey, dict(success=dict(dag_name=dag_name, node_results=node_results)))
            return self.RESP_SUCCESS

        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}"))
            return self.RESP_WARN

    def _exec_command_node(self, node: Dict[str, Any], outputs: Dict[str, Any],
                           data_dir: Path, logger: logging.Logger) -> Any:
        """commandノードを実行します。cmdboxのappcls経由でコマンドを実行します。"""
        import subprocess
        import sys
        mode = node.get('mode', 'client')
        cmd = node.get('cmd')
        params = node.get('params', {}) or {}
        # パラメータ内の{{node_id}}プレースホルダーを解決
        resolved_params = {}
        for k, v in params.items():
            if isinstance(v, str):
                for dep_id, dep_output in outputs.items():
                    placeholder = f"{{{{{dep_id}}}}}"
                    if placeholder in v:
                        v = v.replace(placeholder, str(dep_output))
            resolved_params[k] = v

        args_list = ['-m', mode, '-c', cmd]
        for k, v in resolved_params.items():
            if v is not None:
                args_list.extend([f'--{k}', str(v)])

        proc = subprocess.run(
            [sys.executable, '-m', 'cmdbox'] + args_list,
            capture_output=True, text=True, timeout=300,
            cwd=str(data_dir.parent) if data_dir else None
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Command node '{node.get('id')}' failed (rc={proc.returncode}): {proc.stderr[:500]}")
        try:
            return json.loads(proc.stdout.strip())
        except Exception:
            return proc.stdout.strip()

    def _exec_python_node(self, node: Dict[str, Any], outputs: Dict[str, Any],
                          logger: logging.Logger, use_docker: bool, docker_image: str) -> Any:
        """pythonノードを実行します。sandboxでPythonコードを実行します。"""
        import subprocess
        import sys
        import tempfile
        import os

        code = node.get('code', '')
        # inputsをノード出力から構築 (依存するノードの出力)
        depends_on = node.get('depends_on', [])
        inputs = {dep: outputs.get(dep) for dep in depends_on}
        # __params__も参照可能にする
        if '__params__' in outputs:
            inputs['__params__'] = outputs['__params__']

        # ラッパーコード: inputs変数を注入し、resultを標準出力に出力する
        wrapper = (
            "import json as _json\n"
            f"inputs = _json.loads({json.dumps(json.dumps(inputs, default=str))})\n"
            "result = None\n"
            + code + "\n"
            "print(_json.dumps(result, default=str))\n"
        )

        if use_docker:
            # Dockerコンテナ内で実行
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(wrapper)
                tmp_path = f.name
            try:
                proc = subprocess.run(
                    ['docker', 'run', '--rm',
                     '-v', f'{tmp_path}:/sandbox/script.py:ro',
                     docker_image,
                     'python', '/sandbox/script.py'],
                    capture_output=True, text=True, timeout=300
                )
            finally:
                os.unlink(tmp_path)
        else:
            # ローカルのPythonで実行 (subprocess経由のサブプロセスで分離)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(wrapper)
                tmp_path = f.name
            try:
                proc = subprocess.run(
                    [sys.executable, tmp_path],
                    capture_output=True, text=True, timeout=300
                )
            finally:
                os.unlink(tmp_path)

        if proc.returncode != 0:
            raise RuntimeError(f"Python node '{node.get('id')}' failed (rc={proc.returncode}): {proc.stderr[:500]}")
        try:
            return json.loads(proc.stdout.strip())
        except Exception:
            return proc.stdout.strip()
