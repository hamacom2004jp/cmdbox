"""
Test cases for cmdbox_web_user_list command
"""
import pytest
import logging
import argparse
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cmdbox.app.features.cli.cmdbox_web_user_list import WebUserList


@pytest.fixture
def web_user_list_instance(version_mock):
    """Create a WebUserList instance for testing"""
    return WebUserList(Mock(), version_mock)


class TestWebUserList:
    """Test class for WebUserList command"""

    def test_apprun_without_signin_file_option(self, web_user_list_instance, mock_logger, temp_data_dir):
        """
        Test apprun validation for missing signin_file option.
        
        趣旨: --signin_fileオプションが指定されていない場合、エラーが発生して
        警告ステータスが返されることを検証します。
        期待される結果: RESP_WARNステータスが返される
        """
        args = argparse.Namespace(
            data=temp_data_dir,
            signin_file=None,
            user_name=None,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = web_user_list_instance.apprun(mock_logger, args, tm)
        
        # Should return a tuple (status, result, obj)
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        # When signin_file is not specified, it should raise an exception in Web.user_list
        assert status == web_user_list_instance.RESP_WARN

    @patch('cmdbox.app.web.Web')
    def test_apprun_list_all_users(self, mock_web_class, web_user_list_instance, mock_logger, temp_data_dir):
        """
        Test apprun lists all users when user_name is not specified.
        
        趣旨: --signin_fileが指定され、user_nameが指定されていない場合、
        すべてのユーザーをリストする処理を実行することを検証します。
        期待される結果: SUCCESSステータスと全ユーザーリストが返される
        """
        mock_web_instance = MagicMock()
        mock_web_class.return_value = mock_web_instance
        mock_web_instance.user_list = MagicMock(return_value=[
            {'user_name': 'user1'},
            {'user_name': 'user2'}
        ])
        
        signin_file = temp_data_dir / 'signin.json'
        signin_file.write_text('{}')
        
        args = argparse.Namespace(
            data=temp_data_dir,
            signin_file=str(signin_file),
            user_name=None,
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = web_user_list_instance.apprun(mock_logger, args, tm)
        
        # Check that 3 values are returned for success case
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        assert status == web_user_list_instance.RESP_SUCCESS
        
        # Check that Web class was instantiated
        mock_web_class.assert_called_once()
        # Check that user_list was called with None for all users
        mock_web_instance.user_list.assert_called_once_with(None)

    @patch('cmdbox.app.web.Web')
    def test_apprun_list_specific_user(self, mock_web_class, web_user_list_instance, mock_logger, temp_data_dir):
        """
        Test apprun lists specific user when user_name is specified.
        
        趣旨: --signin_fileと--user_nameが両方指定された場合、
        指定されたユーザーのみをリストする処理を実行することを検証します。
        期待される結果: SUCCESSステータスと該当ユーザー情報が返される
        """
        mock_web_instance = MagicMock()
        mock_web_class.return_value = mock_web_instance
        mock_web_instance.user_list = MagicMock(return_value=[
            {'user_name': 'user1'}
        ])
        
        signin_file = temp_data_dir / 'signin.json'
        signin_file.write_text('{}')
        
        args = argparse.Namespace(
            data=temp_data_dir,
            signin_file=str(signin_file),
            user_name='user1',
            format='json',
            output_json=None,
            output_json_append=False
        )
        
        tm = time.time()
        result = web_user_list_instance.apprun(mock_logger, args, tm)
        
        # Check that 3 values are returned for success case
        assert isinstance(result, tuple)
        assert len(result) == 3
        status, msg, obj = result
        assert status == web_user_list_instance.RESP_SUCCESS
        
        # Check that Web class was instantiated
        mock_web_class.assert_called_once()
        # Check that user_list was called with specific user name
        mock_web_instance.user_list.assert_called_once_with('user1')

    def test_is_cluster_redirect(self, web_user_list_instance):
        """Test that is_cluster_redirect raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            web_user_list_instance.is_cluster_redirect()
