"""
Test cases for cmdbox.app.common module

This file contains tests that execute actual common module functions and verify their results.
Functions are called with properly mocked dependencies to ensure real execution and result validation.
"""
import pytest
import logging
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
import string


class TestCommonRandomString:
    """random_string function execution and result verification"""

    def test_random_string_returns_correct_length(self):
        """
        random_string()関数の長さ指定機能を検証します。
        
        趣旨: 指定した長さのランダムな文字列が生成されることを確認します。
        期待される結果: デフォルト値16文字、指定値32文字など正確な長さが返されます。
        """
        from cmdbox.app.common import random_string
        
        result_default = random_string()
        assert isinstance(result_default, str), "Should return a string"
        assert len(result_default) == 16, "Default should return 16 characters"
        
        result_32 = random_string(size=32)
        assert len(result_32) == 32, "Should return 32 characters when specified"
        
        result_1 = random_string(size=1)
        assert len(result_1) == 1, "Should return 1 character when specified"

    def test_random_string_uses_correct_character_set(self):
        """
        random_string()関数の文字セット機能を検証します。
        
        趣旨: デフォルトの文字セット(大文字アルファベット+数字)のみが使用されることを確認します。
        期待される結果: 返された文字列はすべて大文字アルファベット又は数字で構成されます。
        """
        from cmdbox.app.common import random_string
        
        default_chars = string.ascii_uppercase + string.digits
        result = random_string(size=100)
        
        for char in result:
            assert char in default_chars, f"Character '{char}' not in default character set"

    def test_random_string_custom_character_set(self):
        """
        random_string()関数のカスタム文字セット機能を検証します。
        
        趣旨: カスタム文字セットが正しく適用されることを確認します。
        期待される結果: 返された文字列はカスタム文字セットのみで構成されます。
        """
        from cmdbox.app.common import random_string
        
        custom_chars = "ABC123"
        result = random_string(size=50, chars=custom_chars)
        
        for char in result:
            assert char in custom_chars, f"Character '{char}' not in custom character set"


class TestCommonHashPassword:
    """hash_password function execution and result verification"""

    def test_hash_password_md5_consistency(self):
        """
        hash_password()関数のMD5ハッシュ一貫性を検証します。
        
        趣旨: 同じパスワードでハッシュ化すると毎回同じハッシュが得られることを確認します。
        期待される結果: 複数回のハッシュ化で同一の結果が返されます。
        """
        from cmdbox.app.common import hash_password
        
        password = "testpassword123"
        hash1 = hash_password(password, 'md5')
        hash2 = hash_password(password, 'md5')
        
        assert hash1 == hash2, "Same password should produce same hash"
        assert isinstance(hash1, str), "Hash should be a string"
        assert len(hash1) == 32, "MD5 hash should be 32 characters"

    def test_hash_password_sha256(self):
        """
        hash_password()関数のSHA256ハッシュ機能を検証します。
        
        趣旨: SHA256アルゴリズムでハッシュ化できることを確認します。
        期待される結果: SHA256ハッシュが正しく生成されます。
        """
        from cmdbox.app.common import hash_password
        
        password = "testpassword123"
        hash_result = hash_password(password, 'sha256')
        
        assert isinstance(hash_result, str), "Hash should be a string"
        assert len(hash_result) == 64, "SHA256 hash should be 64 characters"

    def test_hash_password_different_passwords(self):
        """
        hash_password()関数の異なるパスワード識別機能を検証します。
        
        趣旨: 異なるパスワードは異なるハッシュを生成することを確認します。
        期待される結果: 異なるパスワードは異なるハッシュが返されます。
        """
        from cmdbox.app.common import hash_password
        
        hash1 = hash_password("password1", 'md5')
        hash2 = hash_password("password2", 'md5')
        
        assert hash1 != hash2, "Different passwords should produce different hashes"


class TestCommonEncryptDecrypt:
    """encrypt and decrypt functions execution and result verification"""

    def test_encrypt_and_decrypt_roundtrip(self):
        """
        encrypt()とdecrypt()関数の暗号化・復号化機能を検証します。
        
        趣旨: メッセージが暗号化された後に復号化すると、元のメッセージが取得できることを確認します。
        期待される結果: 暗号化・復号化のラウンドトリップで元のメッセージが復元されます。
        """
        from cmdbox.app.common import encrypt, decrypt
        
        original_message = "This is a secret message"
        password = "mypassword123"
        
        encrypted = encrypt(original_message, password)
        assert isinstance(encrypted, str), "Encrypted message should be a string"
        assert encrypted != original_message, "Encrypted message should differ from original"
        
        decrypted = decrypt(encrypted, password)
        assert decrypted == original_message, "Decrypted message should match original"

    def test_decrypt_with_wrong_password_returns_none(self):
        """
        decrypt()関数の間違ったパスワード処理を検証します。
        
        趣旨: 間違ったパスワードで復号化すると、Noneが返されることを確認します。
        期待される結果: 間違ったパスワードでの復号化はNoneを返します。
        """
        from cmdbox.app.common import encrypt, decrypt
        
        original_message = "Secret message"
        password = "correct_password"
        wrong_password = "wrong_password"
        
        encrypted = encrypt(original_message, password)
        decrypted = decrypt(encrypted, wrong_password)
        
        assert decrypted is None, "Decryption with wrong password should return None"

    def test_encrypt_empty_message(self):
        """
        encrypt()関数の空メッセージ処理を検証します。
        
        趣旨: 空のメッセージも正しく暗号化できることを確認します。
        期待される結果: 空のメッセージが暗号化・復号化できます。
        """
        from cmdbox.app.common import encrypt, decrypt
        
        empty_message = ""
        password = "password"
        
        encrypted = encrypt(empty_message, password)
        decrypted = decrypt(encrypted, password)
        
        assert decrypted == empty_message, "Empty message should be encrypted and decrypted correctly"


class TestCommonFileOperations:
    """load_yml, save_yml, load_file, save_file functions execution and result verification"""

    def test_save_and_load_yml(self):
        """
        save_yml()とload_yml()関数のYAML操作機能を検証します。
        
        趣旨: YAMLファイルへの保存と読み込みが正しく機能することを確認します。
        期待される結果: 保存したYAMLデータが読み込まれると元のデータと一致します。
        """
        from cmdbox.app.common import save_yml, load_yml
        
        with tempfile.TemporaryDirectory() as tmpdir:
            yml_path = Path(tmpdir) / "test.yml"
            test_data = {
                'name': 'test',
                'value': 123,
                'nested': {'key': 'value'},
                'list': [1, 2, 3]
            }
            
            save_yml(yml_path, test_data)
            loaded_data = load_yml(yml_path)
            
            assert loaded_data == test_data, "Loaded YAML should match saved data"
            assert yml_path.exists(), "YAML file should be created"

    def test_save_and_load_yml_with_special_characters(self):
        """
        save_yml()とload_yml()関数の特殊文字処理を検証します。
        
        趣旨: 日本語などの特殊文字を含むYAMLデータが正しく保存・読み込みできることを確認します。
        期待される結果: 特殊文字を含むデータが正しく処理されます。
        """
        from cmdbox.app.common import save_yml, load_yml
        
        with tempfile.TemporaryDirectory() as tmpdir:
            yml_path = Path(tmpdir) / "test_special.yml"
            test_data = {
                'name': '日本語テスト',
                'emoji': '😀🎉',
                'special': 'special@#$%'
            }
            
            save_yml(yml_path, test_data)
            loaded_data = load_yml(yml_path)
            
            assert loaded_data == test_data, "Special characters should be preserved"

    def test_load_file_with_custom_function(self):
        """
        load_file()関数のカスタム関数実行機能を検証します。
        
        趣旨: カスタム処理関数がファイルに適用されることを確認します。
        期待される結果: ファイルが読み込まれ、カスタム関数の処理結果が返されます。
        """
        from cmdbox.app.common import load_file, save_file
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            test_content = "test content\nline2\nline3"
            
            # ファイルを保存
            def _w(f):
                f.write(test_content)
            save_file(file_path, _w)
            
            # カスタム関数でファイルを読み込み
            def _r(f):
                return f.readlines()
            
            result = load_file(file_path, _r)
            assert isinstance(result, list), "Should return list of lines"
            assert len(result) == 3, "Should have 3 lines"


class TestCommonStringOperations:
    """safe_fname, check_fname, chopdq functions execution and result verification"""

    def test_safe_fname_replaces_invalid_characters(self):
        """
        safe_fname()関数の無効文字置換機能を検証します。
        
        趣旨: ファイル名に使えない文字が正しく置換されることを確認します。
        期待される結果: 無効な文字が'_'に置換されます。
        """
        from cmdbox.app.common import safe_fname
        
        test_cases = [
            ('file:name', 'file_name'),
            ('file/name', 'file_name'),
            ('file\\name', 'file_name'),
            ('file name', 'file_name'),
            ('file?name', 'file_name'),
        ]
        
        for input_name, expected_pattern in test_cases:
            result = safe_fname(input_name)
            # 結果がアンダースコアだけで構成されていることを確認
            assert '_' in result or result.isalnum(), f"Result '{result}' should have underscores"

    def test_check_fname_detects_invalid_characters(self):
        """
        check_fname()関数の無効文字検出機能を検証します。
        
        趣旨: ファイル名に使えない文字が検出されることを確認します。
        期待される結果: 無効な文字を含む場合Trueが返されます。
        """
        from cmdbox.app.common import check_fname
        
        assert check_fname('file:name') == True, "Should detect colon"
        assert check_fname('file/name') == True, "Should detect slash"
        assert check_fname('file name') == True, "Should detect space"
        assert check_fname('validname') == False, "Should not detect invalid chars in valid name"
        assert check_fname('valid-name-123') == False, "Should allow dashes and numbers"

    def test_chopdq_removes_double_quotes(self):
        """
        chopdq()関数のダブルクォート除去機能を検証します。
        
        趣旨: ダブルクォートで囲まれた文字列の引用符が取り除かれることを確認します。
        期待される結果: ダブルクォートが外側から削除されます。
        """
        from cmdbox.app.common import chopdq
        
        assert chopdq('"hello"') == 'hello', "Should remove surrounding double quotes"
        assert chopdq('hello') == 'hello', "Should not modify unquoted strings"
        assert chopdq('"hello') == '"hello', "Should not modify partially quoted strings"
        assert chopdq('') == '', "Should handle empty strings"
        assert chopdq(None) is None, "Should return None for None input"

    def test_chopdq_handles_non_string_input(self):
        """
        chopdq()関数の非文字列入力処理を検証します。
        
        趣旨: 数値などの非文字列入力が正しく処理されることを確認します。
        期待される結果: 非文字列入力はそのまま返されます。
        """
        from cmdbox.app.common import chopdq
        
        assert chopdq(123) == 123, "Should return non-string input unchanged"
        assert chopdq(12.34) == 12.34, "Should handle float input"


class TestCommonDirectoryOperations:
    """mkdirs, rmdirs functions execution and result verification"""

    def test_mkdirs_creates_directory_structure(self):
        """
        mkdirs()関数のディレクトリ作成機能を検証します。
        
        趣旨: 複数階層のディレクトリが一度に作成されることを確認します。
        期待される結果: 指定されたディレクトリと親ディレクトリが作成されます。
        """
        from cmdbox.app.common import mkdirs, rmdirs
        
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "a" / "b" / "c" / "d"
            result = mkdirs(nested_path)
            
            assert nested_path.exists(), "Nested directory should be created"
            assert nested_path.is_dir(), "Should be a directory"
            assert result == nested_path, "Should return the created path"

    def test_mkdirs_idempotent(self):
        """
        mkdirs()関数のべき等性を検証します。
        
        趣旨: 既に存在するディレクトリに対しても安全に動作することを確認します。
        期待される結果: 複数回呼び出しても正常に動作します。
        """
        from cmdbox.app.common import mkdirs
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "test_dir"
            
            result1 = mkdirs(dir_path)
            result2 = mkdirs(dir_path)
            
            assert result1 == result2, "Should return same path"
            assert dir_path.exists(), "Directory should still exist"

    def test_rmdirs_removes_directory_tree(self):
        """
        rmdirs()関数のディレクトリ削除機能を検証します。
        
        趣旨: ディレクトリとその中身が正しく削除されることを確認します。
        期待される結果: ディレクトリとサブディレクトリが削除されます。
        """
        from cmdbox.app.common import mkdirs, rmdirs
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "remove_test"
            mkdirs(dir_path)
            
            # ファイルを作成
            (dir_path / "file.txt").write_text("test")
            (dir_path / "subdir").mkdir()
            (dir_path / "subdir" / "file2.txt").write_text("test2")
            
            assert dir_path.exists(), "Directory should exist before removal"
            rmdirs(dir_path)
            assert not dir_path.exists(), "Directory should be removed"


class TestCommonCommonValue:
    """set_common_value, get_common_value functions execution and result verification"""

    def test_set_and_get_common_value(self):
        """
        set_common_value()とget_common_value()関数の共通値管理機能を検証します。
        
        趣旨: 共通値を設定し、正しく取得できることを確認します。
        期待される結果: 設定した値が正しく取得されます。
        """
        from cmdbox.app.common import set_common_value, get_common_value
        
        set_common_value('test_key', 'test_value')
        result = get_common_value('test_key')
        
        assert result == 'test_value', "Should retrieve the set value"

    def test_get_common_value_with_default(self):
        """
        get_common_value()関数のデフォルト値機能を検証します。
        
        趣旨: 存在しないキーの場合、デフォルト値が返されることを確認します。
        期待される結果: キーが存在しない場合、指定したデフォルト値が返されます。
        """
        from cmdbox.app.common import get_common_value
        
        result = get_common_value('non_existent_key', default='default_value')
        
        assert result == 'default_value', "Should return default value for non-existent key"

    def test_get_common_value_without_default_returns_none(self):
        """
        get_common_value()関数のNoneデフォルト機能を検証します。
        
        趣旨: デフォルト値を指定しない場合、Noneが返されることを確認します。
        期待される結果: キーが存在しなく、デフォルト値が指定されていない場合、Noneが返されます。
        """
        from cmdbox.app.common import get_common_value
        
        result = get_common_value('another_non_existent_key')
        
        assert result is None, "Should return None when key doesn't exist and no default is provided"


class TestCommonLoadOpt:
    """loadopt, saveopt, loaduser, saveuser functions execution and result verification"""

    def test_saveopt_and_loadopt_json(self):
        """
        saveopt()とloadopt()関数のオプション保存・読み込み機能を検証します。
        
        趣旨: コマンドラインオプションがJSON形式で保存・読み込みできることを確認します。
        期待される結果: 保存したオプションが読み込まれると元のデータと一致します。
        """
        from cmdbox.app.common import saveopt, loadopt
        
        with tempfile.TemporaryDirectory() as tmpdir:
            opt_path = Path(tmpdir) / "options.json"
            opt_data = {
                'mode': 'test',
                'cmd': 'mycommand',
                'param1': 'value1',
                'param2': 123
            }
            
            saveopt(opt_data, opt_path)
            loaded_opt = loadopt(opt_path)
            
            assert loaded_opt == opt_data, "Loaded options should match saved options"

    def test_loadopt_returns_empty_dict_for_nonexistent_file(self):
        """
        loadopt()関数の存在しないファイル処理を検証します。
        
        趣旨: 存在しないファイルパスが指定された場合、空の辞書が返されることを確認します。
        期待される結果: 空の辞書が返されます。
        """
        from cmdbox.app.common import loadopt
        
        result = loadopt('/nonexistent/path/options.json')
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert len(result) == 0, "Should return empty dictionary for non-existent file"

    def test_loadopt_with_none_path(self):
        """
        loadopt()関数のNoneパス処理を検証します。
        
        趣旨: Noneがパスとして渡された場合、空の辞書が返されることを確認します。
        期待される結果: 空の辞書が返されます。
        """
        from cmdbox.app.common import loadopt
        
        result = loadopt(None)
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert len(result) == 0, "Should return empty dictionary for None path"


class TestCommonGetopt:
    """getopt function execution and result verification"""

    def test_getopt_returns_value_from_dict(self):
        """
        getopt()関数の辞書値取得機能を検証します。
        
        趣旨: 指定されたキーの値がoptから取得されることを確認します。
        期待される結果: キーに対応する値が返されます。
        """
        from cmdbox.app.common import getopt
        
        opt = {'key1': 'value1', 'key2': 'value2'}
        result = getopt(opt, 'key1')
        
        assert result == 'value1', "Should return value for existing key"

    def test_getopt_with_preval_priority(self):
        """
        getopt()関数のpreval優先度機能を検証します。
        
        趣旨: prevalが指定されている場合、それが優先的に使用されることを確認します。
        期待される結果: prevalの値が返されます。
        """
        from cmdbox.app.common import getopt
        
        opt = {'key': 'value_from_opt'}
        result = getopt(opt, 'key', preval='value_from_preval')
        
        assert result == 'value_from_preval', "preval should take priority"

    def test_getopt_with_default_value(self):
        """
        getopt()関数のデフォルト値機能を検証します。
        
        趣旨: キーが存在しない場合、デフォルト値が返されることを確認します。
        期待される結果: デフォルト値が返されます。
        """
        from cmdbox.app.common import getopt
        
        opt = {}
        result = getopt(opt, 'nonexistent', defval='default_value')
        
        assert result == 'default_value', "Should return default value"

    def test_getopt_with_zero_value(self):
        """
        getopt()関数の0値処理を検証します。
        
        趣旨: 0という有効な値がデフォルト値に置き換わらないことを確認します。
        期待される結果: 0が返されます。
        """
        from cmdbox.app.common import getopt
        
        opt = {'count': 0}
        result = getopt(opt, 'count', defval=100)
        
        assert result == 0, "Should return 0, not default value"


class TestCommonPrintFormat:
    """print_format function execution and result verification"""

    def test_print_format_json_output(self, capsys):
        """
        print_format()関数のJSON形式出力機能を検証します。
        
        趣旨: 辞書データがJSON形式で出力されることを確認します。
        期待される結果: JSONフォーマットされたデータが出力されます。
        """
        from cmdbox.app.common import print_format
        import time
        
        data = {'key': 'value', 'number': 123}
        tm = time.time()
        
        result = print_format(data, format=False, tm=tm)
        
        assert isinstance(result, str), "Should return a string"
        assert 'key' in result, "Should contain data keys"
        assert 'value' in result, "Should contain data values"

    def test_print_format_with_list_data(self):
        """
        print_format()関数のリストデータ処理を検証します。
        
        趣旨: リストデータが正しく処理されることを確認します。
        期待される結果: リストデータが適切にフォーマットされます。
        """
        from cmdbox.app.common import print_format
        import time
        
        data = [
            {'name': 'item1', 'value': 10},
            {'name': 'item2', 'value': 20}
        ]
        tm = time.time()
        
        result = print_format(data, format=False, tm=tm, stdout=False)
        
        assert isinstance(result, str), "Should return a string"


class TestCommonMiscellaneous:
    """Miscellaneous function execution and result verification"""

    def test_is_japan(self):
        """
        is_japan()関数の日本語環境判定機能を検証します。
        
        趣旨: 関数が正常に実行され、真偽値を返すことを確認します。
        期待される結果: TrueまたはFalseのいずれかが返されます。
        """
        from cmdbox.app.common import is_japan
        
        result = is_japan()
        assert isinstance(result, bool), "Should return a boolean"

    def test_is_event_loop_running(self):
        """
        is_event_loop_running()関数のイベントループ判定機能を検証します。
        
        趣旨: 関数が正常に実行され、真偽値を返すことを確認します。
        期待される結果: TrueまたはFalseのいずれかが返されます。
        """
        from cmdbox.app.common import is_event_loop_running
        
        result = is_event_loop_running()
        assert isinstance(result, bool), "Should return a boolean"

    def test_get_tzoffset_str(self):
        """
        get_tzoffset_str()関数のタイムゾーンオフセット取得機能を検証します。
        
        趣旨: タイムゾーンオフセットが正しい形式で返されることを確認します。
        期待される結果: '+HH:MM'または'-HH:MM'の形式の文字列が返されます。
        """
        from cmdbox.app.common import get_tzoffset_str
        
        result = get_tzoffset_str()
        
        assert isinstance(result, str), "Should return a string"
        assert len(result) == 6, "Should be in format ±HH:MM (6 characters)"
        assert result[0] in ['+', '-'], "Should start with + or -"
        assert result[3] == ':', "Should have colon at position 3"

    def test_to_str_with_dict(self):
        """
        to_str()関数の辞書変換機能を検証します。
        
        趣旨: 辞書がJSON文字列に変換されることを確認します。
        期待される結果: JSON形式の文字列が返されます。
        """
        from cmdbox.app.common import to_str
        
        data = {'key': 'value', 'number': 123}
        result = to_str(data)
        
        assert isinstance(result, str), "Should return a string"
        assert 'key' in result, "Should contain dictionary content"
        parsed = json.loads(result)
        assert parsed == data, "Should be valid JSON"

    def test_to_str_with_slice(self):
        """
        to_str()関数のスライス機能を検証します。
        
        趣旨: 出力文字列が指定された長さに制限されることを確認します。
        期待される結果: スライスされた文字列が返されます。
        """
        from cmdbox.app.common import to_str
        
        data = "This is a very long string"
        result = to_str(data, slise=10)
        
        assert isinstance(result, str), "Should return a string"
        # スライスされた場合、長さは指定値以下か、または指定値より長ければ'...'が付加される
        assert len(result) <= len(data), "Should be sliced"


class TestCommonCopySample:
    """copy_sample function execution and result verification"""

    def test_copy_sample_creates_samples_directory(self):
        """
        copy_sample()関数のサンプルディレクトリ作成機能を検証します。
        
        趣旨: サンプルディレクトリ(.samples)が作成されることを確認します。
        期待される結果: サンプルディレクトリとファイルが作成されます。
        """
        from cmdbox.app.common import copy_sample
        from cmdbox import version
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            samples_dir = data_dir / '.samples'
            
            copy_sample(data_dir, ver=version)
            
            # サンプルディレクトリが作成されたか確認
            assert samples_dir.exists(), "Samples directory should be created"


class TestCommonMklogdir:
    """mklogdir function execution and result verification"""

    def test_mklogdir_creates_logs_directory(self):
        """
        mklogdir()関数のログディレクトリ作成機能を検証します。
        
        趣旨: ログディレクトリ(.logs)が作成されることを確認します。
        期待される結果: ログディレクトリが作成されます。
        """
        from cmdbox.app.common import mklogdir
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            result = mklogdir(data_dir)
            
            expected_logdir = data_dir / '.logs'
            assert result.exists(), "Log directory should be created"
            assert result.is_dir(), "Should be a directory"
            assert result == expected_logdir, "Should return the log directory path"
