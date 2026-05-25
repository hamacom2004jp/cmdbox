from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class AgentSkillInstall(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'skill_install'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="Agentスキルマニフェストをもとに、MCPサーバー設定とAgent設定を自動的に作成・登録します。"
                           "スキルマニフェストに記載された mcp_servers の各設定を `agent mcpsv_save` で登録し、"
                           "agent_description/agent_instruction を `agent agent_save` で登録します。",
            description_en="Automatically creates and registers MCP server settings and Agent settings based on the Agent skill manifest. "
                           "Registers each mcp_servers setting in the skill manifest using `agent mcpsv_save`, "
                           "and registers agent_description/agent_instruction using `agent agent_save`.",
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
                dict(opt="skill_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('agent','skill_list',{},(res)=>{"
                            + "const val = $(\"[name='skill_name']\").val();"
                            + "$(\"[name='skill_name']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='skill_name']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='skill_name']\").val(val);"
                            + "},$(\"[name='title']\").val(),'skill_name');"
                            + "}",
                    description_ja="インストールするスキルの名前を指定します。",
                    description_en="Specify the name of the skill to install."),
                dict(opt="overwrite", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="既存のMCPサーバー設定やAgent設定を上書きします。",
                    description_en="Overwrite existing MCP server settings and Agent settings."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        payload = dict(skill_name=args.skill_name, overwrite=args.overwrite)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class InstalledItem(pydantic.BaseModel):
            type: str = pydantic.Field(description="登録種別 (mcpsv / agent)")
            name: str = pydantic.Field(description="登録名")
            path: str = pydantic.Field(description="保存パス")
        class Data(resdata.Data):
            skill_name: Union[str, None] = pydantic.Field(default=None, description="スキル名")
            installed: List[InstalledItem] = pydantic.Field(default_factory=list, description="登録済みアイテム一覧")
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
            skill_name = payload.get('skill_name')
            overwrite = payload.get('overwrite') == 'True' or payload.get('overwrite') is True

            skill_path = data_dir / ".agent" / f"skill-{skill_name}.json"
            if not skill_path.exists():
                redis_cli.rpush(reskey, dict(warn=f"Skill '{skill_name}' not found. Please run 'agent skill_save' first."))
                return self.RESP_WARN

            with skill_path.open('r', encoding='utf-8') as f:
                manifest = json.load(f)

            agent_dir = data_dir / ".agent"
            agent_dir.mkdir(parents=True, exist_ok=True)
            installed = []

            # 1. MCPサーバー設定を登録
            for mcp in manifest.get('mcp_servers', []):
                mcp_name = mcp.get('mcpserver_name')
                if not mcp_name:
                    continue
                mcp_path = agent_dir / f"mcpsv-{mcp_name}.json"
                if mcp_path.exists() and not overwrite:
                    logger.warning(f"MCP server '{mcp_name}' already exists. Skipping.")
                    continue
                # mcpsv_save と同形式で保存
                configure = dict(
                    mcpserver_name=mcp_name,
                    mcpserver_url=mcp.get('mcpserver_url', 'http://localhost:8091/mcp'),
                    mcpserver_apikey=mcp.get('mcpserver_apikey'),
                    mcpserver_delegated_auth=mcp.get('mcpserver_delegated_auth', False),
                    mcpserver_transport=mcp.get('mcpserver_transport', 'streamable-http'),
                    mcpserver_mcp_tools=mcp.get('mcp_tools', []),
                )
                with mcp_path.open('w', encoding='utf-8') as f:
                    json.dump(configure, f, indent=4)
                installed.append(dict(type='mcpsv', name=mcp_name, path=str(mcp_path)))
                logger.info(f"MCP server '{mcp_name}' registered.")

            # 2. Agent設定を登録
            agent_name = skill_name
            agent_path = agent_dir / f"agent-{agent_name}.json"
            if agent_path.exists() and not overwrite:
                logger.warning(f"Agent '{agent_name}' already exists. Skipping agent registration.")
            else:
                mcp_server_names = [mcp.get('mcpserver_name') for mcp in manifest.get('mcp_servers', []) if mcp.get('mcpserver_name')]
                agent_configure = dict(
                    agent_name=agent_name,
                    agent_type='local',
                    use_planner=False,
                    llm=manifest.get('llm'),
                    mcpservers=mcp_server_names,
                    subagents=[],
                    a2asv_baseurl=None,
                    a2asv_delegated_auth=False,
                    a2asv_apikey=None,
                    agent_description=manifest.get('agent_description', ''),
                    agent_instruction=manifest.get('agent_instruction', ''),
                )
                with agent_path.open('w', encoding='utf-8') as f:
                    json.dump(agent_configure, f, indent=4)
                installed.append(dict(type='agent', name=agent_name, path=str(agent_path)))
                logger.info(f"Agent '{agent_name}' registered.")

            result = dict(skill_name=skill_name, installed=installed)
            redis_cli.rpush(reskey, dict(success=result))
            return self.RESP_SUCCESS

        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}"))
            return self.RESP_WARN
