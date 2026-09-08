"""
Jinja2 テンプレートインジェクション検知プラグイン

Jinja2 テンプレートエンジンを対象とした SSTI（Server-Side Template Injection）パターンを検知します。
"""

import re
import logging
from typing import Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .prompt_injection_common import PromptInjectionException


class TemplateInjectionDetectionPlugin(BasePlugin):
    """Jinja2/テンプレートインジェクション攻撃を検知するプラグイン"""

    PATTERNS = [
        r"\{\{.*?__.*?\}\}",
        r"\{\{.*?self\._TemplateModule__dict__.*?\}\}",
        r"\{%.*?import.*?%\}",
        r"\{\{.*?config\.items\(\).*?\}\}",
        r"\{\{.*?request\.environ.*?\}\}",
        r"{{.*?popen.*?}}",
        r"{{.*?system.*?}}",
    ]

    def __init__(self, logger: logging.Logger):
        super().__init__(name='template_injection_detection')
        self.logger = logger

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """ユーザーメッセージをチェックして Jinja2 テンプレートインジェクションを検知"""
        message_text = None
        if user_message.parts and len(user_message.parts) > 0:
            part = user_message.parts[0]
            if hasattr(part, 'text') and part.text:
                message_text = part.text

        if message_text:
            for pattern in self.PATTERNS:
                try:
                    match = re.search(pattern, message_text, re.DOTALL)
                    if match:
                        raise PromptInjectionException(
                            f"Template injection detected: {match.group(0)[:50]}",
                            'Template Injection',
                            match.group(0)
                        )
                except re.error:
                    continue

        return None

    async def on_event_callback(self, *, invocation_context: InvocationContext, event: Event) -> Optional[Event]:
        """イベントをチェックして Jinja2 テンプレートインジェクションを検知"""
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
                            match = re.search(pattern, text, re.DOTALL)
                            if match:
                                self.logger.warning(
                                    f"Template injection detected in event response: {match.group(0)[:50]}"
                                )
                        except re.error:
                            continue
        return event
