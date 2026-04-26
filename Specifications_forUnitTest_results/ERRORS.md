# テスト実行結果 - エラー一覧

生成日時: 2026-04-26T09:59:03

## サマリー

| 項目 | 件数 |
| --- | --- |
| 失敗コマンド数 | 1 |
| 失敗テストケース数 | 23 |

## 失敗テストケース一覧

| モード | コマンド | # | カテゴリ | 観点 | 入力パターン | 期待ステータス | 実際のステータス | 理由 | 実行日時 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| audit | delete | TC-001 | 正常系 | 最小有効入力 | 全パラメータ省略またはデフォルト値で実行する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:52:05 |
| audit | delete | TC-002 | 型境界 | pg_enabled=False | --pg_enabled に False を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:52:05 |
| audit | delete | TC-003 | 型境界 | pg_enabled=True | --pg_enabled に True を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:52:06 |
| audit | delete | TC-007 | 型境界 | pg_port=0 | --pg_port に 0 を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:55:23 |
| audit | delete | TC-008 | 型境界 | pg_port=1 | --pg_port に 1 を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:55:24 |
| audit | delete | TC-010 | 型境界 | pg_port=2147483647 | --pg_port に 2147483647 を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:55:26 |
| audit | delete | TC-014 | 型境界 | pg_password 1文字 | --pg_password に 1 文字値 X を指定する | RESP_SUCCESS | RESP_WARN | {'error': 'Connected server failed or server not found. svname=cmdbox'} | 2026-04-26T09:55:30 |
| audit | delete | TC-015 | 型境界 | pg_password 特殊文字 | --pg_password に a_日本語 space-_.#"'&<> を指定する | RESP_SUCCESS | RESP_WARN | {'error': 'Connected server failed or server not found. svname=cmdbox'} | 2026-04-26T09:56:00 |
| audit | delete | TC-019 | 選択値境界 | delete_audit_type 先頭選択肢 | --delete_audit_type に選択肢の先頭値  を指定する | RESP_SUCCESS | RESP_WARN | {'error': 'fail to execute command. cmd=audit_delete, msg=Response timed out.'} | 2026-04-26T09:57:05 |
| audit | delete | TC-020 | 選択値境界 | delete_audit_type 末尾選択肢 | --delete_audit_type に選択肢の末尾値 event を指定する | RESP_SUCCESS | RESP_WARN | {'error': 'fail to execute command. cmd=audit_delete, msg=Response timed out.'} | 2026-04-26T09:57:20 |
| audit | delete | TC-022 | 型境界 | delete_audit_type 空文字 | --delete_audit_type に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'error': 'fail to execute command. cmd=audit_delete, msg=Response timed out.'} | 2026-04-26T09:57:35 |
| audit | delete | TC-023 | 型境界 | delete_clmsg_id 空文字 | --delete_clmsg_id に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'error': 'fail to execute command. cmd=audit_delete, msg=Response timed out.'} | 2026-04-26T09:57:50 |
| audit | delete | TC-027 | 型境界 | delete_clmsg_src 空文字 | --delete_clmsg_src に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:29 |
| audit | delete | TC-031 | 型境界 | delete_clmsg_title 空文字 | --delete_clmsg_title に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:43 |
| audit | delete | TC-035 | 型境界 | delete_clmsg_user 空文字 | --delete_clmsg_user に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:47 |
| audit | delete | TC-039 | 複数値境界 | delete_clmsg_body 0件 | --delete_clmsg_body に空配列または未指定を与える | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:51 |
| audit | delete | TC-040 | 複数値境界 | delete_clmsg_body 1件 | --delete_clmsg_body に 1 件だけ指定する | RESP_SUCCESS |  | IndexError: list index out of range | 2026-04-26T09:58:51 |
| audit | delete | TC-041 | 複数値境界 | delete_clmsg_body 複数件 | --delete_clmsg_body に 2 件以上指定する | RESP_SUCCESS |  | IndexError: list index out of range | 2026-04-26T09:58:51 |
| audit | delete | TC-042 | 複数値境界 | delete_clmsg_tag 0件 | --delete_clmsg_tag に空配列または未指定を与える | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:52 |
| audit | delete | TC-043 | 複数値境界 | delete_clmsg_tag 1件 | --delete_clmsg_tag に 1 件だけ指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:53 |
| audit | delete | TC-044 | 複数値境界 | delete_clmsg_tag 複数件 | --delete_clmsg_tag に 2 件以上指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:54 |
| audit | delete | TC-045 | 型境界 | delete_clmsg_tag 空文字 | --delete_clmsg_tag に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:55 |
| audit | delete | TC-049 | 型境界 | delete_svmsg_id 空文字 | --delete_svmsg_id に空文字を指定する | RESP_SUCCESS | RESP_WARN | {'warn': 'No data deleted.'} | 2026-04-26T09:58:59 |
