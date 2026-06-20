from cmdbox.app import common, client, feature, options
from cmdbox.app.features.cli import cmdbox_llm_chat, cmdbox_datasource_load
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import logging
import json
import sys
import re


class AgentBase(feature.ResultEdgeFeature):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)
        self.llm_chat = cmdbox_llm_chat.LLMChat(appcls, ver, language=language)
        self.ds_load = cmdbox_datasource_load.DatasourceLoad(appcls, ver, language=language)

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
        
        if runner_conf.get('session_datasource', None) is not None:
            ds_conf = self._load_ds_config(data_dir, runner_conf['session_datasource'])
        else:
            ds_conf = {}
        if 'db_fullpath' not in ds_conf or not ds_conf['db_fullpath']:
            if 'db_path' in ds_conf and ds_conf['db_path']:
                db_path = str(ds_conf['db_path'])
                db_path = db_path.replace("\\","/").replace("//","/") if db_path else None
                db_path = db_path[1:] if db_path and db_path.startswith('/') else db_path
                ds_conf['db_fullpath'] = str((data_dir / db_path).resolve()) if db_path else None

        return runner_conf, agent_conf, llm_conf, mcpsv_confs, ds_conf

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

    def _load_ds_config(self, data_dir:Path, dsname:str) -> Dict[str, Any]:
        ds_conf = self.ds_load.load_datasource(data_dir, dsname)
        return ds_conf

    def create_session_service(self, logger:logging.Logger, ds_conf:Dict[str, Any]) -> Any:
        """
        セッションサービスを作成します

        Args:
            logger (logging.Logger): ロガー
            ds_conf (Dict[str, Any]): データソースの設定

        Returns:
            BaseSessionService: セッションサービス
        """
        if ds_conf.get('dbtype') == 'sqlite':
            if sys.platform == 'win32':
                uri = Path(ds_conf['db_fullpath']).as_uri()
                agent_session_dburl = f"sqlite+aiosqlite:{uri.replace('file:///', '///')}"
            else:
                db_path = Path(ds_conf['db_fullpath']).resolve().as_posix()
                agent_session_dburl = f"sqlite+aiosqlite:////{db_path.lstrip('/')}"
        elif ds_conf.get('dbtype') == 'postgresql':
            agent_session_dburl = f"postgresql+psycopg://{ds_conf['pguser']}:{ds_conf['pgpass']}@{ds_conf['pghost']}:{ds_conf['pgport']}/{ds_conf['pgdbname']}"
        else:
            agent_session_dburl = None
        from google.adk.sessions import InMemorySessionService
        from google.adk.sessions.database_session_service import DatabaseSessionService
        if agent_session_dburl is not None:
            logger.info(f"Using DatabaseSessionService: {agent_session_dburl}")
            dss = DatabaseSessionService(db_url=agent_session_dburl)
            return dss
        else:
            logger.info(f"Using InMemorySessionService")
            return InMemorySessionService()

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
    def gen_msg(cls, event:Any) -> Tuple[str, bool, bool, bool]:
        json_pattern = re.compile(r'\{.*?\}')
        msg = None
        is_func_call = False
        is_func_response = False
        is_final_response = False
        if event.content and event.content.parts:
            msg = "\n".join([p.text for p in event.content.parts if p and p.text])
            calls = event.get_function_calls()
            if calls:
                is_func_call = True
                msg += '\n```json{"function_calls":'+common.to_str([dict(fn=c.name,args=c.args) for c in calls])+'}```'
            responses = event.get_function_responses()
            if responses:
                is_func_response = True
                structuredContent = []
                for r in responses:
                    row = dict()
                    structuredContent.append(row)
                    if r.response:
                        row['res'] = r.response.get('structuredContent', 'No Response.')
                    row['fn'] = r.name
                msg += '\n```json{"function_responses":'+common.to_str(structuredContent)+'}```'
            is_final_response = event.is_final_response()
        elif event.actions and event.actions.escalate:
            msg = f"Agent escalated: {event.error_message or 'No specific message.'}"
        if msg:
            msg = json_pattern.sub(cls._replace_match, msg)
        return msg, is_func_call, is_func_response, is_final_response
    
    @classmethod
    def _replace_match(cls, match_obj):
        json_str = match_obj.group(0)
        try:
            data = json.loads(json_str) # ユニコード文字列をエンコード
            return json.dumps(data, ensure_ascii=False, default=common.default_json_enc)
        except json.JSONDecodeError:
            return json_str
