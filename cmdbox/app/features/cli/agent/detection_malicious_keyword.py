"""
悪意のあるキーワード検知プラグイン

危険なキーワードやコマンドのパターンを検知します。
"""

import re
import logging
from typing import Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .prompt_injection_common import PromptInjectionException


class MaliciousKeywordDetectionPlugin(BasePlugin):
    """悪意のあるキーワードを検知するプラグイン"""

    PATTERNS = [
        r"(?i)\b(drop\s+database|truncate\s+table|exec\s+xp_|sp_oacreate)",
        r"(?i)(\bignore\b|\bby\s+pass\b|\badmin\b.*?\bpassword\b)",
        r"(?i)(union\s+all\s+select)",
    ]

    def __init__(self, logger: logging.Logger):
        super().__init__(name='malicious_keyword_detection')
        self.logger = logger

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """ユーザーメッセージをチェックして悪意のあるキーワードを検知"""
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
                            f"Malicious keyword detected: {match.group(0)[:50]}",
                            'Malicious Keywords',
                            match.group(0)
                        )
                except re.error:
                    continue

        return None

    async def on_event_callback(self, *, invocation_context: InvocationContext, event: Event) -> Optional[Event]:
        """イベントをチェックして悪意のあるキーワードを検知"""
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
                                    f"Malicious keyword detected in event response: {match.group(0)[:50]}"
                                )
                        except re.error:
                            continue
        return event
