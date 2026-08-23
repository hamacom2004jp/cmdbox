from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli import (
    cmdbox_agent_agent_list,
    cmdbox_agent_mcpsv_list,
    cmdbox_llm_list,
    cmdbox_skill_list,
)
from cmdbox.app.features.cli.agent import agant_base
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import re


class AgentAgentSave(agant_base.AgentBase, validator.Validator, limiter.LimitedFeature):
    def __init__(self, appcls, ver, language = None):
        super().__init__(appcls, ver, language)
        self.agent_list = cmdbox_agent_agent_list.AgentAgentList(appcls, ver, language)
        self.mcpsv_list = cmdbox_agent_mcpsv_list.AgentMcpList(appcls, ver, language)
        self.llm_list = cmdbox_llm_list.LLMList(appcls, ver, language)
        self.skill_list = cmdbox_skill_list.SkillList(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'agent_save'

    def get_option(self) -> Dict[str, Any]:

        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="Agent 設定を保存します。",
            description_en="Saves agent configuration.",
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
                dict(opt="agent_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="保存するAgentの名前を指定します。",
                    description_en="Specify the name of the agent configuration to save."),
                dict(opt="agent_type", type=Options.T_STR, default='local', required=True, multi=False, hide=False,
                    choice=['local', 'remote'],
                    choice_show=dict(local=["llm", "mcpservers", "subagents", "skill_name", "agent_instruction", "prompt_param"],
                                     remote=[]),
                    description_ja="Agentの種類を指定します。`local` または `remote` を指定します。",
                    description_en="Specify the agent type. Specify either `local` or `remote`."),
                dict(opt="reasoning_effort", type=Options.T_STR, default="off", required=False, multi=False, hide=False,
                     choice=["off", "on", "low", "medium", "high", "xhigh"],
                    description_ja="エージェントで思考の連鎖の深さを指定します。使用するモデルによってはサポートされていない場合があります。",
                    description_en="Specify the depth of the thought chain in the agent. Depending on the model you are using, this feature may not be supported."),
                dict(opt="llm", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                    choice_fn=self.choice_llms,
                    description_ja="Agentが参照するLLM設定名を指定します。",
                    description_en="Specify the LLM configuration name referenced by the Agent."),
                dict(opt="mcpservers", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=[],
                    choice_fn=self.choice_mcvpservers,
                    description_ja="Agentが利用するMCPサーバー名を指定します。",
                    description_en="Specify the MCP server name used by the Agent."),
                dict(opt="subagents", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=[],
                    choice_fn=self.choice_subagents,
                    description_ja="Agentが利用するサブエージェント名を指定します。",
                    description_en="Specify the subagent name used by the agent."),
                dict(opt="skill_names", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=[],
                    choice_fn=self.choice_skills,
                    description_ja="Agentが利用するスキル名を指定します。複数指定できます。",
                    description_en="Specify skill names used by the agent. Multiple values are allowed."),
                dict(opt="a2asv_baseurl", type=Options.T_STR, default="http://localhost:8071/a2a/<target_agent_name>", required=False, multi=False, hide=False, choice=None,
                    description_ja="A2A ServerのURLを指定します。<target_agent_name>はagent名を指定します。",
                    description_en="Specify the URL of the A2A Server. <target_agent_name> specifies the name of the agent to be called."),
                dict(opt="a2asv_delegated_auth", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="A2A Serverの認証を現在のログインユーザーのAPI Keyを使用して行います。",
                    description_en="Authenticate the A2A Server using the API Key of the currently logged-in user.",),
                dict(opt="a2asv_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="A2A Server起動時のAPI Keyを指定します。 また`a2asv_delegated_auth` が無効な場合は、Agent実行時に使用も使用されます。",
                    description_en="Specify the API Key when starting the A2A Server. Additionally, if `a2asv_delegated_auth` is disabled, it will also be used when running the Agent.",),
                dict(opt="agent_description", type=Options.T_TEXT, default=self.agent_description, required=False, multi=False, hide=False, choice=None,
                    description_ja="Agentの能力に関する説明を指定します。モデルはこれを使用して、制御をエージェントに委譲するかどうかを決定します。一行の説明で十分であり、推奨されます。",
                    description_en="Specify a description of the agent's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."),
                dict(opt="agent_instruction", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="Agentが使用するLLMモデル向けの指示を指定します。これはエージェントの挙動を促すものになります。",
                    description_en="Specify instructions for the LLM model used by the agent. These will guide the agent's behavior."),
                dict(opt="agent_system_instruction", type=Options.T_TEXT, default=self.agent_system_instruction, required=False, multi=False, hide=True, choice=None,
                    description_ja="サービス提供側がエンドユーザーに公開せずに内部的に設定するシステムプロンプトを指定します。`agent_instruction` と同様にAgentに渡されますが、こちらは非公開の設定です。",
                    description_en="Specify a system prompt set internally by the service provider without exposing it to end users. Like `agent_instruction`, it is passed to the Agent, but this one is private."),
                dict(opt="prompt_param", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="`agent_instruction` や `agent_system_instruction` に埋め込まれたプレースホルダーに対応するパラメータを指定します。例: `{\"key\": \"value\"}`",
                    description_en="Specify parameters corresponding to placeholders embedded in `agent_instruction` or `agent_system_instruction`. Example: `{\"key\": \"value\"}`"),
            ]
        )

    def choice_mcvpservers(self, o:Dict[str, Any], webmode:bool, opt:Dict[str, Any]) -> Any:
        logger = common.default_logger(False, ver=self.ver, webcall=webmode)
        args = argparse.Namespace(**opt)
        st, res, _ = self.mcpsv_list.apprun(logger, args, 0.0, [])
        if st != self.RESP_SUCCESS:
            return []
        ret = [k.get('name') for k in res.get('success', {}).get('data', [])]
        return [''] + ret

    def choice_subagents(self, o:Dict[str, Any], webmode:bool, opt:Dict[str, Any]) -> Any:
        logger = common.default_logger(False, ver=self.ver, webcall=webmode)
        args = argparse.Namespace(**opt)
        st, res, _ = self.agent_list.apprun(logger, args, 0.0, [])
        if st != self.RESP_SUCCESS:
            return []
        ret = [k.get('name') for k in res.get('success', {}).get('data', [])]
        return [''] + ret

    def choice_llms(self, o:Dict[str, Any], webmode:bool, opt:Dict[str, Any]) -> Any:
        logger = common.default_logger(False, ver=self.ver, webcall=webmode)
        args = argparse.Namespace(**opt)
        st, res, _ = self.llm_list.apprun(logger, args, 0.0, [])
        if st != self.RESP_SUCCESS:
            return []
        ret = [k.get('name') for k in res.get('success', {}).get('data', [])]
        return [''] + ret

    def choice_skills(self, o:Dict[str, Any], webmode:bool, opt:Dict[str, Any]) -> Any:
        logger = common.default_logger(False, ver=self.ver, webcall=webmode)
        args = argparse.Namespace(**opt)
        st, res, _ = self.skill_list.apprun(logger, args, 0.0, [])
        if st != self.RESP_SUCCESS:
            return []
        ret = [k.get('name') for k in res.get('success', {}).get('data', [])]
        return [''] + ret

    def list_mcvpservers(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("mcpsv-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('mcpsv-') or not name.endswith('.json'):
                continue
            svname = name[6:-5]
            ret.append(svname)
        return ret

    def list_llms(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("llm-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('llm-') or not name.endswith('.json'):
                continue
            llmname = name[4:-5]
            ret.append(llmname)
        return ret

    def list_agents(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("agent-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('agent-') or not name.endswith('.json'):
                continue
            svname = name[6:-5]
            ret.append(svname)
        return ret

    def list_skills(self, data_dir: str) -> List[str]:
        skills_dir = Path(data_dir) / '.skills'
        if not skills_dir.exists() or not skills_dir.is_dir():
            return []
        ret: List[str] = []
        for p in sorted(skills_dir.iterdir()):
            if p.is_dir() and (p / 'SKILL.md').exists():
                ret.append(p.name)
        return ret

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if args.agent_type == 'local':
            if not hasattr(args, 'llm') or args.llm is None:
                msg = dict(warn="Please specify --llm for local agent")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        elif args.agent_type == 'remote':
            if not hasattr(args, 'a2asv_baseurl') or args.a2asv_baseurl is None:
                msg = dict(warn="Please specify --a2asv_baseurl for remote agent")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        if not args.a2asv_delegated_auth and args.agent_type == 'remote' and (not getattr(args, 'a2asv_apikey', None) or args.a2asv_apikey is None):
            msg = dict(warn="Please specify --a2asv_apikey or enable --a2asv_delegated_auth")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        configure = dict(
            agent_name=args.agent_name,
            agent_type=args.agent_type,
            reasoning_effort=args.reasoning_effort if hasattr(args, 'reasoning_effort') else "off",
            a2asv_baseurl=args.a2asv_baseurl if hasattr(args, 'a2asv_baseurl') else None,
            a2asv_delegated_auth=args.a2asv_delegated_auth if hasattr(args, 'a2asv_delegated_auth') else False,
            a2asv_apikey=args.a2asv_apikey if hasattr(args, 'a2asv_apikey') else None,
            llm=args.llm if hasattr(args, 'llm') else None,
            mcpservers=list(set(args.mcpservers)) if hasattr(args, 'mcpservers') and args.mcpservers is not None else None,
            subagents=list(set(args.subagents)) if hasattr(args, 'subagents') and args.subagents is not None else None,
            skill_names=list(set(args.skill_names)) if hasattr(args, 'skill_names') and args.skill_names is not None else None,
            agent_description=args.agent_description if hasattr(args, 'agent_description') else None,
            agent_instruction=args.agent_instruction if hasattr(args, 'agent_instruction') else None,
            agent_system_instruction=args.agent_system_instruction if hasattr(args, 'agent_system_instruction') else None,
            prompt_param=args.prompt_param if hasattr(args, 'prompt_param') else None,
            save_mode=args.save_mode if hasattr(args, 'save_mode') else None,
        )

        payload_b64 = convert.str2b64str(common.to_str(configure))

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

    @limiter.svrun_check_limit
    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))

            if configure['agent_type'] == 'local':
                if configure['llm'] is not None and configure['llm'] not in self.list_llms(data_dir):
                    msg = dict(warn=f"Specified LLM configuration '{configure['llm']}' not found.")
                    redis_cli.rpush(reskey, msg)
                    return self.RESP_WARN
                if configure['mcpservers'] is not None:
                    entries = self.list_mcvpservers(data_dir)
                    configure['mcpservers'] = list(set(configure['mcpservers']))
                    for m in configure['mcpservers']:
                        if m not in entries:
                            msg = dict(warn=f"Specified MCP server configuration '{m}' not found.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN
                if configure['subagents'] is not None:
                    configure['subagents'] = list(set(configure['subagents']))
                    entries = self.list_agents(data_dir)
                    for a in configure['subagents']:
                        if a not in entries:
                            msg = dict(warn=f"Specified subagent configuration '{a}' not found.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN
                        if a == configure['agent_name']:
                            msg = dict(warn=f"An agent cannot include itself as a subagent.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN
                if configure.get('skill_names', None) is not None:
                    configure['skill_names'] = list(set(configure['skill_names']))
                    entries = self.list_skills(data_dir)
                    for s in configure['skill_names']:
                        if s not in entries:
                            msg = dict(warn=f"Specified skill '{s}' not found.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN

            name = configure.get('agent_name')
            configure_path = data_dir / ".agent" / f"agent-{name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            chk, msg = self.check_save_mode(name, configure, configure_path)
            if not chk:
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"Agent configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def svrun_registrations(self, data_dir, logger, opt, msg):
        agent_dir = data_dir / '.agent'
        paths = agent_dir.glob(f"agent-*.json")
        count = len(list(paths))
        return count

    def init_test(self) -> None:
        """
        テスト用の初期化処理を行います
        """
        app_obj = self.appcls.getInstance(appcls=self.appcls, ver=self.ver)
        app_obj.main(args_list=[
            "-m", "llm", "-c", "save",
            "--llmname", "default_value",
            "--llmprov", "azureopenai",
        ])
        app_obj.main(args_list=[
            "-m", "llm", "-c", "save",
            "--llmname", "enabled_value",
            "--llmprov", "azureopenai",
        ])

    def cleaning_test(self) -> None:
        """
        テスト用のクリーンアップ処理を行います
        """
        app_obj = self.appcls.getInstance(appcls=self.appcls, ver=self.ver)
        app_obj.main(args_list=[
            "-m", "llm", "-c", "del",
            "--llmname", "default_value",
        ])
        app_obj.main(args_list=[
            "-m", "llm", "-c", "del",
            "--llmname", "enabled_value",
        ])
