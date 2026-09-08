"""
危険な文字シーケンス検知プラグイン

SQL コメント、ヌルバイト、16進数エスケープなどの危険な文字パターンを検知します。
"""

import re
import logging
from typing import Optional
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.plugins.base_plugin import BasePlugin


class DangerousSequencePlugin(BasePlugin):
    """危険な文字シーケンスを検知して無害化するプラグイン"""

    PATTERNS = [
        (r"(?i)(--\s+|#\s+|;)", lambda m: " "),  # SQL コメント・コマンド区切り → スペース
        (r"(\x00|\x1a)", lambda m: ""),           # ヌルバイト・ファイル終端 → 削除
        (r"(\\x[0-9a-f]{2})", lambda m: "[hex]"),  # 16進数エスケープ → テキスト化
    ]

    def __init__(self, logger: logging.Logger):
        super().__init__(name='dangerous_sequence')
        self.logger = logger

    def sanitize_text(self, text: str) -> str:
        """指定されたテキストを危険な文字シーケンスから無害化"""
        sanitized_text = text
        for pattern, replacement in self.PATTERNS:
            try:
                if re.search(pattern, sanitized_text):
                    matches = re.findall(pattern, sanitized_text)
                    self.logger.warning(
                        f"Dangerous sequences detected and sanitized: {matches}"
                    )
                    sanitized_text = re.sub(pattern, replacement, sanitized_text)
            except re.error:
                continue
        return sanitized_text

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """ユーザーメッセージをチェックして危険な文字シーケンスを無害化"""
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
        """イベントをチェックして危険な文字シーケンスを無害化"""
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
