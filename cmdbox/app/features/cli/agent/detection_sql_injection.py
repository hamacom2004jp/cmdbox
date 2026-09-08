"""
SQL インジェクション検知プラグイン

SQL インジェクション攻撃パターンを検知し、PromptInjectionException を発生させます。
"""

import re
import logging
from typing import Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .prompt_injection_common import PromptInjectionException


class SQLInjectionDetectionPlugin(BasePlugin):
    """SQL インジェクション攻撃を検知するプラグイン"""

    PATTERNS = [
        r"(?i)\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*?(?:from|into|values|set|where|;)",
        r"(?i)('\s*or\s*'|'\s*or\s*1\s*=\s*1|--\s*|;.*?(union|select|insert))",
        r"(?i)(\bor\b\s*1\s*=\s*1|\bor\b\s*true\b)",
        r"(?i)(xp_cmdshell|exec\s+sp_|sp_executesql)",
        r"(?i)(sqlmap|' and '1'='1)",
    ]

    def __init__(self, logger: logging.Logger):
        super().__init__(name='sql_injection_detection')
        self.logger = logger

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """ユーザーメッセージをチェックして SQL インジェクションを検知"""
        message_text = None
        if user_message.parts and len(user_message.parts) > 0:
            part = user_message.parts[0]
            if hasattr(part, 'text') and part.text:
                message_text = part.text

        if message_text:
            for pattern in self.PATTERNS:
                try:
                    match = re.search(pattern, message_text)
                    if match:
                        raise PromptInjectionException(
                            f"SQL injection detected: {match.group(0)[:50]}",
                            'SQL Injection',
                            match.group(0)
                        )
                except re.error:
                    continue

        return None

    async def on_event_callback(self, *, invocation_context: InvocationContext, event: Event) -> Optional[Event]:
        """イベントをチェックして SQL インジェクションを検知"""
        # イベントのコンテンツをチェック
        if hasattr(event, 'content') and event.content:
            content = event.content
            # コンテンツがテキストを持つか確認
            if hasattr(content, 'parts') and content.parts and len(content.parts) > 0:
                part = content.parts[0]
                if hasattr(part, 'text') and part.text:
                    text = part.text
                    # パターンマッチングを実行
                    for pattern in self.PATTERNS:
                        try:
                            match = re.search(pattern, text)
                            if match:
                                self.logger.warning(
                                    f"SQL injection detected in event response: {match.group(0)[:50]}"
                                )
                        except re.error:
                            continue
        return event
