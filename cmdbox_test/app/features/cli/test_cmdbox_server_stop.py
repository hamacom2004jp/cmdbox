"""
Test cases for cmdbox_server_stop command
"""
import pytest
import logging
import argparse
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cmdbox.app.features.cli.cmdbox_server_stop import ServerStop


@pytest.fixture
def server_stop_instance(version_mock):
    """Create a ServerStop instance for testing"""
    return ServerStop(Mock(), version_mock)


class TestServerStop:
    """Test class for ServerStop command"""

    @patch('cmdbox.app.client.Client')
    def test_apprun_stop_server(self, mock_client_class, server_stop_instance, mock_logger, temp_data_dir):
        """
        Test apprun stops server and creates Client instance correctly.
        
        趣旨: apprunメソッドがサーバー停止処理を実行し、
        正しいパラメータでClientインスタンスを生成することを検証します。
        期待される結果: Clientクラスが正しいホスト、ポート、パスワード、
        サービス名で初期化される
        """
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        mock_client_instance.stop_server = MagicMock(
            return_value={'success': 'Server stopped successfully'}
        )
        
        args = argparse.Namespace(
            data=temp_data_dir,
            host='localhost',
            port=6379,
            password='password',
            svname='test_server',
            retry_count=3,
            retry_interval=5,
            timeout=15,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        status, result, obj = server_stop_instance.apprun(mock_logger, args, tm)
        
        # Check that Client class was instantiated with correct parameters
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args[0][0] == mock_logger    # logger
        assert call_args[1]['redis_host'] == 'localhost'
        assert call_args[1]['redis_port'] == 6379
        assert call_args[1]['redis_password'] == 'password'
        assert call_args[1]['svname'] == 'test_server'

    def test_is_cluster_redirect(self, server_stop_instance):
        """Test that is_cluster_redirect returns True for ServerStop"""
        result = server_stop_instance.is_cluster_redirect()
        assert result is True
