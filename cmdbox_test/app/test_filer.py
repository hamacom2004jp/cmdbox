"""
Test cases for cmdbox.app.filer module

This file contains tests that execute actual Filer class methods and verify their results.
Methods are called with properly mocked dependencies to ensure real execution and result validation.
"""
import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import datetime
import sys
from typing import Dict, Any


def setup_filer_environment():
    """Helper to setup Filer environment by clearing cached modules and mocking dependencies."""
    # Remove cached modules to prevent circular import issues
    for mod in list(sys.modules.keys()):
        if mod.startswith('cmdbox'):
            del sys.modules[mod]
    
    # Create a mock common module with necessary functions
    mock_common = MagicMock()
    mock_common.mkdirs = MagicMock()
    mock_common.safe_fname = lambda x: x  # Identity function for now
    mock_common.rmdirs = MagicMock()
    mock_common.load_file = MagicMock(side_effect=lambda p, func, mode='r': func(MagicMock(read=lambda: b'test_data')))
    
    # Create a proper save_file implementation that actually writes to the file
    def mock_save_file(filepath, func, mode='w'):
        with open(filepath, mode) as f:
            func(f)
    
    mock_common.save_file = MagicMock(side_effect=mock_save_file)
    
    # Create a mock commons module
    mock_commons = MagicMock()
    mock_commons.convert = MagicMock()
    
    return patch.dict('sys.modules', {
        'cmdbox.app.common': mock_common,
        'cmdbox.app.commons': mock_commons,
    })


class TestFilerInitialization:
    """Filer class initialization tests"""

    def test_filer_init_creates_logger_and_data_dir(self):
        """
        Filer()のコンストラクタ初期化機能を検証します。
        
        趣旨: Filerクラスが初期化される際に、ロガーとデータディレクトリが正しく設定されることを確認します。
        期待される結果: インスタンスが作成され、data_dirとloggerが設定されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                
                assert filer.data_dir == data_dir, "data_dir should be set"
                assert filer.logger == mock_logger, "logger should be set"
                assert filer.RESP_SUCCESS == 0, "RESP_SUCCESS should be 0"
                assert filer.RESP_WARN == 1, "RESP_WARN should be 1"
                assert filer.RESP_ERROR == 2, "RESP_ERROR should be 2"


class TestFilerFileExists:
    """_file_exists method execution and result verification"""

    def test_file_exists_validates_existing_file(self):
        """
        _file_exists()メソッドの既存ファイル検証機能を検証します。
        
        趣旨: 存在するファイルパスに対して検証を実行し、Trueが返されることを確認します。
        期待される結果: メソッドがTrue、絶対パス、成功メッセージを返します。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                test_file = data_dir / "test.txt"
                test_file.write_text("test content")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                chk, abspath, msg = filer._file_exists("/test.txt")
                
                assert chk is True, "Should return True for existing file"
                assert abspath == test_file, "Should return correct absolute path"
                assert 'success' in msg, "Should return success message"

    def test_file_exists_detects_missing_file(self):
        """
        _file_exists()メソッドの存在しないファイル検出機能を検証します。
        
        趣旨: 存在しないファイルパスに対して検証を実行し、Falseが返されることを確認します。
        期待される結果: メソッドがFalse、パス、警告メッセージを返します。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                chk, abspath, msg = filer._file_exists("/nonexistent.txt")
                
                assert chk is False, "Should return False for non-existing file"
                assert 'warn' in msg, "Should return warning message"

    def test_file_exists_detects_out_of_bounds_path(self):
        """
        _file_exists()メソッドのセキュリティパス検証機能を検証します。
        
        趣旨: データディレクトリの外のパスへのアクセスを試みた場合、Falseが返されることを確認します。
        期待される結果: メソッドがFalseを返し、セキュリティ警告メッセージが返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                chk, abspath, msg = filer._file_exists("/../../../etc/passwd")
                
                assert chk is False, "Should return False for out-of-bounds path"
                assert 'warn' in msg, "Should return warning message"

    def test_file_exists_validates_not_exists_flag(self):
        """
        _file_exists()メソッドの逆検証機能を検証します。
        
        趣旨: not_exists=Trueで呼び出した場合、存在しないパスに対してTrueが返されることを確認します。
        期待される結果: 存在しないパスの検証がTrueになります。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                chk, abspath, msg = filer._file_exists("/newfile.txt", not_exists=True)
                
                assert chk is True, "Should return True for non-existing file when not_exists=True"
                assert 'success' in msg, "Should return success message"


class TestFilerFileMkdir:
    """file_mkdir method execution and result verification"""

    def test_file_mkdir_creates_directory(self):
        """
        file_mkdir()メソッドのディレクトリ作成機能を検証します。
        
        趣旨: 新しいディレクトリを作成し、正しく作成されることを確認します。
        期待される結果: レスポンスコードが0（成功）で返され、ディレクトリが実際に作成されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_mkdir("/newdir")
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert (data_dir / "newdir").is_dir(), "Directory should be created"

    def test_file_mkdir_fails_for_existing_directory(self):
        """
        file_mkdir()メソッドの既存ディレクトリ検出機能を検証します。
        
        趣旨: 既に存在するディレクトリの作成を試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                existing_dir = data_dir / "existing"
                existing_dir.mkdir()
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_mkdir("/existing")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"


class TestFilerFileRmdir:
    """file_rmdir method execution and result verification"""

    def test_file_rmdir_removes_directory(self):
        """
        file_rmdir()メソッドのディレクトリ削除機能を検証します。
        
        趣旨: 存在するディレクトリを削除し、正しく削除されることを確認します。
        期待される結果: レスポンスコードが0（成功）で返され、ディレクトリが削除されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                test_dir = data_dir / "testdir"
                test_dir.mkdir()
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_rmdir("/testdir")
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"

    def test_file_rmdir_prevents_removing_root_directory(self):
        """
        file_rmdir()メソッドのルートディレクトリ保護機能を検証します。
        
        趣旨: ルートディレクトリの削除を試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_rmdir("/")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"

    def test_file_rmdir_fails_for_nonexistent_directory(self):
        """
        file_rmdir()メソッドの存在しないディレクトリ検出機能を検証します。
        
        趣旨: 存在しないディレクトリの削除を試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_rmdir("/nonexistent")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"


class TestFilerFileDownload:
    """file_download method execution and result verification"""

    def test_file_download_retrieves_file_content(self):
        """
        file_download()メソッドのファイルダウンロード機能を検証します。
        
        趣旨: テキストファイルをダウンロードし、内容が正しく返されることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイル名とデータが返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                test_file = data_dir / "test.txt"
                test_file.write_text("test content")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_download("/test.txt")
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert 'name' in msg['success'], "Should return file name"
                assert 'data' in msg['success'], "Should return file data"

    def test_file_download_fails_for_directory(self):
        """
        file_download()メソッドのディレクトリ検出機能を検証します。
        
        趣旨: ディレクトリのダウンロードを試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                test_dir = data_dir / "testdir"
                test_dir.mkdir()
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_download("/testdir")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"

    def test_file_download_fails_for_nonexistent_file(self):
        """
        file_download()メソッドの存在しないファイル検出機能を検証します。
        
        趣旨: 存在しないファイルのダウンロードを試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_download("/nonexistent.txt")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"


class TestFilerFileUpload:
    """file_upload method execution and result verification"""

    def test_file_upload_creates_new_file(self):
        """
        file_upload()メソッドの新規ファイル作成機能を検証します。
        
        趣旨: 新しいファイルをアップロードし、正しく作成されることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイルが実際に作成されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_upload(
                    current_path="/",
                    file_name="newfile.txt",
                    file_data=b"test data",
                    mkdir=False,
                    orverwrite=False
                )
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert (data_dir / "newfile.txt").is_file(), "File should be created"

    def test_file_upload_prevents_overwrite_by_default(self):
        """
        file_upload()メソッドの上書き防止機能を検証します。
        
        趣旨: 既存ファイルの上書きを試みた場合、上書きしない場合は警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                existing_file = data_dir / "existing.txt"
                existing_file.write_text("original")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_upload(
                    current_path="/existing.txt",
                    file_name="existing.txt",
                    file_data=b"new data",
                    mkdir=False,
                    orverwrite=False
                )
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"
                assert existing_file.read_text() == "original", "Original file should not be modified"

    def test_file_upload_allows_overwrite_with_flag(self):
        """
        file_upload()メソッドの上書き許可機能を検証します。
        
        趣旨: orverwrite=Trueで既存ファイルを上書きした場合、正しく上書きされることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイルが上書きされます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                existing_file = data_dir / "existing.txt"
                existing_file.write_text("original")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_upload(
                    current_path="/existing.txt",
                    file_name="existing.txt",
                    file_data=b"new data",
                    mkdir=False,
                    orverwrite=True
                )
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"


class TestFilerFileRemove:
    """file_remove method execution and result verification"""

    def test_file_remove_deletes_file(self):
        """
        file_remove()メソッドのファイル削除機能を検証します。
        
        趣旨: ファイルを削除し、正しく削除されることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイルが削除されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                test_file = data_dir / "test.txt"
                test_file.write_text("test content")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_remove("/test.txt")
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert not test_file.is_file(), "File should be deleted"

    def test_file_remove_fails_for_directory(self):
        """
        file_remove()メソッドのディレクトリ検出機能を検証します。
        
        趣旨: ディレクトリの削除を試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                test_dir = data_dir / "testdir"
                test_dir.mkdir()
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_remove("/testdir")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"


class TestFilerFileCopy:
    """file_copy method execution and result verification"""

    def test_file_copy_copies_file(self):
        """
        file_copy()メソッドのファイルコピー機能を検証します。
        
        趣旨: ファイルをコピーし、正しくコピーされることを確認します。
        期待される結果: レスポンスコードが0（成功）で、コピーファイルが作成されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                source_file = data_dir / "source.txt"
                source_file.write_text("test content")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_copy(
                    from_path="/source.txt",
                    to_path="/copy.txt",
                    orverwrite=False
                )
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert (data_dir / "copy.txt").is_file(), "Copy file should be created"
                assert (data_dir / "copy.txt").read_text() == "test content", "Content should match"

    def test_file_copy_copies_directory(self):
        """
        file_copy()メソッドのディレクトリコピー機能を検証します。
        
        趣旨: ディレクトリをコピーし、正しくコピーされることを確認します。
        期待される結果: レスポンスコードが0（成功）で、コピーディレクトリが作成されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                source_dir = data_dir / "sourcedir"
                source_dir.mkdir()
                (source_dir / "file.txt").write_text("test")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_copy(
                    from_path="/sourcedir",
                    to_path="/copydir",
                    orverwrite=False
                )
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert (data_dir / "copydir").is_dir(), "Copy directory should be created"

    def test_file_copy_fails_for_nonexistent_source(self):
        """
        file_copy()メソッドのコピー元検証機能を検証します。
        
        趣旨: 存在しないファイルのコピーを試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_copy(
                    from_path="/nonexistent.txt",
                    to_path="/copy.txt",
                    orverwrite=False
                )
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"


class TestFilerFileMove:
    """file_move method execution and result verification"""

    def test_file_move_moves_file(self):
        """
        file_move()メソッドのファイル移動機能を検証します。
        
        趣旨: ファイルを移動し、正しく移動されることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイルが移動されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                source_file = data_dir / "source.txt"
                source_file.write_text("test content")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_move(
                    from_path="/source.txt",
                    to_path="/moved.txt"
                )
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert not source_file.is_file(), "Source file should be moved"
                assert (data_dir / "moved.txt").is_file(), "Destination file should exist"

    def test_file_move_fails_for_nonexistent_source(self):
        """
        file_move()メソッドの移動元検証機能を検証します。
        
        趣旨: 存在しないファイルの移動を試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_move(
                    from_path="/nonexistent.txt",
                    to_path="/moved.txt"
                )
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"

    def test_file_move_fails_for_existing_destination(self):
        """
        file_move()メソッドの移動先検証機能を検証します。
        
        趣旨: 既に存在する移動先への移動を試みた場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                source_file = data_dir / "source.txt"
                source_file.write_text("source")
                dest_file = data_dir / "dest.txt"
                dest_file.write_text("destination")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_move(
                    from_path="/source.txt",
                    to_path="/dest.txt"
                )
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"


class TestFilerFileList:
    """file_list method execution and result verification"""

    def test_file_list_retrieves_root_directory_contents(self):
        """
        file_list()メソッドのルートディレクトリ取得機能を検証します。
        
        趣旨: ルートディレクトリのファイルリストを取得し、正しく返されることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイルリストが返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                (data_dir / "file1.txt").write_text("content1")
                (data_dir / "file2.txt").write_text("content2")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_list("/")
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"
                assert isinstance(msg['success'], dict), "Should return a dictionary"

    def test_file_list_retrieves_subdirectory_contents(self):
        """
        file_list()メソッドのサブディレクトリ取得機能を検証します。
        
        趣旨: サブディレクトリのファイルリストを取得し、正しく返されることを確認します。
        期待される結果: レスポンスコードが0（成功）で、ファイルリストが返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                subdir = data_dir / "subdir"
                subdir.mkdir()
                (subdir / "file.txt").write_text("content")
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_list("/subdir")
                
                assert resp_code == filer.RESP_SUCCESS, "Should return success code"
                assert 'success' in msg, "Should return success message"

    def test_file_list_fails_for_nonexistent_directory(self):
        """
        file_list()メソッドの存在しないディレクトリ検出機能を検証します。
        
        趣旨: 存在しないディレクトリのリストを取得した場合、警告が返されることを確認します。
        期待される結果: レスポンスコードが1（警告）で返されます。
        """
        with setup_filer_environment():
            from cmdbox.app.filer import Filer
            
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_logger = MagicMock(spec=logging.Logger)
                data_dir = Path(tmpdir)
                
                filer = Filer(data_dir=data_dir, logger=mock_logger)
                resp_code, msg = filer.file_list("/nonexistent")
                
                assert resp_code == filer.RESP_WARN, "Should return warning code"
                assert 'warn' in msg, "Should return warning message"
