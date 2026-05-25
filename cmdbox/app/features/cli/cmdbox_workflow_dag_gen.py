from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_llm_chat
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


DAG_SYSTEM_PROMPT = """You are a workflow DAG (Directed Acyclic Graph) generator.
The user will describe a workflow in natural language.
Your task is to output a valid DAG definition in YAML format.

Rules:
- The output MUST be only the YAML text. Do not include any other text, markdown code blocks, or explanations.
- Each node must have a unique `id` (snake_case).
- `type` must be either `command` or `python`.
- For `command` nodes: include `mode` (e.g. client, agent, llm), `cmd`, and `params` (as a mapping).
- For `python` nodes: include `code` (multiline Python code). The `inputs` dict is available with outputs of upstream nodes keyed by node id.
- `depends_on` is a list of node ids this node depends on. Leave empty [] for start nodes.
- The output variable of each node is accessible in downstream nodes via `inputs['<node_id>']`.

Output format:
dag_name: <name>
description: "<description>"
nodes:
  - id: <node_id>
    type: command
    mode: <mode>
    cmd: <cmd>
    params:
      <key>: <value>
    depends_on: []
  - id: <node_id2>
    type: python
    code: |
      result = inputs['<node_id>']['content']
    depends_on: [<node_id>]

{{msg_text}}"""


class WorkflowDagGen(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language=None):
        super().__init__(appcls, ver, language=language)
        self.llm_chat = cmdbox_llm_chat.LLMChat(appcls, ver, language=language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'workflow'

    def get_cmd(self) -> str:
        return 'dag_gen'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="自然言語のワークフロー記述からDAG YAMLを自動生成します。LLMを使用してDAG定義を生成します。",
            description_en="Automatically generates DAG YAML from natural language workflow descriptions using an LLM.",
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
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
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
                    description_ja="使用するLLM設定の名前を指定します。",
                    description_en="Specify the name of the LLM configuration to use."),
                dict(opt="description", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="生成するワークフローの自然言語による説明を記述します。",
                    description_en="Describe the workflow to generate in natural language."),
                dict(opt="save", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="Trueにすると、生成したDAGを自動的に保存します。",
                    description_en="If True, automatically saves the generated DAG."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        payload = dict(llmname=args.llmname, description=args.description, save=args.save)
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
            dag_yaml: Union[str, None] = pydantic.Field(default=None, description="生成されたDAG YAMLテキスト")
            saved: Union[bool, None] = pydantic.Field(default=None, description="保存されたかどうか")
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
            llmname = payload.get('llmname')
            description = payload.get('description', '')
            do_save = payload.get('save') == 'True' or payload.get('save') is True

            # LLMを呼び出してDAG YAMLを生成
            status, llm_result = self.llm_chat.chat(
                data_dir, logger, llmname,
                msg_role='user',
                msg_text=description,
                msg_text_system=DAG_SYSTEM_PROMPT,
            )
            if status != self.RESP_SUCCESS:
                redis_cli.rpush(reskey, llm_result)
                return self.RESP_WARN

            # LLMの応答からYAMLテキストを取り出す
            data = llm_result.get('success', {}).get('data', [])
            messages = [d for d in data if isinstance(d, dict)]
            dag_yaml_str = ''
            for m in messages:
                if m.get('content', None):
                    content = m.get('content')
                    if isinstance(content, dict) and content.get('type') == 'text':
                        dag_yaml_str += content.get('text', '')
                    elif isinstance(content, str):
                        dag_yaml_str += content

            dag_yaml_str = dag_yaml_str.strip()
            # コードブロックのマークダウン除去
            if dag_yaml_str.startswith('```'):
                lines = dag_yaml_str.split('\n')
                start = 1
                end = len(lines)
                if lines[-1].strip() == '```':
                    end = len(lines) - 1
                dag_yaml_str = '\n'.join(lines[start:end])

            saved = False
            if do_save and dag_yaml_str:
                import yaml as _yaml
                try:
                    parsed = _yaml.safe_load(dag_yaml_str)
                    dag_name = parsed.get('dag_name', 'generated')
                    workflow_dir = data_dir / ".workflow"
                    workflow_dir.mkdir(parents=True, exist_ok=True)
                    dag_path = workflow_dir / f"dag-{dag_name}.yml"
                    with dag_path.open('w', encoding='utf-8') as f:
                        f.write(dag_yaml_str)
                    saved = True
                    logger.info(f"Generated DAG saved to '{str(dag_path)}'.")
                except Exception as e:
                    logger.warning(f"Failed to save generated DAG: {e}")

            redis_cli.rpush(reskey, dict(success=dict(dag_yaml=dag_yaml_str, saved=saved)))
            return self.RESP_SUCCESS

        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}"))
            return self.RESP_WARN
