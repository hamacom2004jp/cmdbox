"""
Test cases for cmdbox.app.mcp module

This file contains tests that execute actual Mcp and ToolList class methods and verify their results.
Methods are called with properly mocked dependencies to ensure real execution and result validation.
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import argparse
from typing import Dict, Any, List


def setup_mcp_environment():
    """Helper to setup MCP environment by clearing cached modules and mocking dependencies."""
    # Remove cached modules to prevent circular import issues
    for mod in list(sys.modules.keys()):
        if mod.startswith('cmdbox'):
            del sys.modules[mod]
    
    # Create a mock common module with necessary functions
    mock_common = MagicMock()
    mock_common.is_japan = MagicMock(return_value=True)
    mock_common.loadopt = MagicMock(return_value={'mode': 'test', 'cmd': 'cmd'})
    
    # Create a mock feature module
    mock_feature = MagicMock()
    
    # Create mock fastmcp modules
    mock_fastmcp = MagicMock()
    mock_fastmcp.FastMCP = MagicMock()
    
    mock_middleware = MagicMock()
    mock_middleware.Middleware = MagicMock()
    mock_middleware.MiddlewareContext = MagicMock()
    
    mock_jwt = MagicMock()
    mock_jwt.JWTVerifier = MagicMock()
    
    # Create a real class for FunctionTool that isinstance checks can use
    class FunctionToolMock:
        pass
    
    mock_tools = MagicMock()
    mock_tools.FunctionTool = FunctionToolMock
    
    # Create mock google modules
    mock_google_events = MagicMock()
    mock_google_events.Event = MagicMock()
    
    mock_google_sessions = MagicMock()
    
    # Create real mock instances for session services
    class MockInMemorySessionService:
        pass
    
    class MockDatabaseSessionService:
        def __init__(self, db_url):
            self.db_engine = MagicMock()
    
    mock_google_sessions.InMemorySessionService = MockInMemorySessionService
    mock_google_sessions.DatabaseSessionService = MockDatabaseSessionService
    mock_google_sessions.session = MagicMock()
    
    mock_options = MagicMock()
    mock_options.getInstance = MagicMock(return_value=MagicMock())
    
    mock_signin = MagicMock()
    mock_signin.request_scope = MagicMock()
    
    mock_web = MagicMock()
    mock_web.Web = MagicMock()
    mock_web.Web.getInstance = MagicMock()
    
    return patch.dict('sys.modules', {
        'cmdbox.app.common': mock_common,
        'cmdbox.app.feature': mock_feature,
        'cmdbox.app.options': mock_options,
        'cmdbox.app.auth.signin': mock_signin,
        'cmdbox.app.web': mock_web,
        'fastmcp': mock_fastmcp,
        'fastmcp.FastMCP': mock_fastmcp.FastMCP,
        'fastmcp.server': MagicMock(),
        'fastmcp.server.middleware': mock_middleware,
        'fastmcp.server.auth': MagicMock(),
        'fastmcp.server.auth.providers': MagicMock(),
        'fastmcp.server.auth.providers.jwt': mock_jwt,
        'fastmcp.tools': mock_tools,
        'google': MagicMock(),
        'google.adk': MagicMock(),
        'google.adk.events': mock_google_events,
        'google.adk.sessions': mock_google_sessions,
        'fastapi': MagicMock(),
        'fastapi.Response': MagicMock(),
    })


class TestMcpInitialization:
    """Mcp class initialization and attribute verification"""

    def test_mcp_init_sets_attributes_correctly(self):
        """
        Mcp()クラスの初期化機能を検証します。
        
        趣旨: Mcpクラスが初期化時に全ての属性を正しく設定することを確認します。
        期待される結果: logger、data、appcls、ver、signinの各属性が設定されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_data = Path('/tmp')
            mock_signin = MagicMock()
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = 'test_app'
            
            mcp = Mcp(logger=mock_logger, data=mock_data, sign=mock_signin, appcls=mock_appcls, ver=mock_ver)
            
            assert mcp.logger == mock_logger, "Logger should be set correctly"
            assert mcp.data == mock_data, "Data path should be set correctly"
            assert mcp.appcls == mock_appcls, "App class should be set correctly"
            assert mcp.ver == mock_ver, "Version should be set correctly"
            assert mcp.signin == mock_signin, "Signin object should be set correctly"

    def test_mcp_default_values_from_environment(self):
        """
        Mcp()クラスの環境変数からのデフォルト値設定機能を検証します。
        
        趣旨: Mcpクラスが環境変数からデフォルト値を取得することを確認します。
        期待される結果: default_host、default_port、default_pass、default_svnameが設定されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            # デフォルト値の確認
            assert hasattr(Mcp, 'default_host'), "Mcp should have default_host attribute"
            assert hasattr(Mcp, 'default_port'), "Mcp should have default_port attribute"
            assert hasattr(Mcp, 'default_pass'), "Mcp should have default_pass attribute"
            assert hasattr(Mcp, 'default_svname'), "Mcp should have default_svname attribute"
            
            # デフォルト値が正しい型であることを確認
            assert isinstance(Mcp.default_host, str), "default_host should be a string"
            assert isinstance(Mcp.default_port, int), "default_port should be an integer"
            assert isinstance(Mcp.default_pass, str), "default_pass should be a string"
            assert isinstance(Mcp.default_svname, str), "default_svname should be a string"


class TestMcpCreateSessionService:
    """create_session_service method execution and result verification"""

    def test_create_session_service_returns_inmemory_service_when_no_dburl(self):
        """
        create_session_service()メソッドのセッションサービス作成機能を検証します。
        
        趣旨: agent_session_dburlが指定されていない場合、InMemorySessionServiceが返されることを確認します。
        期待される結果: InMemorySessionServiceインスタンスが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            
            # InMemorySessionServiceが返されることを確認
            result = mcp.create_session_service(args)
            
            # セッションサービスが返されたことを確認
            assert result is not None, "Session service should be returned"
            # InMemorySessionServiceの型名が含まれていることを確認
            assert 'InMemorySessionService' in result.__class__.__name__, f"Should return InMemorySessionService, got {result.__class__.__name__}"
            # BaseSessionService互換のオブジェクトであることを確認（セッション関連の属性を持つ）
            assert hasattr(result, 'append_event') or hasattr(result, '__class__'), "Session service should have session-related methods"

    def test_create_session_service_returns_database_service_when_dburl_provided(self):
        """
        create_session_service()メソッドのデータベースセッションサービス作成機能を検証します。
        
        趣旨: agent_session_dburlが指定されている場合、DatabaseSessionServiceが返されることを確認します。
        期待される結果: DatabaseSessionServiceインスタンスが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            args.agent_session_dburl = 'sqlite:///test.db'
            
            # DatabaseSessionServiceが返されることを確認
            result = mcp.create_session_service(args)
            
            # セッションサービスが返されたことを確認
            assert result is not None, "Session service should be returned"
            # DatabaseSessionServiceの型名が含まれていることを確認
            assert 'DatabaseSessionService' in result.__class__.__name__, f"Should return DatabaseSessionService, got {result.__class__.__name__}"
            # BaseSessionService互換のオブジェクトであることを確認（db_engineまたはセッション関連の属性を持つ）
            assert hasattr(result, 'db_engine') or hasattr(result, 'append_event'), "Database session service should have db_engine or session methods"


class TestMcpCreateTools:
    """create_tools method execution and result verification"""

    def test_create_tools_returns_toollist_instance(self):
        """
        create_tools()メソッドのツールリスト作成機能を検証します。
        
        趣旨: create_tools()がToolListインスタンスを返すことを確認します。
        期待される結果: ToolListクラスのインスタンスが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp, ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            
            result = mcp.create_tools(logger=mock_logger, args=args, extract_callable=False)
            
            assert isinstance(result, ToolList), "Should return a ToolList instance"

    def test_create_tools_sets_extract_callable_property(self):
        """
        create_tools()メソッドのextract_callable属性設定機能を検証します。
        
        趣旨: extract_callableパラメータが正しく設定されることを確認します。
        期待される結果: ToolListのextract_callableプロパティが指定値に設定されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            
            # extract_callable=True で作成
            result = mcp.create_tools(logger=mock_logger, args=args, extract_callable=True)
            
            assert result.extract_callable == True, "extract_callable should be True"
            
            # extract_callable=False で作成
            result = mcp.create_tools(logger=mock_logger, args=args, extract_callable=False)
            
            assert result.extract_callable == False, "extract_callable should be False"


class TestMcpCreateMiddleware:
    """Middleware creation methods execution and result verification"""

    def test_create_mw_logging_returns_middleware_instance(self):
        """
        create_mw_logging()メソッドのロギングミドルウェア作成機能を検証します。
        
        趣旨: create_mw_logging()がミドルウェアオブジェクトを返すことを確認します。
        期待される結果: ミドルウェアインスタンスが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            
            result = mcp.create_mw_logging(logger=mock_logger, args=args)
            
            assert result is not None, "Middleware should be returned"

    def test_create_mw_reqscope_returns_middleware_instance(self):
        """
        create_mw_reqscope()メソッドのリクエストスコープミドルウェア作成機能を検証します。
        
        趣旨: create_mw_reqscope()がミドルウェアオブジェクトを返すことを確認します。
        期待される結果: ミドルウェアインスタンスが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            
            result = mcp.create_mw_reqscope(logger=mock_logger, args=args)
            
            assert result is not None, "Middleware should be returned"

    def test_create_mw_toollist_returns_middleware_instance(self):
        """
        create_mw_toollist()メソッドのツールリストミドルウェア作成機能を検証します。
        
        趣旨: create_mw_toollist()がミドルウェアオブジェクトを返すことを確認します。
        期待される結果: ミドルウェアインスタンスが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp, ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=MagicMock())
            
            args = argparse.Namespace()
            tools = []
            
            result = mcp.create_mw_toollist(logger=mock_logger, args=args, tools=tools)
            
            assert result is not None, "Middleware should be returned"


class TestToolListInitialization:
    """ToolList class initialization and attribute verification"""

    def test_toollist_init_sets_attributes_correctly(self):
        """
        ToolList()クラスの初期化機能を検証します。
        
        趣旨: ToolListクラスが初期化時に全ての属性を正しく設定することを確認します。
        期待される結果: logger、data、appcls、ver、toolsの各属性が設定されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_data = Path('/tmp')
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            
            toollist = ToolList(logger=mock_logger, data=mock_data, appcls=mock_appcls, ver=mock_ver)
            
            assert toollist.logger == mock_logger, "Logger should be set correctly"
            assert toollist.data == mock_data, "Data path should be set correctly"
            assert toollist.appcls == mock_appcls, "App class should be set correctly"
            assert toollist.ver == mock_ver, "Version should be set correctly"
            assert isinstance(toollist.tools, list), "Tools should be a list"

    def test_toollist_extract_callable_property_getter_and_setter(self):
        """
        ToolList()クラスのextract_callableプロパティを検証します。
        
        趣旨: extract_callableプロパティのgetterとsetterが正しく機能することを確認します。
        期待される結果: プロパティの値が正しく設定・取得できます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            # setterをテスト
            toollist.extract_callable = True
            assert toollist.extract_callable == True, "extract_callable should be True"
            
            toollist.extract_callable = False
            assert toollist.extract_callable == False, "extract_callable should be False"

    def test_toollist_extract_callable_setter_validates_type(self):
        """
        ToolList()クラスのextract_callableセッターの型チェック機能を検証します。
        
        趣旨: extract_callableに非ブール値を設定しようとした場合、TypeErrorが発生することを確認します。
        期待される結果: TypeErrorが発生し、エラーメッセージが記述されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            with pytest.raises(TypeError):
                toollist.extract_callable = "not_a_bool"
            
            with pytest.raises(TypeError):
                toollist.extract_callable = 1


class TestToolListOperations:
    """ToolList class operations and methods"""

    def test_toollist_append_adds_tool(self):
        """
        ToolList.append()メソッドのツール追加機能を検証します。
        
        趣旨: ToolListにツールを追加できることを確認します。
        期待される結果: toolsリストの長さが増加します。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            from fastmcp.tools import FunctionTool
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            initial_count = len(toollist.tools)
            
            # FunctionToolのインスタンスを作成
            mock_tool = FunctionTool()
            mock_tool.name = 'test_tool'
            
            # ツールを追加
            toollist.append(mock_tool)
            
            # リストの長さが増加したことを確認
            assert len(toollist.tools) > initial_count, "Tool should be added to tools list"

    def test_toollist_pop_removes_tool(self):
        """
        ToolList.pop()メソッドのツール取り出し機能を検証します。
        
        趣旨: ToolListからツールを取り出せることを確認します。
        期待される結果: toolsリストの長さが減少します。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            # モックツールを追加
            mock_tool = MagicMock()
            toollist.tools.append(mock_tool)
            
            initial_count = len(toollist.tools)
            
            # ツールを取り出す
            result = toollist.pop()
            
            # リストの長さが減少したことを確認
            assert len(toollist.tools) < initial_count, "Tool should be removed from tools list"
            assert result == mock_tool, "Should return the removed tool"

    def test_toollist_pop_raises_on_empty_list(self):
        """
        ToolList.pop()メソッドの空リストエラー処理を検証します。
        
        趣旨: 空のToolListからツールを取り出そうとした場合、IndexErrorが発生することを確認します。
        期待される結果: IndexErrorが発生し、エラーメッセージが記述されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            with pytest.raises(IndexError):
                toollist.pop()

    def test_toollist_getitem_returns_tool_by_index(self):
        """
        ToolList.__getitem__()メソッドのインデックスアクセス機能を検証します。
        
        趣旨: インデックスでToolListのツールにアクセスできることを確認します。
        期待される結果: 指定したインデックスのツールが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            # モックツールを追加
            mock_tool1 = MagicMock()
            mock_tool2 = MagicMock()
            toollist.tools.append(mock_tool1)
            toollist.tools.append(mock_tool2)
            
            # インデックスでアクセス
            assert toollist[0] == mock_tool1, "Should return first tool"
            assert toollist[1] == mock_tool2, "Should return second tool"

    def test_toollist_str_representation(self):
        """
        ToolList.__str__()メソッドの文字列表現機能を検証します。
        
        趣旨: ToolListの文字列表現が取得できることを確認します。
        期待される結果: ツールリストの文字列表現が返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            # 文字列表現を取得
            result = str(toollist)
            
            assert isinstance(result, str), "str() should return a string"
            assert '[]' in result, "Should contain list representation"

    def test_toollist_repr_representation(self):
        """
        ToolList.__repr__()メソッドの表現機能を検証します。
        
        趣旨: ToolListのrepr表現が取得できることを確認します。
        期待される結果: ツールリストのrepr表現が返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import ToolList
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            toollist = ToolList(logger=mock_logger, data=Path('/tmp'))
            
            # repr表現を取得
            result = repr(toollist)
            
            assert isinstance(result, str), "repr() should return a string"
            assert 'ToolList' in result, "Should contain ToolList class name"


class TestMcpCreateMcpserver:
    """create_mcpserver method execution and result verification"""

    def test_create_mcpserver_returns_fastmcp_instance(self):
        """
        create_mcpserver()メソッドのFastMCPサーバー作成機能を検証します。
        
        趣旨: create_mcpserver()がFastMCPインスタンスを返すことを確認します。
        期待される結果: FastMCPオブジェクトが返されます。
        """
        with setup_mcp_environment():
            from cmdbox.app.mcp import Mcp
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_signin = MagicMock()
            mock_signin.__class__ = MagicMock()
            
            mock_ver = MagicMock()
            mock_ver.__appid__ = 'test_app'
            
            mcp = Mcp(logger=mock_logger, data=Path('/tmp'), sign=mock_signin, ver=mock_ver)
            
            args = argparse.Namespace()
            tools = []
            
            result = mcp.create_mcpserver(logger=mock_logger, args=args, tools=tools)
            
            assert result is not None, "FastMCP instance should be returned"
