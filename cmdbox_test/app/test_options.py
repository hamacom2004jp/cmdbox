"""
Test cases for cmdbox.app.options module

This file contains tests that execute actual Options class methods and verify their results.
Methods are called with properly mocked dependencies to ensure real execution and result validation.
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
from typing import Dict, Any, List


def setup_options_environment():
    """Helper to setup Options environment by clearing cached modules and mocking dependencies."""
    # Remove cached modules to prevent circular import issues
    for mod in list(sys.modules.keys()):
        if mod.startswith('cmdbox'):
            del sys.modules[mod]
    
    # Create a mock common module with necessary functions
    mock_common = MagicMock()
    mock_common.default_logger = MagicMock(return_value=MagicMock(spec=logging.Logger))
    mock_common.save_yml = MagicMock()
    mock_common.load_yml = MagicMock(return_value={})
    mock_common.is_japan = MagicMock(return_value=False)
    mock_common.get_tzoffset_str = MagicMock(return_value='+00:00')
    mock_common.chopdq = lambda x: x
    mock_common.to_str = lambda x, max_len=None: str(x)
    
    # Create a mock feature module
    mock_feature = MagicMock()
    
    # Create a mock commons.module
    mock_commons_module = MagicMock()
    mock_commons_module.load_features = MagicMock(return_value={})
    
    mock_commons = MagicMock()
    mock_commons.module = mock_commons_module
    
    return patch.dict('sys.modules', {
        'cmdbox.app.common': mock_common,
        'cmdbox.app.feature': mock_feature,
        'cmdbox.app.commons': mock_commons,
        'cmdbox.app.commons.module': mock_commons_module,
        'cmdbox.app.web': MagicMock(),
    })


class TestOptionsInitialization:
    """Options class initialization and getInstance functionality"""

    def test_options_get_instance_creates_singleton(self):
        """
        getInstance()メソッドのシングルトンパターン実装を検証します。
        
        趣旨: 複数回getInstance()を呼び出した場合、同じインスタンスが返されることを確認します。
        期待される結果: 同じインスタンスが返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            instance1 = Options.getInstance()
            instance2 = Options.getInstance()
            
            assert instance1 is instance2, "getInstance should return the same instance (singleton pattern)"

    def test_options_init_creates_default_options(self):
        """
        __init__()メソッドがデフォルトオプションを初期化することを検証します。
        
        趣旨: Options インスタンスが作成されるとき、_options辞書にデフォルトオプションが設定されることを確認します。
        期待される結果: version, debug, mode, cmd などの基本的なオプションが_options に含まれます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            assert hasattr(options, '_options'), "Options should have _options attribute"
            assert isinstance(options._options, dict), "_options should be a dictionary"
            assert 'version' in options._options, "version option should be initialized"
            assert 'debug' in options._options, "debug option should be initialized"
            assert 'mode' in options._options, "mode option should be initialized"
            assert 'cmd' in options._options, "cmd option should be initialized"


class TestOptionsTypeConstants:
    """Test type constant definitions"""

    def test_options_type_constants_defined(self):
        """
        型定数がすべて定義されていることを検証します。
        
        趣旨: Options クラスに必要なすべての型定数が定義されていることを確認します。
        期待される結果: T_INT, T_FLOAT, T_BOOL, T_STR などすべての型定数が定義されています。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Check all type constants are defined
            assert Options.T_INT == 'int'
            assert Options.T_FLOAT == 'float'
            assert Options.T_BOOL == 'bool'
            assert Options.T_STR == 'str'
            assert Options.T_DATE == 'date'
            assert Options.T_DATETIME == 'datetime'
            assert Options.T_DICT == 'dict'
            assert Options.T_TEXT == 'text'
            assert Options.T_FILE == 'file'
            assert Options.T_DIR == 'dir'
            assert Options.T_PASSWD == 'passwd'
            assert Options.T_MLIST == 'mlist'


class TestOptionsGetModeKeys:
    """get_mode_keys method execution and result verification"""

    def test_get_mode_keys_returns_empty_list_for_default_options(self):
        """
        get_mode_keys()メソッドがモードキーのリストを返すことを検証します。
        
        趣旨: mode オプションから辞書型の値のキーを抽出できることを確認します。
        期待される結果: リストが返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method
            mode_keys = options.get_mode_keys()
            
            assert isinstance(mode_keys, list), "get_mode_keys should return a list"


class TestOptionsGetModes:
    """get_modes method execution and result verification"""

    def test_get_modes_returns_list(self):
        """
        get_modes()メソッドが起動モードの選択肢を返すことを検証します。
        
        趣旨: get_modes() を呼び出した際にリストが返されることを確認します。
        期待される結果: リスト（空の文字列を含む）が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method
            modes = options.get_modes()
            
            assert isinstance(modes, list), "get_modes should return a list"
            # First element should be empty string
            assert modes[0] == '', "First element should be empty string"


class TestOptionsGetCmdKeys:
    """get_cmd_keys method execution and result verification"""

    def test_get_cmd_keys_returns_empty_list_for_unknown_mode(self):
        """
        get_cmd_keys()メソッドが未知のモードに対して空リストを返すことを検証します。
        
        趣旨: 存在しないモードを指定した場合、空のリストが返されることを確認します。
        期待される結果: 空のリスト [] が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method with non-existent mode
            cmd_keys = options.get_cmd_keys('unknown_mode')
            
            assert isinstance(cmd_keys, list), "get_cmd_keys should return a list"
            assert len(cmd_keys) == 0, "Should return empty list for unknown mode"


class TestOptionsGetCmds:
    """get_cmds method execution and result verification"""

    def test_get_cmds_returns_error_message_for_unknown_mode(self):
        """
        get_cmds()メソッドが未知のモードに対してエラーメッセージを返すことを検証します。
        
        趣旨: 存在しないモードを指定した場合、エラーメッセージを含むリストが返されることを確認します。
        期待される結果: 'Please select mode.' というメッセージを含むリストが返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method with non-existent mode
            cmds = options.get_cmds('unknown_mode')
            
            assert isinstance(cmds, list), "get_cmds should return a list"
            assert 'Please select mode.' in cmds, "Should return error message for unknown mode"


class TestOptionsGetCmdAttr:
    """get_cmd_attr method execution and result verification"""

    def test_get_cmd_attr_returns_error_for_unknown_mode(self):
        """
        get_cmd_attr()メソッドが未知のモードに対してエラーメッセージを返すことを検証します。
        
        趣旨: 存在しないモードを指定した場合、エラーメッセージを含むリストが返されることを確認します。
        期待される結果: 'Unknown mode.' というメッセージを含むリストが返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method with non-existent mode
            result = options.get_cmd_attr('unknown_mode', 'cmd', 'attr')
            
            assert isinstance(result, list), "get_cmd_attr should return a list for unknown mode"
            assert f'Unknown mode.' in result[0], "Should return error message for unknown mode"

    def test_get_cmd_attr_returns_empty_list_for_empty_cmd(self):
        """
        get_cmd_attr()メソッドが空のコマンド指定に対して空リストを返すことを検証します。
        
        趣旨: cmd が空文字列のとき、空のリストが返されることを確認します。
        期待される結果: [] が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Add a test mode
            options._options['cmd']['test_mode'] = {}
            
            # Call the method with empty cmd
            result = options.get_cmd_attr('test_mode', '', 'attr')
            
            assert isinstance(result, list), "get_cmd_attr should return a list"
            assert len(result) == 0, "Should return empty list for empty command"


class TestOptionsGetSvcmdFeature:
    """get_svcmd_feature method execution and result verification"""

    def test_get_svcmd_feature_returns_none_for_empty_svcmd(self):
        """
        get_svcmd_feature()メソッドが空の svcmd に対して None を返すことを検証します。
        
        趣旨: svcmd が None または空文字列のとき、None が返されることを確認します。
        期待される結果: None が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method with None
            result = options.get_svcmd_feature(None)
            assert result is None, "Should return None for None svcmd"
            
            # Call the method with empty string
            result = options.get_svcmd_feature('')
            assert result is None, "Should return None for empty string svcmd"

    def test_get_svcmd_feature_returns_none_for_unknown_svcmd(self):
        """
        get_svcmd_feature()メソッドが未知の svcmd に対して None を返すことを検証します。
        
        趣旨: _options['svcmd'] に存在しない svcmd を指定した場合、None が返されることを確認します。
        期待される結果: None が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Initialize svcmd dict if not present
            if 'svcmd' not in options._options:
                options._options['svcmd'] = {}
            
            # Call the method with unknown svcmd
            result = options.get_svcmd_feature('unknown_svcmd')
            
            assert result is None, "Should return None for unknown svcmd"


class TestOptionsListOptions:
    """list_options method execution and result verification"""

    def test_list_options_returns_dict(self):
        """
        list_options()メソッドが辞書型のオプション一覧を返すことを検証します。
        
        趣旨: list_options() を呼び出した際に辞書が返されることを確認します。
        期待される結果: 辞書が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method
            result = options.list_options()
            
            assert isinstance(result, dict), "list_options should return a dictionary"

    def test_list_options_contains_default_options(self):
        """
        list_options()メソッドがデフォルトオプションを含むことを検証します。
        
        趣旨: 返されたオプション一覧に version, debug などのデフォルトオプションが含まれることを確認します。
        期待される結果: version, debug オプションが含まれます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method
            result = options.list_options()
            
            assert 'version' in result, "list_options should contain version option"
            assert 'debug' in result, "list_options should contain debug option"


class TestOptionsIsFeaturesLoaded:
    """is_features_loaded method execution and result verification"""

    def test_is_features_loaded_returns_false_for_unloaded_feature(self):
        """
        is_features_loaded()メソッドが未読み込みフィーチャーに対して False を返すことを検証します。
        
        趣旨: features_loaded に存在しないフィーチャータイプを指定した場合、False が返されることを確認します。
        期待される結果: False が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method
            result = options.is_features_loaded('unknown_feature')
            
            assert result is False, "is_features_loaded should return False for unloaded feature"

    def test_is_features_loaded_returns_true_for_loaded_feature(self):
        """
        is_features_loaded()メソッドが読み込み済みフィーチャーに対して True を返すことを検証します。
        
        趣旨: features_loaded に存在するフィーチャータイプを指定した場合、True が返されることを確認します。
        期待される結果: True が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Set a feature as loaded
            options.features_loaded['test_feature'] = True
            
            # Call the method
            result = options.is_features_loaded('test_feature')
            
            assert result is True, "is_features_loaded should return True for loaded feature"


class TestOptionsCheckAgentrule:
    """check_agentrule method execution and result verification"""

    def test_check_agentrule_returns_false_when_not_loaded(self):
        """
        check_agentrule()メソッドがagentruleが未読み込みの場合 False を返すことを検証します。
        
        趣旨: agentrule_loaded が False のとき、check_agentrule() が False を返すことを確認します。
        期待される結果: False が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.level = logging.INFO
            
            # Ensure agentrule is not loaded
            options.agentrule_loaded = False
            
            # Call the method
            result = options.check_agentrule('test_mode', 'test_cmd', mock_logger)
            
            assert result is False, "check_agentrule should return False when not loaded"


class TestOptionsSetAttr:
    """__setattr__ method execution and result verification"""

    def test_setattr_prevents_type_constant_modification(self):
        """
        __setattr__()メソッドが型定数の再設定を防ぐことを検証します。
        
        趣旨: T_ で始まる属性が既に存在する場合、再設定できないことを確認します。
        期待される結果: ValueError が発生し、属性が変更されていません。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # T_INT is already in __dict__, try to modify it
            # The __setattr__ checks if name.startswith('T_') and is already in __dict__
            with pytest.raises(ValueError, match="Cannot set attribute"):
                # Force the attribute to exist first by directly setting it in __dict__
                options.__dict__['T_NEW'] = 'original'
                # Now try to modify it via __setattr__
                options.T_NEW = 'modified'

    def test_setattr_allows_regular_attributes(self):
        """
        __setattr__()メソッドが通常の属性の設定を許可することを検証します。
        
        趣旨: T_ で始まらない属性は通常通り設定できることを確認します。
        期待される結果: 属性が正常に設定されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Set a regular attribute
            options.test_attr = 'test_value'
            
            assert options.test_attr == 'test_value', "Regular attributes should be settable"


class TestOptionsGetCmdChoices:
    """get_cmd_choices method execution and result verification"""

    def test_get_cmd_choices_returns_list(self):
        """
        get_cmd_choices()メソッドが選択肢リストを返すことを検証します。
        
        趣旨: mode と cmd を指定した場合、オプション選択肢のリストが返されることを確認します。
        期待される結果: リストが返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Call the method with test_mode and test_cmd
            options._options['cmd']['test_mode'] = {'test_cmd': {'choice': []}}
            
            result = options.get_cmd_choices('test_mode', 'test_cmd')
            
            assert isinstance(result, list), "get_cmd_choices should return a list"

    def test_get_cmd_choices_masks_password_in_webmode(self):
        """
        get_cmd_choices()メソッドがWebモードでパスワードをマスクすることを検証します。
        
        趣旨: webmode=True でかつ 'web'='mask' の場合、default値が '********' に置換されることを確認します。
        期待される結果: マスクされた選択肢が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Create a test option with web masking
            test_choice = [
                {'opt': 'password', 'web': 'mask', 'default': 'secret123'}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            result = options.get_cmd_choices('test_mode', 'test_cmd', webmode=True)
            
            assert len(result) > 0, "Should return at least one choice"
            assert result[0]['default'] == '********', "Password should be masked with '********'"

    def test_get_cmd_choices_preserves_original_in_non_webmode(self):
        """
        get_cmd_choices()メソッドが非Webモードで元のデータを保持することを検証します。
        
        趣旨: webmode=False の場合、元の default 値が変更されないことを確認します。
        期待される結果: 元の default 値が保持されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Create a test option with web masking
            test_choice = [
                {'opt': 'password', 'web': 'mask', 'default': 'secret123'}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            result = options.get_cmd_choices('test_mode', 'test_cmd', webmode=False)
            
            assert len(result) > 0, "Should return at least one choice"
            assert result[0]['default'] == 'secret123', "Password should not be masked in non-webmode"


class TestOptionsGetCmdOpt:
    """get_cmd_opt method execution and result verification"""

    def test_get_cmd_opt_returns_matching_option(self):
        """
        get_cmd_opt()メソッドがマッチするオプションを返すことを検証します。
        
        趣旨: 指定された opt パラメータにマッチするオプション辞書が返されることを確認します。
        期待される結果: マッチするオプション辞書が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Create a test option
            test_choice = [
                {'opt': 'test_opt1', 'type': 'str', 'default': 'value1'},
                {'opt': 'test_opt2', 'type': 'int', 'default': 'value2'}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            result = options.get_cmd_opt('test_mode', 'test_cmd', 'test_opt1')
            
            assert result is not None, "Should return a matching option"
            assert result['opt'] == 'test_opt1', "Should return the correct option"
            assert result['default'] == 'value1', "Should return the correct value"

    def test_get_cmd_opt_returns_none_for_nonexistent_option(self):
        """
        get_cmd_opt()メソッドが存在しないオプションに対して None を返すことを検証します。
        
        趣旨: 指定された opt が存在しない場合、None が返されることを確認します。
        期待される結果: None が返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Create a test option
            test_choice = [
                {'opt': 'test_opt1', 'type': 'str', 'default': 'value1'}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            result = options.get_cmd_opt('test_mode', 'test_cmd', 'nonexistent')
            
            assert result is None, "Should return None for non-existent option"


class TestOptionsListOptions:
    """list_options method detailed validation"""

    def test_list_options_contains_correct_types_for_int(self):
        """
        list_options()メソッドが INT 型オプションを正しく処理することを検証します。
        
        趣旨: T_INT 型のオプションが Python の int 型に変換されることを確認します。
        期待される結果: type フィールドが int で、action が適切に設定されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            result = options.list_options()
            
            # Check that type conversions are correct
            for key, opt in result.items():
                if opt.get('type') == int:
                    assert 'action' in opt, f"Option {key} should have action field"

    def test_list_options_builds_opts_array_correctly(self):
        """
        list_options()メソッドが opts 配列を正しく構築することを検証します。
        
        趣旨: opts 配列に短いフラグと長いフラグが含まれることを確認します。
        期待される結果: opts 配列は ['--key'] または ['-s', '--key'] の形式です。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            result = options.list_options()
            
            # Check version option has both short and long forms
            assert 'version' in result, "version should be in list_options"
            assert 'opts' in result['version'], "version should have opts field"
            assert isinstance(result['version']['opts'], list), "opts should be a list"
            assert '--version' in result['version']['opts'], "opts should contain --version"
            assert '-v' in result['version']['opts'], "opts should contain -v (short form)"

    def test_list_options_handles_multi_flag_correctly(self):
        """
        list_options()メソッドが multi フラグを正しく処理することを検証します。
        
        趣旨: multi=True のオプションは action が 'append' に設定されることを確認します。
        期待される結果: multi が True の場合、action は 'append' です。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            result = options.list_options()
            
            # Check tag option which has multi=True
            assert 'tag' in result, "tag should be in list_options"
            assert result['tag']['action'] == 'append', "tag should have append action since multi=True"


class TestOptionsMkOptList:
    """mk_opt_list method execution and result verification"""

    def test_mk_opt_list_creates_option_list(self):
        """
        mk_opt_list()メソッドがオプションリストを作成することを検証します。
        
        趣旨: 引数辞書をコマンドラインオプションリストに変換できることを確認します。
        期待される結果: オプションリストと ファイル辞書のタプルが返されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Create a simple opt dictionary
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd'
            }
            
            # Call the method
            result = options.mk_opt_list(opt)
            
            assert isinstance(result, tuple), "mk_opt_list should return a tuple"
            assert len(result) == 2, "Tuple should have 2 elements (opt_list, file_dict)"
            
            opt_list, file_dict = result
            
            assert isinstance(opt_list, list), "opt_list should be a list"
            assert isinstance(file_dict, dict), "file_dict should be a dictionary"
            assert '-m' in opt_list, "opt_list should contain -m flag"
            assert 'test_mode' in opt_list, "opt_list should contain mode value"

    def test_mk_opt_list_handles_string_values_correctly(self):
        """
        mk_opt_list()メソッドが文字列値を正しく処理することを検証します。
        
        趣旨: スペースを含まない文字列値は引用符なしで、スペースを含む場合は引用符付きで処理されることを確認します。
        期待される結果: スペースなし値は引用符なし、スペースあり値は引用符付きで出力されます。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Setup test mode and cmd with schema
            test_choice = [
                {'opt': 'name', 'type': 'str', 'default': None}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            # Test with string without spaces
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd',
                'name': 'simple_value'
            }
            
            opt_list, _ = options.mk_opt_list(opt)
            
            assert '--name' in opt_list, "Option flag should be present"
            assert 'simple_value' in opt_list, "Simple value should be present without quotes"

    def test_mk_opt_list_quotes_strings_with_spaces(self):
        """
        mk_opt_list()メソッドがスペース含む文字列を引用符で囲むことを検証します。
        
        趣旨: スペースを含む値が二重引用符で囲まれることを確認します。
        期待される結果: スペース含む値は "..." の形式になります。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Setup test mode and cmd with schema
            test_choice = [
                {'opt': 'name', 'type': 'str', 'default': None}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            # Test with string with spaces
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd',
                'name': 'value with spaces'
            }
            
            opt_list, _ = options.mk_opt_list(opt)
            
            assert '"value with spaces"' in opt_list, "Value with spaces should be quoted"

    def test_mk_opt_list_handles_boolean_values(self):
        """
        mk_opt_list()メソッドがブール値を正しく処理することを検証します。
        
        趣旨: T_BOOL 型のオプションが True の場合、フラグのみ追加されることを確認します。
        期待される結果: True の場合はフラグが追加、False の場合はフラグが追加されません。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Setup test mode and cmd with boolean schema
            test_choice = [
                {'opt': 'verbose', 'type': Options.T_BOOL, 'default': False}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            # Test with True value
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd',
                'verbose': True
            }
            
            opt_list, _ = options.mk_opt_list(opt)
            
            assert '--verbose' in opt_list, "Boolean True should add flag"
            
            # Test with False value
            opt['verbose'] = False
            opt_list, _ = options.mk_opt_list(opt)
            
            assert '--verbose' not in opt_list, "Boolean False should not add flag"

    def test_mk_opt_list_handles_list_values(self):
        """
        mk_opt_list()メソッドがリスト値を正しく処理することを検証します。
        
        趣旨: リスト型の値は各要素ごとにフラグが追加されることを確認します。
        期待される結果: リストの各要素が個別の --key value ペアになります。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Setup test mode and cmd with list schema
            test_choice = [
                {'opt': 'tags', 'type': 'str', 'multi': True, 'default': None}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            # Test with list value
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd',
                'tags': ['tag1', 'tag2', 'tag3']
            }
            
            opt_list, _ = options.mk_opt_list(opt)
            
            # Count how many times --tags appears
            tags_count = opt_list.count('--tags')
            assert tags_count == 3, "Should have --tags flag for each tag value"
            assert 'tag1' in opt_list, "tag1 should be in option list"
            assert 'tag2' in opt_list, "tag2 should be in option list"
            assert 'tag3' in opt_list, "tag3 should be in option list"

    def test_mk_opt_list_handles_dict_values(self):
        """
        mk_opt_list()メソッドが辞書値を正しく処理することを検証します。
        
        趣旨: 辞書型の値が key=value の形式で処理されることを確認します。
        期待される結果: 辞書の各キーバリューペアが --key k=v の形式になります。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Setup test mode and cmd with dict schema
            test_choice = [
                {'opt': 'params', 'type': 'dict', 'multi': True, 'default': None}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            # Test with dict value
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd',
                'params': {'key1': 'value1', 'key2': 'value2'}
            }
            
            opt_list, _ = options.mk_opt_list(opt)
            
            # Count how many times --params appears
            params_count = opt_list.count('--params')
            assert params_count == 2, "Should have --params flag for each dict entry"
            assert 'key1=value1' in opt_list, "key1=value1 should be in option list"
            assert 'key2=value2' in opt_list, "key2=value2 should be in option list"

    def test_mk_opt_list_skips_empty_values(self):
        """
        mk_opt_list()メソッドが空の値をスキップすることを検証します。
        
        趣旨: 空文字列、None、または空リスト/辞書の値はオプションリストに追加されないことを確認します。
        期待される結果: 空の値は出力に含まれません。
        """
        with setup_options_environment():
            from cmdbox.app.options import Options
            
            # Reset singleton
            Options._instance = None
            
            options = Options()
            
            # Setup test mode and cmd
            test_choice = [
                {'opt': 'optional1', 'type': 'str', 'default': None},
                {'opt': 'optional2', 'type': 'str', 'default': None}
            ]
            options._options['cmd']['test_mode'] = {
                'test_cmd': {'choice': test_choice}
            }
            
            # Test with empty values
            opt = {
                'mode': 'test_mode',
                'cmd': 'test_cmd',
                'optional1': '',
                'optional2': None
            }
            
            opt_list, _ = options.mk_opt_list(opt)
            
            assert '--optional1' not in opt_list, "Empty string should be skipped"
            assert '--optional2' not in opt_list, "None value should be skipped"
            # Should still have mode and cmd
            assert '-m' in opt_list, "Mode flag should be present"
            assert '-c' in opt_list, "Command flag should be present"
