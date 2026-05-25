from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class AgentSkillSave(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'skill_save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="Agentスキルマニフェストを保存します。スキルマニフェストには、AgentのDescription/Instruction/MCPサーバー設定を含めます。",
            description_en="Saves an Agent skill manifest. The skill manifest includes Agent Description/Instruction/MCP server settings.",
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
                dict(opt="skill_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="保存するスキルの名前を指定します。",
                    description_en="Specify the name of the skill to save."),
                dict(opt="skill_version", type=Options.T_STR, default="1.0.0", required=False, multi=False, hide=False, choice=None,
                    description_ja="スキルのバージョンを指定します。省略時は `1.0.0` を使用します。",
                    description_en="Specify the version of the skill. If omitted, `1.0.0` is used."),
                dict(opt="skill_description", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="スキルの概要説明を指定します。スキルの目的や提供する機能を記述します。",
                    description_en="Specify a summary description of the skill. Describe the purpose and features of the skill."),
                dict(opt="agent_description", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="スキルインストール時に設定するAgentのDescriptionを指定します。",
                    description_en="Specify the Agent Description to be set when the skill is installed."),
                dict(opt="agent_instruction", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="スキルインストール時に設定するAgentのInstructionを指定します。",
                    description_en="Specify the Agent Instruction to be set when the skill is installed."),
                dict(opt="llm", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                            + "const val = $(\"[name='llm']\").val();"
                            + "$(\"[name='llm']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llm']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llm']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llm');"
                            + "}",
                    description_ja="スキルインストール時に使用するLLM設定名を指定します。",
                    description_en="Specify the LLM configuration name to use when installing the skill."),
                dict(opt="mcp_servers", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="スキルが使用するMCPサーバーの定義をJSON形式で指定します。"
                                  "例: [{\"mcpserver_name\":\"my_mcp\",\"mcpserver_url\":\"http://localhost:8091/mcp\","
                                  "\"mcpserver_transport\":\"streamable-http\",\"mcpserver_delegated_auth\":false,"
                                  "\"mcpserver_apikey\":null,\"mcp_tools\":[]}]",
                    description_en="Specify the MCP server definitions used by the skill in JSON format. "
                                  "Example: [{\"mcpserver_name\":\"my_mcp\",\"mcpserver_url\":\"http://localhost:8091/mcp\","
                                  "\"mcpserver_transport\":\"streamable-http\",\"mcpserver_delegated_auth\":false,"
                                  "\"mcpserver_apikey\":null,\"mcp_tools\":[]}]"),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        mcp_servers = []
        if args.mcp_servers:
            try:
                mcp_servers = json.loads(args.mcp_servers)
            except Exception as e:
                msg = dict(warn=f"mcp_servers is not valid JSON: {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        manifest = dict(
            skill_name=args.skill_name,
            skill_version=args.skill_version,
            skill_description=args.skill_description,
            agent_description=args.agent_description,
            agent_instruction=args.agent_instruction,
            llm=args.llm,
            mcp_servers=mcp_servers,
        )
        payload_b64 = convert.str2b64str(common.to_str(manifest))
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
            manifest = json.loads(convert.b64str2str(msg[2]))
            name = manifest.get('skill_name')
            if not name:
                redis_cli.rpush(reskey, dict(warn="skill_name is required."))
                return self.RESP_WARN
            skill_path = data_dir / ".agent" / f"skill-{name}.json"
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            with skill_path.open('w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)
            redis_cli.rpush(reskey, dict(success=f"Skill manifest saved to '{str(skill_path)}'."))
            return self.RESP_SUCCESS
        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}"))
            return self.RESP_WARN
