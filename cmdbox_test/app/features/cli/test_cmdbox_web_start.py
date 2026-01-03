"""
Test cases for cmdbox_web_start command
"""
import pytest
import logging
import argparse
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from cmdbox.app.features.cli.cmdbox_web_start import WebStart


@pytest.fixture
def web_start_instance(version_mock):
    """Create a WebStart instance for testing"""
    return WebStart(Mock(), version_mock)


class TestWebStart:
    """Test class for WebStart command"""

    def test_apprun_without_data_option(self, web_start_instance, mock_logger):
        """
        Test apprun validation for missing data option.
        
        趣旨: --dataオプションが指定されていない場合、apprunメソッドが
        警告ステータスと警告メッセージを返すことを検証します。
        期待される結果: RESP_WARNステータスが返される
        """
        args = argparse.Namespace(
            data=None,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = web_start_instance.apprun(mock_logger, args, tm)
        
        # Should return a tuple (status, result, obj) when validation fails
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        assert status == web_start_instance.RESP_WARN
        assert 'warn' in msg
        assert 'data' in msg['warn']

    @patch('cmdbox.app.features.cli.cmdbox_web_start.WebStart.createWeb')
    @patch('cmdbox.app.features.cli.cmdbox_web_start.WebStart.start')
    def test_apprun_with_valid_args(self, mock_start, mock_create_web, web_start_instance, mock_logger, temp_data_dir):
        """
        Test apprun with valid arguments creates Web instance correctly.
        
        趣旨: 有効な引数がすべて提供された場合、apprunメソッドが
        正しいパラメータでWebインスタンスを生成することを検証します。
        期待される結果: Webクラスが正しいパラメータで初期化される
        """
        mock_web_instance = MagicMock()
        mock_create_web.return_value = mock_web_instance
        mock_start.return_value = None
        
        args = argparse.Namespace(
            data=temp_data_dir,
            host='localhost',
            port=6379,
            password='password',
            svname='server',
            allow_host='0.0.0.0',
            listen_port=8081,
            ssl_listen_port=8443,
            ssl_cert=None,
            ssl_key=None,
            ssl_keypass=None,
            ssl_ca_certs=None,
            signin_file=None,
            gui_mode=False,
            client_only=False,
            doc_root=None,
            gui_html=None,
            filer_html=None,
            result_html=None,
            users_html=None,
            assets=None,
            signin_html=None,
            session_domain=None,
            session_path='/',
            session_secure=False,
            session_timeout='900',
            outputs_key=None,
            gunicorn_workers=4,
            gunicorn_timeout=30,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = web_start_instance.apprun(mock_logger, args, tm)
        
        # Check that 3 values are returned for success case
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        
        # Check that Web was instantiated
        mock_create_web.assert_called_once()
        # Check that start was called
        mock_start.assert_called_once()

    def test_is_cluster_redirect(self, web_start_instance):
        """Test that is_cluster_redirect raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            web_start_instance.is_cluster_redirect()
