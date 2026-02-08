from cmdbox.app import common, client, feature, options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import logging
import json
import re


class AgentBase(feature.ResultEdgeFeature):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)

    def load_conf(self, runner_name:str, data_dir:Path, logger:logging.Logger):
        runner_conf_path = data_dir / ".agent" / f"runner-{runner_name}.json"
        if not runner_conf_path.exists():
            raise FileNotFoundError(f"Specified runner configuration '{runner_name}' not found on server at '{str(runner_conf_path)}'.")
        with runner_conf_path.open('r', encoding='utf-8') as f:
            runner_conf = json.load(f)

        agent_conf = self._load_agent_config(data_dir, runner_conf['agent'])
        if agent_conf.get('llm', None) is not None:
            llm_conf = self._load_llm_config(data_dir, agent_conf['llm'])
        else:
            llm_conf = {}

        if agent_conf.get('mcpservers', None) is not None:
            mcpsv_confs = self._load_mcpsv_config(data_dir, agent_conf['mcpservers'])
        else:
            mcpsv_confs = []

        memory_conf = self._load_memory_config(data_dir, runner_conf['memory'])
        if memory_conf.get('llm', None) is not None:
            memory_llm_conf = self._load_llm_config(data_dir, memory_conf['llm'])
        else:
            memory_llm_conf = {}

        if memory_conf.get('embed', None) is not None:
            memory_embed_conf = self._load_embed_config(data_dir, memory_conf['embed'])
        else:
            memory_embed_conf = {}

        return runner_conf, agent_conf, llm_conf, memory_conf, memory_llm_conf, memory_embed_conf, mcpsv_confs

    def _load_agent_config(self, data_dir:Path, agent_name:str) -> Dict[str, Any]:
        agent_conf_path = data_dir / ".agent" / f"agent-{agent_name}.json"
        if not agent_conf_path.exists():
            raise FileNotFoundError(f"Specified agent configuration '{agent_name}' not found on server at '{str(agent_conf_path)}'.")
        with agent_conf_path.open('r', encoding='utf-8') as f:
            agent_conf = json.load(f)
        return agent_conf

    def _load_llm_config(self, data_dir:Path, llm_name:str) -> Dict[str, Any]:
        llm_conf_path = data_dir / ".agent" / f"llm-{llm_name}.json"
        if not llm_conf_path.exists():
            raise FileNotFoundError(f"Specified llm configuration '{llm_name}' not found on server at '{str(llm_conf_path)}'.")
        with llm_conf_path.open('r', encoding='utf-8') as f:
            llm_conf = json.load(f)
        return llm_conf

    def _load_mcpsv_config(self, data_dir:Path, mcpservers:List[str]) -> List[Dict[str, Any]]:
        mcpsv_confs = []
        if isinstance(mcpservers, list):
            for mcpsv_name in mcpservers:
                mcpsv_conf_path = data_dir / ".agent" / f"mcpsv-{mcpsv_name}.json"
                if not mcpsv_conf_path.exists():
                    raise FileNotFoundError(f"Specified MCP server configuration '{mcpsv_name}' not found on server at '{str(mcpsv_conf_path)}'.")
                with mcpsv_conf_path.open('r', encoding='utf-8') as f:
                    mcpsv_conf = json.load(f)
                    mcpsv_confs.append(mcpsv_conf)
        return mcpsv_confs

    def _load_embed_config(self, data_dir:Path, embed_name:str) -> Dict[str, Any]:
        embed_conf_path = data_dir / ".agent" / f"embed-{embed_name}.json"
        if not embed_conf_path.exists():
            raise FileNotFoundError(f"Specified embed configuration '{embed_name}' not found on server at '{str(embed_conf_path)}'.")
        with embed_conf_path.open('r', encoding='utf-8') as f:
            embed_conf = json.load(f)
        return embed_conf

    def _load_memory_config(self, data_dir:Path, memory_name:str) -> Dict[str, Any]:
        memory_conf_path = data_dir / ".agent" / f"memory-{memory_name}.json"
        if not memory_conf_path.exists():
            raise FileNotFoundError(f"Specified memory configuration '{memory_name}' not found on server at '{str(memory_conf_path)}'.")
        with memory_conf_path.open('r', encoding='utf-8') as f:
            memory_conf = json.load(f)
        return memory_conf

    async def create_agent_session(self, session_service:Any, runner_name:str, user_name:str, session_id:str=None) -> Any:
        """
        セッションを作成します

        Args:
            session_service (BaseSessionService): セッションサービス
            runner_name (str): ランナー名
            user_name (str): ユーザー名
            session_id (str): セッションID

        Returns:
            Any: セッション
        """
        if session_id is None:
            session_id = common.random_string(32)
        try:
            session = await session_service.get_session(app_name=runner_name, user_id=user_name, session_id=session_id)
            if session is None:
                session = await session_service.create_session(app_name=runner_name, user_id=user_name, session_id=session_id)
            return session
        except NotImplementedError:
            # セッションが１件もない場合はNotImplementedErrorが発生することがある
            session = await session_service.create_session(app_name=runner_name, user_id=user_name, session_id=session_id)
            return session

    @classmethod
    def gen_msg(cls, event:Any) -> Tuple[str, bool, bool]:
        json_pattern = re.compile(r'\{.*?\}')
        msg = None
        is_func_call = False
        is_func_response = False
        if event.content and event.content.parts:
            msg = "\n".join([p.text for p in event.content.parts if p and p.text])
            calls = event.get_function_calls()
            if calls:
                is_func_call = True
                msg += '\n```json{"function_calls":'+common.to_str([dict(fn=c.name,args=c.args) for c in calls])+'}```'
            responses = event.get_function_responses()
            if responses:
                is_func_response = True
                msg += '\n```json{"function_responses":'+common.to_str([dict(fn=r.name, res=r.response) for r in responses])+'}```'
        elif event.actions and event.actions.escalate:
            msg = f"Agent escalated: {event.error_message or 'No specific message.'}"
        if msg:
            msg = json_pattern.sub(cls._replace_match, msg)
        return msg, is_func_call, is_func_response
    
    @classmethod
    def _replace_match(cls, match_obj):
        json_str = match_obj.group(0)
        try:
            data = json.loads(json_str) # ユニコード文字列をエンコード
            return json.dumps(data, ensure_ascii=False, default=common.default_json_enc)
        except json.JSONDecodeError:
            return json_str
