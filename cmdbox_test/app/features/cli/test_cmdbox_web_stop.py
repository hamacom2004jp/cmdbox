"""
Test cases for cmdbox_web_stop command
"""
import pytest
import logging
import argparse
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cmdbox.app.features.cli.cmdbox_web_stop import WebStop


@pytest.fixture
def web_stop_instance(version_mock):
    """Create a WebStop instance for testing"""
    return WebStop(Mock(), version_mock)


class TestWebStop:
    """Test class for WebStop command"""

    @patch('cmdbox.app.web.Web')
    def test_apprun_successful_stop(self, mock_web_class, web_stop_instance, mock_logger, temp_data_dir):
        """
        Test apprun with valid arguments creates Web instance and stops it.
        
        趣旨: 有効な引数がすべて提供された場合、apprunメソッドが
        Webインスタンスを生成してstop処理を実行することを検証します。
        期待される結果: Webクラスが生成され、stop()メソッドが呼ばれる
        """
        mock_web_instance = MagicMock()
        mock_web_class.return_value = mock_web_instance
        mock_web_instance.stop = MagicMock()
        
        args = argparse.Namespace(
            data=temp_data_dir,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = web_stop_instance.apprun(mock_logger, args, tm)
        
        # Check that 3 values are returned for success case
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        assert status == web_stop_instance.RESP_SUCCESS
        
        # Check that Web class was instantiated with correct parameters
        mock_web_class.assert_called_once()
        call_args = mock_web_class.call_args
        assert call_args[0][0] == mock_logger    # logger
        # Check that stop was called
        mock_web_instance.stop.assert_called_once()

    def test_is_cluster_redirect(self, web_stop_instance):
        """Test that is_cluster_redirect raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            web_stop_instance.is_cluster_redirect()
