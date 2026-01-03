"""
Test cases for cmdbox_server_list command
"""
import pytest
import logging
import argparse
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cmdbox.app.features.cli.cmdbox_server_list import ServerList


@pytest.fixture
def server_list_instance(version_mock):
    """Create a ServerList instance for testing"""
    return ServerList(Mock(), version_mock)


class TestServerList:
    """Test class for ServerList command"""

    @patch('cmdbox.app.server.Server')
    def test_apprun_list_servers(self, mock_server_class, server_list_instance, mock_logger, temp_data_dir):
        """
        Test apprun retrieves server list and returns success status.
        
        趣旨: apprunメソッドがサーバーのリストを正常に取得し、
        成功ステータスと複数のサーバー情報を返すことを検証します。
        期待される結果: RESP_SUCCESSステータスが返され、resultに複数の
        サーバー情報が含まれている
        """
        # Mock the Server instance and its methods
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        
        # Mock the list_server method to return a list of servers
        mock_server_instance.list_server.return_value = {
            'success': [
                {
                    'svname': 'server-abc123',
                    'pid': 12345,
                    'model': 'test_model',
                    'status': 'running'
                },
                {
                    'svname': 'server-def456',
                    'pid': 12346,
                    'model': 'another_model',
                    'status': 'running'
                }
            ]
        }
        
        args = argparse.Namespace(
            data=temp_data_dir,
            host='localhost',
            port=6379,
            password='password',
            timeout=15,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        status, result, obj = server_list_instance.apprun(mock_logger, args, tm)
        
        # Check that success status is returned
        assert status == server_list_instance.RESP_SUCCESS
        assert 'success' in result
        assert len(result['success']) == 2

    @patch('cmdbox.app.server.Server')
    def test_apprun_no_servers_running(self, mock_server_class, server_list_instance, mock_logger, temp_data_dir):
        """
        Test apprun returns warning when no servers are running.
        
        趣旨: サーバーが起動していない場合、apprunメソッドが
        警告ステータスと警告メッセージを返すことを検証します。
        期待される結果: RESP_WARNステータスが返される
        """
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        
        # Mock the list_server method to return warning
        mock_server_instance.list_server.return_value = {
            'warn': 'No server is running.'
        }
        
        args = argparse.Namespace(
            data=temp_data_dir,
            host='localhost',
            port=6379,
            password='password',
            timeout=15,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        status, result, obj = server_list_instance.apprun(mock_logger, args, tm)
        
        # Check that warning status is returned
        assert status == server_list_instance.RESP_WARN
        assert 'warn' in result

    def test_is_cluster_redirect(self, server_list_instance):
        """Test that is_cluster_redirect raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            server_list_instance.is_cluster_redirect()

    @patch('cmdbox.app.server.Server')
    def test_apprun_returned_object(self, mock_server_class, server_list_instance, mock_logger, temp_data_dir):
        """
        Test apprun returns correct Server object.
        
        趣旨: apprunメソッドが正しくServerオブジェクトを返すことを検証します。
        返されたオブジェクトが、メソッド内で生成されたServerインスタンスと
        同一であることを確認します。
        期待される結果: 返されるオブジェクトがモック化されたServerインスタンス
        と同じ
        """
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        mock_server_instance.list_server.return_value = {'success': []}
        
        args = argparse.Namespace(
            data=temp_data_dir,
            host='localhost',
            port=6379,
            password='password',
            timeout=15,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        status, result, obj = server_list_instance.apprun(mock_logger, args, tm)
        
        # Check that Server object is returned
        assert obj == mock_server_instance

    def test_option_descriptions(self, server_list_instance):
        """Test that option descriptions are present"""
        options = server_list_instance.get_option()
        
        assert 'description_ja' in options
        assert 'description_en' in options
        assert len(options['description_ja']) > 0
        assert len(options['description_en']) > 0
