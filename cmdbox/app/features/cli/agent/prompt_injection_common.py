from typing import Optional, Dict, Any

class PromptInjectionException(Exception):
    """プロンプトインジェクション検知時の例外"""

    def __init__(
        self,
        message: str,
        pattern_type: Optional[str] = None,
        matched_content: Optional[str] = None,
    ):
        self.pattern_type = pattern_type
        self.matched_content = matched_content
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """例外情報を辞書形式で取得"""
        return {
            'error': 'Prompt Injection Detected',
            'pattern_type': self.pattern_type,
            'message': str(self),
            'matched_content': (
                self.matched_content[:50] if self.matched_content else None
            ),
        }
