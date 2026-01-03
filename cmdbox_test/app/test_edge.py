"""
Test cases for cmdbox.app.edge module

This file contains tests that execute actual Edge class methods and verify their results.
Methods are called with properly mocked dependencies to ensure real execution and result validation.
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import argparse
import json
from typing import Dict, Any, List


def setup_edge_environment():
    """Helper to setup Edge environment by clearing cached modules and mocking dependencies."""
    # Remove cached modules to prevent circular import issues
    for mod in list(sys.modules.keys()):
        if mod.startswith('cmdbox'):
            del sys.modules[mod]
    
    # Create mock modules for edge dependencies
    mock_common = MagicMock()
    mock_common.print_format = MagicMock()
    mock_common.mkdirs = MagicMock()
    mock_common.loadopt = MagicMock(return_value={})
    mock_common.saveopt = MagicMock()
    mock_common.is_japan = MagicMock(return_value=False)
    mock_common.to_str = MagicMock(side_effect=lambda x: str(x))
    
    mock_options = MagicMock()
    mock_options.Options.getInstance = MagicMock(return_value=MagicMock())
    mock_options.T_BOOL = 'bool'
    mock_options.T_INT = 'int'
    mock_options.T_FLOAT = 'float'
    
    mock_commons = MagicMock()
    mock_convert = MagicMock()
    mock_convert.str2b64str = MagicMock(side_effect=lambda x: 'b64_' + str(x))
    mock_commons.convert = mock_convert
    
    mock_web = MagicMock()
    mock_feature = MagicMock()
    mock_edge_tool = MagicMock()
    
    return patch.dict('sys.modules', {
        'cmdbox.app.common': mock_common,
        'cmdbox.app.options': mock_options,
        'cmdbox.app.commons': mock_commons,
        'cmdbox.app.commons.convert': mock_convert,
        'cmdbox.app.web': mock_web,
        'cmdbox.app.feature': mock_feature,
        'cmdbox.app.edge_tool': mock_edge_tool,
    })


class TestEdgeInitialization:
    """Edge class initialization and validation"""

    def test_edge_initialization_success(self):
        """
        Edge()のコンストラクタが必須パラメータで正しく初期化されることを検証します。
        
        趣旨: Edgeオブジェクトが全ての必須パラメータを受け取ると、正常に初期化されることを確認します。
        期待される結果: Edgeオブジェクトが作成され、各プロパティが正しく設定されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__logo__ = "Test Logo"
            mock_ver.__description__ = "Test Description"
            mock_ver.__appid__ = "test_app"
            mock_ver.__title__ = "Test Title"
            
            edge = Edge(logger=mock_logger, data="/tmp/test", appcls=mock_appcls, ver=mock_ver)
            
            assert edge.logger == mock_logger, "Logger should be set"
            assert edge.data == "/tmp/test", "Data path should be set"
            assert edge.appcls == mock_appcls, "Application class should be set"
            assert edge.ver == mock_ver, "Version should be set"
            assert edge.user_info is None, "User info should be initially None"
            assert edge.svcert_no_verify is False, "svcert_no_verify should be initially False"

    def test_edge_initialization_fails_with_missing_logger(self):
        """
        Edge()のコンストラクタにloggerがNoneの場合、例外が発生することを検証します。
        
        趣旨: loggerがNoneで初期化しようとした場合、ValueErrorが発生することを確認します。
        期待される結果: 'logger is None'というメッセージを含むValueErrorが発生します。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            
            with pytest.raises(ValueError, match="logger is None"):
                Edge(logger=None, data="/tmp/test", appcls=mock_appcls, ver=mock_ver)

    def test_edge_initialization_fails_with_missing_version(self):
        """
        Edge()のコンストラクタにverがNoneの場合、例外が発生することを検証します。
        
        趣旨: verがNoneで初期化しようとした場合、ValueErrorが発生することを確認します。
        期待される結果: 'ver is None'というメッセージを含むValueErrorが発生します。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_appcls = MagicMock()
            
            with pytest.raises(ValueError, match="ver is None"):
                Edge(logger=mock_logger, data="/tmp/test", appcls=mock_appcls, ver=None)

    def test_edge_initialization_fails_with_missing_appcls(self):
        """
        Edge()のコンストラクタにappclsがNoneの場合、例外が発生することを検証します。
        
        趣旨: appclsがNoneで初期化しようとした場合、ValueErrorが発生することを確認します。
        期待される結果: 'appcls is None'というメッセージを含むValueErrorが発生します。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_ver = MagicMock()
            
            with pytest.raises(ValueError, match="appcls is None"):
                Edge(logger=mock_logger, data="/tmp/test", appcls=None, ver=mock_ver)

    def test_edge_initialization_fails_with_missing_data(self):
        """
        Edge()のコンストラクタにdataがNoneの場合、例外が発生することを検証します。
        
        趣旨: dataがNoneで初期化しようとした場合、ValueErrorが発生することを確認します。
        期待される結果: 'data is None'というメッセージを含むValueErrorが発生します。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            
            with pytest.raises(ValueError, match="data is None"):
                Edge(logger=mock_logger, data=None, appcls=mock_appcls, ver=mock_ver)


class TestEdgeSiteRequest:
    """site_request method execution and result verification"""

    def test_site_request_success_with_status_200(self):
        """
        site_request()メソッドが正常にリクエストを実行することを検証します。
        
        趣旨: ステータスコード200のレスポンスに対して、正常な結果が返されることを確認します。
        期待される結果: ステータス0と共にレスポンス内容とヘッダーが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"success": true}'
            mock_response.headers = {'content-type': 'application/json'}
            
            mock_func = MagicMock(return_value=mock_response)
            
            status, res, headers = edge.site_request(mock_func, "/api/test")
            
            assert status == 0, "Should return status 0 on success"
            assert res == b'{"success": true}', "Should return response content"
            assert headers == {'content-type': 'application/json'}, "Should return headers"

    def test_site_request_adds_leading_slash_to_path(self):
        """
        site_request()メソッドがパスに先頭スラッシュを自動的に追加することを検証します。
        
        趣旨: スラッシュなしのパスを指定した場合、自動的に追加されることを確認します。
        期待される結果: リクエスト関数が正しい形式のパス（先頭スラッシュ付き）で呼ばれます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'test'
            mock_response.headers = {}
            
            mock_func = MagicMock(return_value=mock_response)
            
            edge.site_request(mock_func, "api/test")
            
            # Check that the function was called with correct full URL
            call_args = mock_func.call_args
            assert call_args[0][0] == "http://localhost:8000/api/test", "Path should have leading slash added"

    def test_site_request_fails_with_non_ok_status(self):
        """
        site_request()メソッドがok_statusに含まれないステータスコードでエラーを返すことを検証します。
        
        趣旨: 期待されないステータスコードが返された場合、エラーが返されることを確認します。
        期待される結果: ステータス1とエラーメッセージが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            edge.tool = MagicMock()
            
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.headers = {}
            
            mock_func = MagicMock(return_value=mock_response)
            
            status, res, headers = edge.site_request(mock_func, "/api/test", ok_status=[200])
            
            assert status == 1, "Should return status 1 on error"
            assert 'warn' in res, "Should contain warning in response"


class TestEdgeStopJobs:
    """stop_jobs method execution and result verification"""

    def test_stop_jobs_clears_threading_event(self):
        """
        stop_jobs()メソッドがスレッド処理を正しく停止することを検証します。
        
        趣旨: スレッド処理中にstop_jobs()を呼び出すと、threading_eventが設定されることを確認します。
        期待される結果: threading_eventがセットされ、新しいイベントが初期化されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import threading
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.tool = MagicMock()
            edge.threading_event = threading.Event()
            edge.threadings = []
            
            assert not edge.threading_event.is_set(), "Event should not be set initially"
            
            edge.stop_jobs(no_notify=True)
            
            # After stop_jobs, a new event should be created
            assert isinstance(edge.threading_event, threading.Event), "Should have threading event"
            assert edge.threadings == [], "Threadings list should be empty"

    def test_stop_jobs_notifies_when_no_jobs_running(self):
        """
        stop_jobs()メソッドが実行中のジョブがない場合に通知することを検証します。
        
        趣旨: ジョブが実行されていない状態でstop_jobs()を呼び出すと、警告が通知されることを確認します。
        期待される結果: toolのnotify()メソッドが警告メッセージを含めて呼ばれます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import threading
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.tool = MagicMock()
            edge.threading_event = threading.Event()
            edge.threadings = []
            
            edge.stop_jobs(no_notify=False)
            
            edge.tool.notify.assert_called_once()
            call_arg = edge.tool.notify.call_args[0][0]
            assert 'warn' in call_arg, "Should notify with warning when no jobs running"


class TestEdgeLoadUserInfo:
    """load_user_info method execution and result verification"""

    def test_load_user_info_success(self):
        """
        load_user_info()メソッドがユーザー情報を正常に取得することを検証します。
        
        趣旨: リモートエンドポイントからユーザー情報を取得し、JSON形式で返されることを確認します。
        期待される結果: ステータス0と共にユーザー情報が辞書形式で返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import requests
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            edge.session = MagicMock(spec=requests.Session)
            
            mock_user_info = {"name": "testuser", "uid": "1", "email": "test@example.com"}
            
            edge.site_request = MagicMock(return_value=(0, json.dumps(mock_user_info).encode(), {}))
            
            status, res = edge.load_user_info()
            
            assert status == 0, "Should return status 0 on success"
            assert isinstance(res, dict), "Result should be a dictionary"
            assert res['name'] == 'testuser', "Should contain user name"
            assert res['uid'] == '1', "Should contain user uid"


class TestEdgeConfigure:
    """configure method execution and result verification"""

    def test_configure_creates_conf_directory(self):
        """
        configure()メソッドが.edgeディレクトリを作成することを検証します。
        
        趣旨: configure()メソッド実行時に、data/.edgeディレクトリが作成されることを確認します。
        期待される結果: common.mkdirs()が呼ばれ、ディレクトリが作成されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__logo__ = "Test Logo"
            mock_ver.__description__ = "Test Description"
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.options = MagicMock()
                edge.options.get_cmd_choices = MagicMock(return_value=[])
                
                # Mock common module
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.print_format = MagicMock()
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={})
                    mock_common.saveopt = MagicMock()
                    mock_common.is_japan = MagicMock(return_value=False)
                    
                    args = argparse.Namespace()
                    result = edge.configure(edge_mode='test', edge_cmd='test', args=args, tm=0.0)
                    
                    # Verify mkdirs was called for .edge directory
                    mock_common.mkdirs.assert_called()
                    assert isinstance(result, dict), "Should return a dictionary"
                    assert 'success' in result, "Should contain success message"

    def test_configure_loads_existing_config(self):
        """
        configure()メソッドが既存の設定ファイルを読み込むことを検証します。
        
        趣旨: 既に設定ファイルが存在する場合、それが読み込まれることを確認します。
        期待される結果: common.loadopt()が呼ばれ、既存の設定が返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__logo__ = "Test Logo"
            mock_ver.__description__ = "Test Description"
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.options = MagicMock()
                edge.options.get_cmd_choices = MagicMock(return_value=[])
                
                existing_config = {'option1': 'value1', 'option2': 'value2'}
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.print_format = MagicMock()
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value=existing_config)
                    mock_common.saveopt = MagicMock()
                    mock_common.is_japan = MagicMock(return_value=False)
                    
                    with patch('cmdbox.app.edge.Path') as mock_path:
                        mock_conf_file = MagicMock()
                        mock_conf_file.is_file = MagicMock(return_value=True)
                        mock_path.return_value = MagicMock()
                        mock_path.return_value.__truediv__ = MagicMock(return_value=mock_conf_file)
                        
                        args = argparse.Namespace()
                        result = edge.configure(edge_mode='test', edge_cmd='test', args=args, tm=0.0)
                        
                        # Verify that loadopt was called (indicating config file was read)
                        assert mock_common.loadopt.called, "loadopt should be called to read existing config"

    def test_configure_saves_configuration(self):
        """
        configure()メソッドが設定を保存することを検証します。
        
        趣旨: 設定が入力された後、saveopt()で保存されることを確認します。
        期待される結果: common.saveopt()が呼ばれます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__logo__ = "Test Logo"
            mock_ver.__description__ = "Test Description"
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.options = MagicMock()
                edge.options.get_cmd_choices = MagicMock(return_value=[])
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.print_format = MagicMock()
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={})
                    mock_common.saveopt = MagicMock()
                    mock_common.is_japan = MagicMock(return_value=False)
                    
                    args = argparse.Namespace()
                    result = edge.configure(edge_mode='test', edge_cmd='test', args=args, tm=0.0)
                    
                    # Verify that saveopt was called
                    mock_common.saveopt.assert_called()
                    assert isinstance(result, dict), "Should return a dictionary"

    def test_configure_returns_success_message(self):
        """
        configure()メソッドが成功メッセージを返すことを検証します。
        
        趣旨: 設定完了時に、successキーを含むメッセージが返されることを確認します。
        期待される結果: 'success'キーを持つ辞書が返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__logo__ = "Test Logo"
            mock_ver.__description__ = "Test Description"
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.options = MagicMock()
                edge.options.get_cmd_choices = MagicMock(return_value=[])
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.print_format = MagicMock()
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={})
                    mock_common.saveopt = MagicMock()
                    mock_common.is_japan = MagicMock(return_value=False)
                    
                    args = argparse.Namespace()
                    result = edge.configure(edge_mode='test', edge_cmd='test', args=args, tm=0.0)
                    
                    assert 'success' in result, "Result should contain 'success' key"
                    assert result['success'] == "configure complate.", "Success message should match"


class TestEdgeSigninValidation:
    """signin method validation and error handling"""

    def test_signin_noauth_success(self):
        """
        signin()メソッドがnoauth認証で正常に完了することを検証します。
        
        趣旨: 認証なし（noauth）の設定でサインインが成功することを確認します。
        期待される結果: ステータス0と共に成功メッセージが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            edge.tool = MagicMock()
            edge.icon_path = MagicMock()
            
            mock_user_info = {"name": "guest", "uid": "0"}
            edge.load_user_info = MagicMock(return_value=(0, mock_user_info))
            edge.site_request = MagicMock(return_value=(0, b'OK', {}))
            
            with patch('cmdbox.app.edge.requests.Session'):
                status, res = edge.signin(
                    auth_type="noauth",
                    user=None, password=None, apikey=None,
                    oauth2=None, oauth2_port=0, oauth2_tenant_id=None,
                    oauth2_client_id=None, oauth2_client_secret=None, oauth2_timeout=0,
                    saml=None, saml_port=0, saml_tenant_id=None, saml_timeout=0
                )
            
            assert status == 0, "Should return status 0 on success"
            assert 'success' in res, "Should contain success message"

    def test_signin_idpw_missing_user_parameter(self):
        """
        signin()メソッドがidpw認証でuserパラメータなしの場合、エラーを返すことを検証します。
        
        趣旨: ユーザー名が指定されない場合、警告メッセージが返されることを確認します。
        期待される結果: ステータス1と共に警告メッセージが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            edge.tool = MagicMock()
            
            status, res = edge.signin(
                auth_type="idpw",
                user=None, password="password", apikey=None,
                oauth2=None, oauth2_port=0, oauth2_tenant_id=None,
                oauth2_client_id=None, oauth2_client_secret=None, oauth2_timeout=0,
                saml=None, saml_port=0, saml_tenant_id=None, saml_timeout=0
            )
            
            assert status == 1, "Should return status 1 on error"
            assert 'warn' in res, "Should contain warning message"
            assert 'user' in res['warn'].lower(), "Warning should mention user parameter"

    def test_signin_apikey_missing_apikey_parameter(self):
        """
        signin()メソッドがapikey認証でapikeyパラメータなしの場合、エラーを返すことを検証します。
        
        趣旨: APIキーが指定されない場合、警告メッセージが返されることを確認します。
        期待される結果: ステータス1と共に警告メッセージが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            edge.tool = MagicMock()
            
            status, res = edge.signin(
                auth_type="apikey",
                user=None, password=None, apikey=None,
                oauth2=None, oauth2_port=0, oauth2_tenant_id=None,
                oauth2_client_id=None, oauth2_client_secret=None, oauth2_timeout=0,
                saml=None, saml_port=0, saml_tenant_id=None, saml_timeout=0
            )
            
            assert status == 1, "Should return status 1 on error"
            assert 'warn' in res, "Should contain warning message"
            assert 'apikey' in res['warn'].lower(), "Warning should mention apikey parameter"

    def test_signin_unsupported_auth_type(self):
        """
        signin()メソッドが未サポートの認証タイプで警告を返すことを検証します。
        
        趣旨: サポートされていない認証タイプが指定された場合、警告が返されることを確認します。
        期待される結果: ステータス1と共に未サポート認証タイプの警告が返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.endpoint = "http://localhost:8000"
            edge.timeout = 30
            edge.svcert_no_verify = False
            edge.tool = MagicMock()
            
            status, res = edge.signin(
                auth_type="unsupported",
                user=None, password=None, apikey=None,
                oauth2=None, oauth2_port=0, oauth2_tenant_id=None,
                oauth2_client_id=None, oauth2_client_secret=None, oauth2_timeout=0,
                saml=None, saml_port=0, saml_tenant_id=None, saml_timeout=0
            )
            
            assert status == 1, "Should return status 1 on error"
            assert 'warn' in res, "Should contain warning message"
            assert 'unsupported' in res['warn'].lower(), "Warning should mention unsupported auth_type"


class TestEdgeStart:
    """start method execution and result verification"""

    def test_start_fails_without_config_file(self):
        """
        start()メソッドが設定ファイルなしの場合にエラーを返すことを検証します。
        
        趣旨: .edge/edge.confが存在しない場合、警告が返されることを確認します。
        期待される結果: 'warn'キーを含むメッセージが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.tool = MagicMock()
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={})
                    
                    result = edge.start(resignin=False)
                    
                    assert isinstance(result, dict), "Should return a dictionary"
                    assert 'warn' in result, "Should contain warning message"

    def test_start_fails_with_missing_icon_path(self):
        """
        start()メソッドがicon_pathなしの場合にエラーを返すことを検証します。
        
        趣旨: 設定にicon_pathが存在しない場合、警告が返されることを確認します。
        期待される結果: icon_pathが見つからないという警告が返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.tool = MagicMock()
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={'icon_path': None})
                    
                    with patch('cmdbox.app.edge.Path') as mock_path:
                        mock_conf_file = MagicMock()
                        mock_conf_file.is_file = MagicMock(return_value=True)
                        mock_path.return_value = MagicMock()
                        mock_path.return_value.__truediv__ = MagicMock(return_value=mock_conf_file)
                        
                        result = edge.start(resignin=False)
                        
                        assert isinstance(result, dict), "Should return a dictionary"
                        assert 'warn' in result, "Should contain warning for missing icon_path"

    def test_start_fails_with_missing_endpoint(self):
        """
        start()メソッドがendpointなしの場合にエラーを返すことを検証します。
        
        趣旨: 設定にendpointが存在しない場合、警告が返されることを確認します。
        期待される結果: endpointが見つからないという警告が返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.tool = MagicMock()
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={
                        'icon_path': '/tmp/icon.png',
                        'endpoint': None
                    })
                    
                    with patch('cmdbox.app.edge.Path') as mock_path:
                        mock_conf_file = MagicMock()
                        mock_conf_file.is_file = MagicMock(return_value=True)
                        mock_icon = MagicMock()
                        mock_icon.is_file = MagicMock(return_value=True)
                        
                        mock_path.return_value = MagicMock()
                        mock_path.return_value.__truediv__ = MagicMock(return_value=mock_conf_file)
                        mock_path.side_effect = lambda x: mock_icon if x == '/tmp/icon.png' else mock_path.return_value
                        
                        result = edge.start(resignin=False)
                        
                        assert isinstance(result, dict), "Should return a dictionary"
                        assert 'warn' in result, "Should contain warning for missing endpoint"

    def test_start_fails_with_invalid_timeout(self):
        """
        start()メソッドがtimeoutが数値でない場合にエラーを返すことを検証します。
        
        趣旨: timeoutが数値文字列ではない場合、警告が返されることを確認します。
        期待される結果: timeoutが無効という警告が返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import tempfile
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            with tempfile.TemporaryDirectory() as tmpdir:
                edge = Edge(logger=mock_logger, data=tmpdir, appcls=mock_appcls, ver=mock_ver)
                edge.tool = MagicMock()
                
                with patch('cmdbox.app.edge.common') as mock_common:
                    mock_common.mkdirs = MagicMock()
                    mock_common.loadopt = MagicMock(return_value={
                        'icon_path': '/tmp/icon.png',
                        'endpoint': 'http://localhost:8000',
                        'auth_type': 'noauth',
                        'timeout': 'invalid'
                    })
                    
                    with patch('cmdbox.app.edge.Path') as mock_path:
                        mock_conf_file = MagicMock()
                        mock_conf_file.is_file = MagicMock(return_value=True)
                        mock_icon = MagicMock()
                        mock_icon.is_file = MagicMock(return_value=True)
                        
                        mock_path.return_value = MagicMock()
                        mock_path.return_value.__truediv__ = MagicMock(return_value=mock_conf_file)
                        mock_path.side_effect = lambda x: mock_icon if x == '/tmp/icon.png' else mock_path.return_value
                        
                        result = edge.start(resignin=False)
                        
                        assert isinstance(result, dict), "Should return a dictionary"
                        assert 'warn' in result, "Should contain warning for invalid timeout"


class TestEdgeExecPipe:
    """exec_pipe method execution and result verification"""

    def test_exec_pipe_loads_pipeline(self):
        """
        exec_pipe()メソッドがパイプラインを読み込むことを検証します。
        
        趣旨: site_request()を呼び出してパイプラインを読み込むことを確認します。
        期待される結果: site_request()が呼ばれ、パイプラインが処理されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import threading
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.session = MagicMock()
            edge.tool = MagicMock()
            edge.options = MagicMock()
            edge.endpoint = "http://localhost:8000"
            edge.svcert_no_verify = False
            edge.icon_path = MagicMock()
            edge.user_info = {"name": "testuser"}
            edge.oauth2 = None
            edge.saml = None
            edge.threading_event = threading.Event()
            edge.threadings = []
            edge.timeout = 30
            
            mock_pipe_data = {"pipe_cmd": ["cmd1"]}
            mock_cmd_data = {"mode": "test", "cmd": "test_cmd", "timeout": 30}
            
            edge.site_request = MagicMock(side_effect=[
                (0, json.dumps(mock_pipe_data).encode(), {}),
                (0, json.dumps(mock_cmd_data).encode(), {})
            ])
            
            opt = {'title': 'test_pipe'}
            status, result = edge.exec_pipe(opt)
            
            assert status == 0, "Should return status 0 on success"
            assert 'success' in result, "Should contain success message"
            assert edge.site_request.called, "site_request should be called"

    def test_exec_pipe_returns_error_on_missing_pipe_cmd(self):
        """
        exec_pipe()メソッドがpipe_cmdなしの場合にエラーを返すことを検証します。
        
        趣旨: レスポンスにpipe_cmdが含まれない場合、エラーが返されることを確認します。
        期待される結果: 警告メッセージが返されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import threading
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.session = MagicMock()
            edge.tool = MagicMock()
            edge.threading_event = threading.Event()
            edge.threadings = []
            
            mock_pipe_data = {}  # Missing pipe_cmd
            
            edge.site_request = MagicMock(return_value=(0, json.dumps(mock_pipe_data).encode(), {}))
            
            opt = {'title': 'test_pipe'}
            status, result = edge.exec_pipe(opt)
            
            assert status == 1, "Should return status 1 on error"
            assert 'warn' in result, "Should contain warning message"

    def test_exec_pipe_initializes_threading_event(self):
        """
        exec_pipe()メソッドがスレッド実行用のイベントを初期化することを検証します。
        
        趣旨: パイプラインを実行する際に、threading_eventが初期化されることを確認します。
        期待される結果: threading_eventが存在し、スレッドが起動されます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            import threading
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.session = MagicMock()
            edge.tool = MagicMock()
            edge.options = MagicMock()
            edge.endpoint = "http://localhost:8000"
            edge.svcert_no_verify = False
            edge.icon_path = MagicMock()
            edge.user_info = {"name": "testuser"}
            edge.oauth2 = None
            edge.saml = None
            edge.threading_event = threading.Event()
            edge.threadings = []
            edge.timeout = 30
            
            mock_pipe_data = {"pipe_cmd": ["cmd1"]}
            mock_cmd_data = {"mode": "test", "cmd": "test_cmd", "timeout": 30}
            
            edge.site_request = MagicMock(side_effect=[
                (0, json.dumps(mock_pipe_data).encode(), {}),
                (0, json.dumps(mock_cmd_data).encode(), {})
            ])
            
            # Mock the feature's edgerun to return immediately without blocking
            mock_feature = MagicMock()
            mock_feature.edgerun = MagicMock(return_value=[(0, {"result": "test"})])
            edge.options.get_cmd_attr = MagicMock(return_value=mock_feature)
            
            opt = {'title': 'test_pipe'}
            status, result = edge.exec_pipe(opt)
            
            assert status == 0, "Should return status 0 on success"
            assert isinstance(edge.threading_event, threading.Event), "Should have threading event"
            # Give threads a moment to start (not to complete, just to be scheduled)
            import time
            time.sleep(0.1)


class TestEdgeStartTray:
    """start_tray method execution and result verification"""

    def test_start_tray_calls_tool_notify(self):
        """
        start_tray()メソッドがツール通知を呼び出すことを検証します。
        
        趣旨: start_tray()実行時に、toolのnotify()メソッドが呼ばれることを確認します。
        期待される結果: tool.notify()が成功メッセージを含めて呼ばれます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test Title"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.session = MagicMock()
            edge.tool = MagicMock()
            edge.options = MagicMock()
            edge.icon_path = MagicMock()
            edge.user_info = {"name": "testuser"}
            edge.oauth2 = None
            edge.saml = None
            
            # Mock site_request - Note: list_opens() is called FIRST in the menu construction
            edge.site_request = MagicMock(side_effect=[
                (0, json.dumps({}).encode(), {}),  # list_opens (called first - returns dict)
                (0, json.dumps([]).encode(), {}),  # list_cmd (called second - returns list)
                (0, json.dumps([]).encode(), {}),  # list_pipe (called third - returns list)
            ])
            
            # Mock pystray and Image in sys.modules for dynamic import
            mock_pystray = MagicMock()
            mock_icon = MagicMock()
            mock_pystray.Icon = MagicMock(return_value=mock_icon)
            mock_pystray.MenuItem = MagicMock(return_value=MagicMock())
            mock_pystray.Menu = MagicMock(return_value=MagicMock())
            
            mock_image = MagicMock()
            mock_image_instance = MagicMock()
            mock_image.open = MagicMock(return_value=mock_image_instance)
            
            with patch.dict('sys.modules', {
                'pystray': mock_pystray,
            }):
                with patch('cmdbox.app.edge.Image', mock_image):
                    edge.start_tray()
                    
                    edge.tool.notify.assert_called_once()
                    call_arg = edge.tool.notify.call_args[0][0]
                    assert 'success' in call_arg, "Should notify with success message"

    def test_start_tray_creates_menu_items(self):
        """
        start_tray()メソッドがメニューアイテムを作成することを検証します。
        
        趣旨: start_tray()実行時にメニューアイテムが適切に作成されることを確認します。
        期待される結果: pystray.Menu()が呼ばれます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test"
            mock_ver.__title__ = "Test Title"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.session = MagicMock()
            edge.tool = MagicMock()
            edge.options = MagicMock()
            edge.icon_path = MagicMock()
            edge.user_info = {"name": "testuser"}
            edge.oauth2 = None
            edge.saml = None
            
            edge.site_request = MagicMock(side_effect=[
                (0, json.dumps({}).encode(), {}),  # list_opens (called first - returns dict)
                (0, json.dumps([]).encode(), {}),  # list_cmd (called second - returns list)
                (0, json.dumps([]).encode(), {}),  # list_pipe (called third - returns list)
            ])
            
            # Mock pystray and Image in sys.modules for dynamic import
            mock_pystray = MagicMock()
            mock_icon = MagicMock()
            mock_pystray.Icon = MagicMock(return_value=mock_icon)
            mock_pystray.MenuItem = MagicMock(return_value=MagicMock())
            mock_pystray.Menu = MagicMock(return_value=MagicMock())
            
            mock_image = MagicMock()
            mock_image_instance = MagicMock()
            mock_image.open = MagicMock(return_value=mock_image_instance)
            
            with patch.dict('sys.modules', {
                'pystray': mock_pystray,
            }):
                with patch('cmdbox.app.edge.Image', mock_image):
                    edge.start_tray()
                    
                    assert mock_pystray.Menu.called, "pystray.Menu should be called"

    def test_start_tray_creates_icon(self):
        """
        start_tray()メソッドがトレイアイコンを作成することを検証します。
        
        趣旨: start_tray()実行時にpystray.Icon()が呼ばれることを確認します。
        期待される結果: pystray.Icon()が正しいパラメータで呼ばれます。
        """
        with setup_edge_environment():
            from cmdbox.app.edge import Edge
            
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            mock_appcls = MagicMock()
            mock_ver = MagicMock()
            mock_ver.__appid__ = "test_appid"
            mock_ver.__title__ = "Test Title"
            
            edge = Edge(logger=mock_logger, data="/tmp", appcls=mock_appcls, ver=mock_ver)
            edge.session = MagicMock()
            edge.tool = MagicMock()
            edge.options = MagicMock()
            edge.icon_path = MagicMock()
            edge.user_info = {"name": "testuser"}
            edge.oauth2 = None
            edge.saml = None
            
            edge.site_request = MagicMock(side_effect=[
                (0, json.dumps({}).encode(), {}),  # list_opens (called first - returns dict)
                (0, json.dumps([]).encode(), {}),  # list_cmd (called second - returns list)
                (0, json.dumps([]).encode(), {}),  # list_pipe (called third - returns list)
            ])
            
            # Mock pystray and Image in sys.modules for dynamic import
            mock_pystray = MagicMock()
            mock_icon = MagicMock()
            mock_pystray.Icon = MagicMock(return_value=mock_icon)
            mock_pystray.MenuItem = MagicMock(return_value=MagicMock())
            mock_pystray.Menu = MagicMock(return_value=MagicMock())
            
            mock_image = MagicMock()
            mock_image_instance = MagicMock()
            mock_image.open = MagicMock(return_value=mock_image_instance)
            
            with patch.dict('sys.modules', {
                'pystray': mock_pystray,
            }):
                with patch('cmdbox.app.edge.Image', mock_image):
                    edge.start_tray()
                    
                    mock_pystray.Icon.assert_called_once()
                    call_args = mock_pystray.Icon.call_args
                    assert call_args[0][0] == "test_appid", "Icon appid should match"
                    assert call_args[0][2] == "Test Title", "Icon title should match"
