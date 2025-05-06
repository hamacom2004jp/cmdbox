from cmdbox.app import common, feature
from cmdbox.app.options import Options
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from pathlib import Path
from typing import Any, Dict, Tuple, List, Union
import argparse
import asyncio
import logging
import json


class AgentStart(feature.ResultEdgeFeature):

    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'agent'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'start'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="-",
            discription_en="-",
            choice=[
                dict(opt="llmprov", type=Options.T_STR, default="azureopenai", required=False, multi=False, hide=False,
                     choice=["azureopenai", "openai", "vertexai", "ollama"],
                     discription_ja="llmのプロバイダを指定します。",
                     discription_en="Specify llm provider.",
                     choice_show=dict(azureopenai=["llmapikey", "llmendpoint", "llmmodel", "llmapiversion"],
                                      openai=["llmapikey", "llmendpoint", "llmmodel"],
                                      vertexai=["llmprojectid", "llmsvaccountfile", "llmlocation", "llmmodel", "llmseed", "llmtemperature"],
                                      ollama=["llmendpoint", "llmmodel", "llmtemperature"],),
                     ),
                dict(opt="llmprojectid", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのプロジェクトIDを指定します。",
                     discription_en="Specify the project ID for llm's provider connection."),
                dict(opt="llmsvaccountfile", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのサービスアカウントファイルを指定します。",
                     discription_en="Specifies the service account file for llm's provider connection."),
                dict(opt="llmlocation", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのロケーションを指定します。",
                     discription_en="Specifies the location for llm provider connections."),
                dict(opt="llmapikey", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのAPIキーを指定します。",
                     discription_en="Specify API key for llm provider connection."),
                dict(opt="llmapiversion", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのAPIバージョンを指定します。",
                     discription_en="Specifies the API version for llm provider connections."),
                dict(opt="llmendpoint", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのエンドポイントを指定します。",
                     discription_en="Specifies the endpoint for llm provider connections."),
                dict(opt="llmmodel", type=Options.T_STR, default="text-multilingual-embedding-002", required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmの埋め込みモデルを指定します。",
                     discription_en="Specifies the embedding model for llm."),
                dict(opt="llmseed", type=Options.T_INT, default=13, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmの埋め込みモデルを使用するときのシード値を指定します。",
                     discription_en="Specifies the seed value when using llm's embedded model."),
                dict(opt="llmtemperature", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmの埋め込みモデルを使用するときのtemperatureを指定します。",
                     discription_en="Specifies the temperature when using llm's embedded model."),
            ])

    def apprun(self, logger, args, tm, pf):
        vertex_credentials = dict()
        with open("inspectionbox-hama-4d7b588f29ab.json", "r") as f:
            vertex_credentials = json.load(f)
        weather_agent = Agent(
            name="weather_agent_v1",
            model=LiteLlm(
                model="gemini-2.0-flash", # Geminiの文字列またはLiteLlmオブジェクト。
                vertex_credentials=vertex_credentials,
                vertex_location="us-central1",),
            description="特定の都市の気象情報を提供",
            instruction="あなたは親切な気象アシスタントだ。"
                        "ユーザーが特定の都市の天気を尋ねたとき、get_weather'ツールを使って情報を検索する。"
                        "ツールがエラーを返した場合は、ユーザーに丁寧に知らせること。"
                        "Iツールが成功したら、天気予報を明確に提示する。",
            tools=[AgentStart.get_weather], # 関数を直接渡す
        )
        session_service = InMemorySessionService()
        USER_ID = "user_1"
        SESSION_ID = "session_001"
        session = session_service.create_session(
            app_name=self.ver.__appid__,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        runner = Runner(
            agent=weather_agent,
            app_name=self.ver.__appid__,
            session_service=session_service
        )
        async def call_agent_async(query:str, runner:Runner, user_id, session_id):
            content = types.Content(role='user', parts=[types.Part(text=query)])

            final_response_text = "Agent did not produce a final response." # Default

            # イベントを繰り返し、最終的な答えを見つける。
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                logger.debug(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate:
                        final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                    break
            logger.debug(f"<<< Agent Response: {final_response_text}")

        async def run_conversation():
            await call_agent_async("Londonの天気はどうですか？",
                                            runner=runner,
                                            user_id=USER_ID,
                                            session_id=SESSION_ID)

            await call_agent_async("Parisはどうですか？",
                                            runner=runner,
                                            user_id=USER_ID,
                                            session_id=SESSION_ID) # Expecting the tool's error message

            await call_agent_async("New Yorkの天気を教えて",
                                            runner=runner,
                                            user_id=USER_ID,
                                            session_id=SESSION_ID)
        asyncio.run(run_conversation())
        return 0, dict(status="success", message="Agent conversation completed."), None


    @staticmethod
    def get_weather(city: str) -> dict:
        city_normalized = city.lower().replace(" ", "")
        mock_weather_db = {
            "newyork": {"status": "success", "report": "ニューヨークの天候は晴れ、気温は25℃。"},
            "london": {"status": "success", "report": "ロンドンは曇り、気温は15℃。"},
            "tokyo": {"status": "success", "report": "東京は小雨が降り、気温は18度。"},
        }
        if city_normalized in mock_weather_db:
            return mock_weather_db[city_normalized]
        else:
            return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
