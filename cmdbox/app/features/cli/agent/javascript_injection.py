"""
JavaScript/HTML インジェクション無害化プラグイン

XSS（クロスサイトスクリプティング）および HTML インジェクション攻撃パターンを無害化します。
"""

import re
import html
import logging
from typing import Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


class JavaScriptInjectionPlugin(BasePlugin):
    """JavaScript/HTML インジェクション攻撃を無害化するプラグイン"""

    # JavaScript 検出パターン
    JS_PATTERNS = [
        (r"javascript:", re.IGNORECASE),
        (r"on\w+\s*=\s*[\"']?.*?[\"']", re.IGNORECASE),
        (r"eval\s*\(", re.IGNORECASE),
        (r"new\s+Function\s*\(", re.IGNORECASE),
    ]

    def __init__(self, logger: logging.Logger):
        super().__init__(name='javascript_injection')
        self.logger = logger

    def sanitize_text(self, text: str) -> str:
        """指定されたテキストを JavaScript/HTML インジェクションから無害化"""
        sanitized_text = text
        dangerous_detected = False

        # JavaScript パターンの検出
        for pattern, flags in self.JS_PATTERNS:
            try:
                if re.search(pattern, sanitized_text, flags):
                    dangerous_detected = True
                    matches = re.findall(pattern, sanitized_text, flags)
                    self.logger.warning(
                        f"JavaScript injection detected: {matches}"
                    )
            except re.error:
                continue

        # HTML タグの検出（<, > が含まれている）
        if '<' in sanitized_text or '>' in sanitized_text:
            dangerous_detected = True
            self.logger.warning("HTML content detected and will be escaped")
        
        # HTML 特殊文字をエスケープして無害化
        if dangerous_detected:
            sanitized_text = html.escape(sanitized_text, quote=True)
        
        return sanitized_text

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """ユーザーメッセージをチェックして JavaScript インジェクションを無害化"""
        message_text = None
        if user_message.parts and len(user_message.parts) > 0:
            part = user_message.parts[0]
            if hasattr(part, 'text') and part.text:
                message_text = part.text

        if message_text:
            sanitized_text = self.sanitize_text(message_text)
            # メッセージが無害化された場合はテキストを更新
            if sanitized_text != message_text:
                if hasattr(user_message.parts[0], 'text'):
                    user_message.parts[0].text = sanitized_text
                self.logger.info("User message has been sanitized")

        return None

    async def on_event_callback(self, *, invocation_context: InvocationContext, event: Event) -> Optional[Event]:
        """イベントをチェックして JavaScript/HTML インジェクションを無害化"""
        # イベントのコンテンツをチェック
        if hasattr(event, 'content') and event.content:
            content = event.content
            # コンテンツがテキストを持つか確認
            if hasattr(content, 'parts') and content.parts and len(content.parts) > 0:
                part = content.parts[0]
                if hasattr(part, 'text') and part.text:
                    original_text = part.text
                    sanitized_text = self.sanitize_text(original_text)
                    # テキストが無害化された場合はイベントを更新
                    if sanitized_text != original_text:
                        if hasattr(part, 'text'):
                            part.text = sanitized_text
                        self.logger.info("Event response has been sanitized")
        return event
