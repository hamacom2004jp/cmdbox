"""
Test cases for cmdbox_server_start command
"""
import pytest
import logging
import argparse
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cmdbox.app.features.cli.cmdbox_server_start import ServerStart


@pytest.fixture
def server_start_instance(version_mock):
    """Create a ServerStart instance for testing"""
    return ServerStart(Mock(), version_mock)


class TestServerStart:
    """Test class for ServerStart command"""

    def test_apprun_without_data_option(self, server_start_instance, mock_logger):
        """
        Test apprun validation for missing data option.
        
        趣旨: --dataオプションが指定されていない場合、apprunメソッドが
        警告ステータスと警告メッセージを返すことを検証します。
        期待される結果: RESP_WARNステータスが返される
        """
        args = argparse.Namespace(
            data=None,
            svname='test_server',
            host='localhost',
            port=6379,
            password='password',
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = server_start_instance.apprun(mock_logger, args, tm)
        
        # Should return a tuple (status, result) when validation fails
        assert isinstance(result, tuple)
        assert len(result) == 2
        status, msg = result
        assert status == server_start_instance.RESP_WARN
        assert 'warn' in msg
        assert 'data' in msg['warn']

    def test_apprun_without_svname_option(self, server_start_instance, mock_logger, temp_data_dir):
        """
        Test apprun validation for missing svname option.
        
        趣旨: --svnameオプションが指定されていない場合、apprunメソッドが
        警告ステータスと警告メッセージを返すことを検証します。
        期待される結果: RESP_WARNステータスが返される
        """
        args = argparse.Namespace(
            data=temp_data_dir,
            svname=None,
            host='localhost',
            port=6379,
            password='password',
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = server_start_instance.apprun(mock_logger, args, tm)
        
        # Should return a tuple (status, result) when validation fails
        assert isinstance(result, tuple)
        assert len(result) == 2
        status, msg = result
        assert status == server_start_instance.RESP_WARN
        assert 'warn' in msg
        assert 'svname' in msg['warn']

    @patch('cmdbox.app.server.Server')
    def test_apprun_with_valid_args(self, mock_server_class, server_start_instance, mock_logger, temp_data_dir):
        """
        Test apprun with valid arguments creates Server instance correctly.
        
        趣旨: 有効な引数がすべて提供された場合、apprunメソッドが
        正しいパラメータでServerインスタンスを生成することを検証します。
        期待される結果: Serverクラスが正しいホスト、ポート、パスワード、
        サービス名で初期化される
        """
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        mock_server_instance.start_server = MagicMock()
        mock_server_instance.svname = 'test_server-abc123'
        
        args = argparse.Namespace(
            data=temp_data_dir,
            svname='test_server',
            host='localhost',
            port=6379,
            password='password',
            retry_count=20,
            retry_interval=5,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = server_start_instance.apprun(mock_logger, args, tm)
        
        # Check that 3 values are returned for success
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        
        # Check that Server class was instantiated with correct parameters
        mock_server_class.assert_called_once()
        call_args = mock_server_class.call_args
        assert call_args[0][0] == temp_data_dir  # data_dir
        assert call_args[0][1] == mock_logger    # logger
        assert call_args[1]['redis_host'] == 'localhost'
        assert call_args[1]['redis_port'] == 6379
        assert call_args[1]['redis_password'] == 'password'
        assert call_args[1]['svname'] == 'test_server'

    def test_is_cluster_redirect(self, server_start_instance):
        """Test that is_cluster_redirect raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            server_start_instance.is_cluster_redirect()
