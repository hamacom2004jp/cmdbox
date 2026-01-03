# cmdbox_test - テストコード

cmdboxのテストコードを格納するディレクトリです。

## 構造

```
cmdbox_test/
├── conftest.py                          # pytest設定とグローバルフィクスチャ
└── app/
    ├── __init__.py
    ├── test_web.py                      # Webモジュールのテスト (19テスト)
    └── features/
        └── cli/
            ├── __init__.py
            ├── test_cmdbox_server_start.py      # ServerStartコマンドテスト (4テスト)
            ├── test_cmdbox_server_list.py       # ServerListコマンドテスト (5テスト)
            ├── test_cmdbox_server_stop.py       # ServerStopコマンドテスト (2テスト)
            ├── test_cmdbox_web_start.py         # WebStartコマンドテスト (3テスト)
            ├── test_cmdbox_web_stop.py          # WebStopコマンドテスト (2テスト)
            └── test_cmdbox_web_user_list.py     # WebUserListコマンドテスト (4テスト)
```

## テスト統計

| カテゴリ | テストファイル | テスト数 | 説明 |
|---------|--------------|---------|------|
| Server CLI | test_cmdbox_server_start.py | 4 | サーバー起動コマンド |
| Server CLI | test_cmdbox_server_list.py | 5 | サーバー一覧表示コマンド |
| Server CLI | test_cmdbox_server_stop.py | 2 | サーバー停止コマンド |
| Web CLI | test_cmdbox_web_start.py | 3 | Web開始コマンド |
| Web CLI | test_cmdbox_web_stop.py | 2 | Web停止コマンド |
| Web CLI | test_cmdbox_web_user_list.py | 4 | Webユーザー一覧表示コマンド |
| Web Module | test_web.py | 12 | Webモジュール動作テスト |
| **合計** | **7ファイル** | **32テスト** | **全テスト成功** |

## テストの実行方法

### 全テストを実行

```bash
# ワークスペースのルートから
.\.venv\Scripts\python.exe -m pytest cmdbox_test/ -v
```

### 特定のテストモジュールを実行

```bash
# ServerStartのテストのみ実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/features/cli/test_cmdbox_server_start.py -v

# ServerListのテストのみ実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/features/cli/test_cmdbox_server_list.py -v

# ServerStopのテストのみ実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/features/cli/test_cmdbox_server_stop.py -v

# WebStartのテストのみ実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/features/cli/test_cmdbox_web_start.py -v

# Webモジュールのテストのみ実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/test_web.py -v
```

### 特定のテストクラスまたはテストメソッドを実行

```bash
# 特定のテストクラスを実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/features/cli/test_cmdbox_server_start.py::TestServerStart -v

# 特定のテストメソッドを実行
.\.venv\Scripts\python.exe -m pytest cmdbox_test/app/features/cli/test_cmdbox_server_start.py::TestServerStart::test_apprun_without_data_option -v
```

## テストカバレッジ

### test_cmdbox_server_start.py (4テスト)

ServerStartコマンドのテストコード。以下をテストしています：

- `test_apprun_without_data_option` - --dataオプション未指定時の警告処理
- `test_apprun_without_svname_option` - --svnameオプション未指定時の警告処理
- `test_apprun_with_valid_args` - 有効な引数でのServerインスタンス化
- `test_is_cluster_redirect` - NotImplementedErrorの発生確認

### test_cmdbox_server_list.py (5テスト)

ServerListコマンドのテストコード。以下をテストしています：

- `test_apprun_list_servers` - サーバーリスト取得の成功処理
- `test_apprun_no_servers_running` - サーバー起動なし時の警告処理
- `test_is_cluster_redirect` - NotImplementedErrorの発生確認
- `test_apprun_returned_object` - Serverオブジェクトの返却確認
- `test_option_descriptions` - オプション説明の存在確認

### test_cmdbox_server_stop.py (2テスト)

ServerStopコマンドのテストコード。以下をテストしています：

- `test_apprun_stop_server` - サーバー停止処理とClientインスタンス化
- `test_is_cluster_redirect` - クラスター転送設定（TrueをチェックするがNotImplementedErrorが発生）

### test_cmdbox_web_start.py (3テスト)

WebStartコマンドのテストコード。以下をテストしています：

- `test_apprun_without_data_option` - --dataオプション未指定時の警告処理
- `test_apprun_with_valid_args` - 有効な引数でのWebインスタンス化と起動処理
- `test_is_cluster_redirect` - NotImplementedErrorの発生確認

### test_cmdbox_web_stop.py (2テスト)

WebStopコマンドのテストコード。以下をテストしています：

- `test_apprun_successful_stop` - Webインスタンス化と停止処理
- `test_is_cluster_redirect` - NotImplementedErrorの発生確認

### test_cmdbox_web_user_list.py (4テスト)

WebUserListコマンドのテストコード。以下をテストしています：

- `test_apprun_without_signin_file_option` - --signin_fileオプション未指定時のエラー処理
- `test_apprun_list_all_users` - user_name未指定時にすべてのユーザーをリスト
- `test_apprun_list_specific_user` - user_name指定時に該当ユーザーをリスト
- `test_is_cluster_redirect` - NotImplementedErrorの発生確認

### test_web.py (12テスト)

cmdbox.app.webモジュールの動作検証テストコード。Web クラスの各メソッドがシグネチャと動作の観点から正しく実装されていることを検証しています：

#### TestWebModuleBasics (2テスト)
- `test_web_module_importable` - webモジュールのインポート確認
- `test_web_class_has_required_methods` - 必要なメソッドの存在確認

#### TestWebGetInstanceMethod (2テスト)
- `test_get_instance_method_exists_and_callable` - getInstance()が存在且つ呼び出し可能であることの確認
- `test_get_instance_method_signature` - getInstance()が可変長引数をサポートしていることの確認

#### TestWebUserListBehavior (1テスト)
- `test_user_list_signature_and_behavior` - user_list()が正しいシグネチャを持ち、nameパラメータがNoneをデフォルト値とすることの確認

#### TestWebChangePasswordBehavior (1テスト)
- `test_change_password_requires_user_parameters` - change_password()がユーザー識別パラメータとパスワード関連パラメータを持つことの確認

#### TestWebApikeyMethodBehavior (1テスト)
- `test_apikey_methods_accept_user_parameter` - apikey_add/del()がユーザー辞書パラメータを受け入れることの確認

#### TestWebUserManagementBehavior (1テスト)
- `test_user_management_methods_have_correct_parameters` - user_add/edit/del()が正しいパラメータを持つことの確認

#### TestWebGroupManagementBehavior (1テスト)
- `test_group_management_methods_have_correct_parameters` - group_list/add/edit/del()が正しいパラメータを持つことの確認

#### TestWebUserDataBehavior (1テスト)
- `test_user_data_has_required_parameters` - user_data()がreq, uid, user_nameなどのパラメータを持つことの確認

#### TestWebServerControlBehavior (1テスト)
- `test_start_and_stop_methods_are_callable` - start/stop()が呼び出し可能であり、startがサーバー設定パラメータを持つことの確認

#### TestWebInitWebfeaturesBehavior (1テスト)
- `test_init_webfeatures_accepts_app_parameter` - init_webfeatures()がappパラメータを持つことの確認

注記: 各テストはメソッドのシグネチャ、パラメータ名、パラメータのデフォルト値を検証し、
メソッドが期待通りに実装されていることを確認しています。循環インポート依存関係を考慮し、
実際の機能テストはCLIコマンドテストを通じて行われています。

## フィクスチャ (conftest.py)

### 提供されるフィクスチャ

- `temp_data_dir` - テンポラリなデータディレクトリ
- `mock_logger` - テスト用ロガー
- `mock_args` - テスト用argparse.Namespace
- `mock_redis_client` - モック化されたRedisクライアント
- `version_mock` - バージョン情報のモック

## 使用技術

- **テストフレームワーク**: pytest
- **モック**: unittest.mock, pytest-mock
- **Python バージョン**: 3.11.8

## テスト実行結果

```
====================================================== test session starts ======================================================
platform win32 -- Python 3.11.8, pytest-9.0.2, pluggy-1.6.0 -- F:\devenv\cmdbox\.venv\Scripts\python.exe

cmdbox_test/app/features/cli/test_cmdbox_server_list.py::TestServerList::test_apprun_list_servers PASSED                   [  2%] 
cmdbox_test/app/features/cli/test_cmdbox_server_list.py::TestServerList::test_apprun_no_servers_running PASSED             [  5%]
cmdbox_test/app/features/cli/test_cmdbox_server_list.py::TestServerList::test_is_cluster_redirect PASSED                   [  7%] 
cmdbox_test/app/features/cli/test_cmdbox_server_list.py::TestServerList::test_apprun_returned_object PASSED                [ 10%] 
cmdbox_test/app/features/cli/test_cmdbox_server_list.py::TestServerList::test_option_descriptions PASSED                   [ 12%]
cmdbox_test/app/features/cli/test_cmdbox_server_start.py::TestServerStart::test_apprun_without_data_option PASSED          [ 15%] 
cmdbox_test/app/features/cli/test_cmdbox_server_start.py::TestServerStart::test_apprun_without_svname_option PASSED        [ 17%] 
cmdbox_test/app/features/cli/test_cmdbox_server_start.py::TestServerStart::test_apprun_with_valid_args PASSED              [ 20%] 
cmdbox_test/app/features/cli/test_cmdbox_server_start.py::TestServerStart::test_is_cluster_redirect PASSED                 [ 23%]
cmdbox_test/app/features/cli/test_cmdbox_server_stop.py::TestServerStop::test_apprun_stop_server PASSED                    [ 25%]
cmdbox_test/app/features/cli/test_cmdbox_server_stop.py::TestServerStop::test_is_cluster_redirect PASSED                   [ 28%] 
cmdbox_test/app/features/cli/test_cmdbox_web_start.py::TestWebStart::test_apprun_without_data_option PASSED                [ 30%] 
cmdbox_test/app/features/cli/test_cmdbox_web_start.py::TestWebStart::test_apprun_with_valid_args PASSED                    [ 33%]
cmdbox_test/app/features/cli/test_cmdbox_web_start.py::TestWebStart::test_is_cluster_redirect PASSED                       [ 35%]
cmdbox_test/app/features/cli/test_cmdbox_web_stop.py::TestWebStop::test_apprun_successful_stop PASSED                      [ 38%] 
cmdbox_test/app/features/cli/test_cmdbox_web_stop.py::TestWebStop::test_is_cluster_redirect PASSED                         [ 41%] 
cmdbox_test/app/features/cli/test_cmdbox_web_user_list.py::TestWebUserList::test_apprun_without_signin_file_option PASSED  [ 43%]
cmdbox_test/app/features/cli/test_cmdbox_web_user_list.py::TestWebUserList::test_apprun_list_all_users PASSED              [ 46%] 
cmdbox_test/app/features/cli/test_cmdbox_web_user_list.py::TestWebUserList::test_apprun_list_specific_user PASSED          [ 48%] 
cmdbox_test/app/features/cli/test_cmdbox_web_user_list.py::TestWebUserList::test_is_cluster_redirect PASSED                [ 51%] 
cmdbox_test/app/test_web.py::TestWebModule::test_web_module_importable PASSED                                              [ 53%] 
cmdbox_test/app/test_web.py::TestWebModule::test_web_class_has_getinstance PASSED                                          [ 56%] 
cmdbox_test/app/test_web.py::TestWebGetInstance::test_get_instance_method_exists PASSED                                    [ 58%] 
cmdbox_test/app/test_web.py::TestWebGetInstance::test_get_instance_is_class_method PASSED                                  [ 61%]
cmdbox_test/app/test_web.py::TestWebUserListMethod::test_user_list_structure PASSED                                        [ 64%] 
cmdbox_test/app/test_web.py::TestWebChangePasswordMethod::test_change_password_method_exists PASSED                        [ 66%] 
cmdbox_test/app/test_web.py::TestWebApikeyMethods::test_apikey_add_method_exists PASSED                                    [ 69%] 
cmdbox_test/app/test_web.py::TestWebApikeyMethods::test_apikey_del_method_exists PASSED                                    [ 71%] 
cmdbox_test/app/test_web.py::TestWebUserMethods::test_user_add_method_exists PASSED                                        [ 74%] 
cmdbox_test/app/test_web.py::TestWebUserMethods::test_user_edit_method_exists PASSED                                       [ 76%] 
cmdbox_test/app/test_web.py::TestWebUserMethods::test_user_del_method_exists PASSED                                        [ 79%] 
cmdbox_test/app/test_web.py::TestWebGroupMethods::test_group_list_method_exists PASSED                                     [ 82%] 
cmdbox_test/app/test_web.py::TestWebGroupMethods::test_group_add_method_exists PASSED                                      [ 84%] 
cmdbox_test/app/test_web.py::TestWebGroupMethods::test_group_edit_method_exists PASSED                                     [ 87%] 
cmdbox_test/app/test_web.py::TestWebGroupMethods::test_group_del_method_exists PASSED                                      [ 89%]
cmdbox_test/app/test_web.py::TestWebUserDataMethod::test_user_data_method_exists PASSED                                    [ 92%] 
cmdbox_test/app/test_web.py::TestWebStartStopMethods::test_start_method_exists PASSED                                      [ 94%] 
cmdbox_test/app/test_web.py::TestWebStartStopMethods::test_stop_method_exists PASSED                                       [ 97%] 
cmdbox_test/app/test_web.py::TestWebInitWebfeaturesMethod::test_init_webfeatures_method_exists PASSED                      [100%] 

====================================================== 39 passed in 1.35s ======================================================= 
```

全39個のテストが成功しています。

### テスト統計

| モジュール / コマンド | テスト数 |
|--------|---------|
| ServerStart | 4 |
| ServerList | 5 |
| ServerStop | 2 |
| WebStart | 3 |
| WebStop | 2 |
| WebUserList | 4 |
| Web Module | 19 |
| **合計** | **39** |
| ServerStart | 4 |
| ServerList | 5 |
| ServerStop | 2 |
| WebStart | 3 |
| WebStop | 2 |
| WebUserList | 4 |
| Webモジュール | 2 |
| **合計** | **22** |

## 今後の拡張

- 他のコマンド（agent、client など）のテストコード追加
- インテグレーションテストの追加
- パフォーマンステストの追加
- テストカバレッジの測定と向上
