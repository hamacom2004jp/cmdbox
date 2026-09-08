"""
プロンプトインジェクション検知パッケージ

複数の検知プラグインとユーティリティクラスを提供します。
"""

# 共通定義（常にインポート可能）
from .prompt_injection_common import PromptInjectionException

# プラグインクラス（google.adk が利用可能な環境でのみインポート）
try:
    from .detection_sql_injection import SQLInjectionDetectionPlugin
    from .javascript_injection import JavaScriptInjectionPlugin
    from .detection_template_injection import TemplateInjectionDetectionPlugin
    from .detection_malicious_keyword import MaliciousKeywordDetectionPlugin
    from .dangerous_sequence import DangerousSequencePlugin
    
    __all__ = [
        'PromptInjectionException',
        'SQLInjectionDetectionPlugin',
        'JavaScriptInjectionPlugin',
        'TemplateInjectionDetectionPlugin',
        'MaliciousKeywordDetectionPlugin',
        'DangerousSequencePlugin',
    ]
except ImportError:
    # google.adk が利用不可の場合は、共通定義のみをエクスポート
    __all__ = [
        'PromptInjectionException',
    ]
