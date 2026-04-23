# Specifications_forUnitTest

CLI コマンドごとの単体テスト仕様です。

- 対象コマンド数: 115
- 生成元 JSON: cli-unit-test-specifications.json
- 生成日時: 2026-04-23T23:40:14

## 使い方

- 各仕様書は、最小有効入力、必須チェック、境界値、ファイル I/O、副作用確認の順でテストパターンを整理しています。
- 数値の厳密な許容範囲がコードから判定できないものは、汎用境界値として 0, 1, -1, 極大値を採用しています。
- fileio=out のパラメータを持つコマンドでは、戻り値だけでなく生成物の存在・内容・追記挙動も確認対象にしています。

## a2asv

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| start | 43 | 1 | [cli/a2asv/start.md](cli/a2asv/start.md) |
| stop | 7 | 2 | [cli/a2asv/stop.md](cli/a2asv/stop.md) |

## agent

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| agent_del | 9 | 2 | [cli/agent/agent_del.md](cli/agent/agent_del.md) |
| agent_list | 8 | 1 | [cli/agent/agent_list.md](cli/agent/agent_list.md) |
| agent_load | 9 | 1 | [cli/agent/agent_load.md](cli/agent/agent_load.md) |
| agent_save | 55 | 2 | [cli/agent/agent_save.md](cli/agent/agent_save.md) |
| chat | 33 | 1 | [cli/agent/chat.md](cli/agent/chat.md) |
| mcp_client | 52 | 1 | [cli/agent/mcp_client.md](cli/agent/mcp_client.md) |
| mcp_proxy | 21 | 0 | [cli/agent/mcp_proxy.md](cli/agent/mcp_proxy.md) |
| mcpsv_del | 9 | 2 | [cli/agent/mcpsv_del.md](cli/agent/mcpsv_del.md) |
| mcpsv_list | 8 | 1 | [cli/agent/mcpsv_list.md](cli/agent/mcpsv_list.md) |
| mcpsv_load | 9 | 1 | [cli/agent/mcpsv_load.md](cli/agent/mcpsv_load.md) |
| mcpsv_save | 25 | 2 | [cli/agent/mcpsv_save.md](cli/agent/mcpsv_save.md) |
| memory_del | 9 | 2 | [cli/agent/memory_del.md](cli/agent/memory_del.md) |
| memory_list | 8 | 1 | [cli/agent/memory_list.md](cli/agent/memory_list.md) |
| memory_load | 9 | 1 | [cli/agent/memory_load.md](cli/agent/memory_load.md) |
| memory_save | 52 | 2 | [cli/agent/memory_save.md](cli/agent/memory_save.md) |
| memory_status | 28 | 2 | [cli/agent/memory_status.md](cli/agent/memory_status.md) |
| runner_del | 9 | 2 | [cli/agent/runner_del.md](cli/agent/runner_del.md) |
| runner_list | 8 | 1 | [cli/agent/runner_list.md](cli/agent/runner_list.md) |
| runner_load | 9 | 1 | [cli/agent/runner_load.md](cli/agent/runner_load.md) |
| runner_save | 66 | 2 | [cli/agent/runner_save.md](cli/agent/runner_save.md) |
| session_del | 19 | 1 | [cli/agent/session_del.md](cli/agent/session_del.md) |
| session_list | 18 | 1 | [cli/agent/session_list.md](cli/agent/session_list.md) |

## audit

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| createdb | 25 | 0 | [cli/audit/createdb.md](cli/audit/createdb.md) |
| delete | 60 | 0 | [cli/audit/delete.md](cli/audit/delete.md) |
| search | 102 | 2 | [cli/audit/search.md](cli/audit/search.md) |
| write | 65 | 1 | [cli/audit/write.md](cli/audit/write.md) |

## client

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| file_copy | 26 | 2 | [cli/client/file_copy.md](cli/client/file_copy.md) |
| file_download | 34 | 2 | [cli/client/file_download.md](cli/client/file_download.md) |
| file_list | 24 | 1 | [cli/client/file_list.md](cli/client/file_list.md) |
| file_mkdir | 18 | 2 | [cli/client/file_mkdir.md](cli/client/file_mkdir.md) |
| file_move | 24 | 1 | [cli/client/file_move.md](cli/client/file_move.md) |
| file_remove | 18 | 1 | [cli/client/file_remove.md](cli/client/file_remove.md) |
| file_rmdir | 18 | 1 | [cli/client/file_rmdir.md](cli/client/file_rmdir.md) |
| file_upload | 25 | 1 | [cli/client/file_upload.md](cli/client/file_upload.md) |
| http | 48 | 0 | [cli/client/http.md](cli/client/http.md) |
| server_info | 3 | 1 | [cli/client/server_info.md](cli/client/server_info.md) |
| time | 6 | 0 | [cli/client/time.md](cli/client/time.md) |

## cmd

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| list | 36 | 1 | [cli/cmd/list.md](cli/cmd/list.md) |
| load | 22 | 1 | [cli/cmd/load.md](cli/cmd/load.md) |

## cmdbox

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| down | 5 | 0 | [cli/cmdbox/down.md](cli/cmdbox/down.md) |
| exec | 12 | 0 | [cli/cmdbox/exec.md](cli/cmdbox/exec.md) |
| load | 17 | 1 | [cli/cmdbox/load.md](cli/cmdbox/load.md) |
| logs | 14 | 0 | [cli/cmdbox/logs.md](cli/cmdbox/logs.md) |
| pgsql_install | 36 | 1 | [cli/cmdbox/pgsql_install.md](cli/cmdbox/pgsql_install.md) |
| pgsql_load | 17 | 1 | [cli/cmdbox/pgsql_load.md](cli/cmdbox/pgsql_load.md) |
| reboot | 8 | 0 | [cli/cmdbox/reboot.md](cli/cmdbox/reboot.md) |
| redis_install | 12 | 0 | [cli/cmdbox/redis_install.md](cli/cmdbox/redis_install.md) |
| redis_load | 13 | 1 | [cli/cmdbox/redis_load.md](cli/cmdbox/redis_load.md) |
| save | 16 | 2 | [cli/cmdbox/save.md](cli/cmdbox/save.md) |
| server_install | 76 | 1 | [cli/cmdbox/server_install.md](cli/cmdbox/server_install.md) |
| server_load | 19 | 1 | [cli/cmdbox/server_load.md](cli/cmdbox/server_load.md) |
| uninstall | 12 | 0 | [cli/cmdbox/uninstall.md](cli/cmdbox/uninstall.md) |
| up | 8 | 0 | [cli/cmdbox/up.md](cli/cmdbox/up.md) |

## edge

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| config | 74 | 0 | [cli/edge/config.md](cli/edge/config.md) |
| start | 5 | 0 | [cli/edge/start.md](cli/edge/start.md) |

## embed

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| del | 9 | 2 | [cli/embed/del.md](cli/embed/del.md) |
| embedding | 16 | 1 | [cli/embed/embedding.md](cli/embed/embedding.md) |
| list | 8 | 1 | [cli/embed/list.md](cli/embed/list.md) |
| load | 9 | 1 | [cli/embed/load.md](cli/embed/load.md) |
| save | 22 | 2 | [cli/embed/save.md](cli/embed/save.md) |
| start | 8 | 1 | [cli/embed/start.md](cli/embed/start.md) |
| stop | 8 | 1 | [cli/embed/stop.md](cli/embed/stop.md) |

## excel

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| cell_details | 43 | 1 | [cli/excel/cell_details.md](cli/excel/cell_details.md) |
| cell_search | 55 | 1 | [cli/excel/cell_search.md](cli/excel/cell_search.md) |
| cell_values | 46 | 1 | [cli/excel/cell_values.md](cli/excel/cell_values.md) |
| sheet_list | 15 | 1 | [cli/excel/sheet_list.md](cli/excel/sheet_list.md) |

## extract

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| chunklet | 43 | 1 | [cli/extract/chunklet.md](cli/extract/chunklet.md) |
| del | 9 | 2 | [cli/extract/del.md](cli/extract/del.md) |
| list | 8 | 1 | [cli/extract/list.md](cli/extract/list.md) |
| load | 9 | 1 | [cli/extract/load.md](cli/extract/load.md) |
| pdfplumber | 64 | 1 | [cli/extract/pdfplumber.md](cli/extract/pdfplumber.md) |
| save | 40 | 2 | [cli/extract/save.md](cli/extract/save.md) |

## gui

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| start | 90 | 0 | [cli/gui/start.md](cli/gui/start.md) |
| stop | 7 | 1 | [cli/gui/stop.md](cli/gui/stop.md) |

## llm

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| chat | 54 | 1 | [cli/llm/chat.md](cli/llm/chat.md) |
| del | 9 | 2 | [cli/llm/del.md](cli/llm/del.md) |
| list | 8 | 1 | [cli/llm/list.md](cli/llm/list.md) |
| load | 9 | 1 | [cli/llm/load.md](cli/llm/load.md) |
| save | 52 | 2 | [cli/llm/save.md](cli/llm/save.md) |

## mcpsv

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| start | 43 | 1 | [cli/mcpsv/start.md](cli/mcpsv/start.md) |
| stop | 7 | 2 | [cli/mcpsv/stop.md](cli/mcpsv/stop.md) |

## omni

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| pred | 4 | 1 | [cli/omni/pred.md](cli/omni/pred.md) |

## rag

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| build | 9 | 1 | [cli/rag/build.md](cli/rag/build.md) |
| del | 9 | 2 | [cli/rag/del.md](cli/rag/del.md) |
| list | 8 | 1 | [cli/rag/list.md](cli/rag/list.md) |
| load | 9 | 1 | [cli/rag/load.md](cli/rag/load.md) |
| regist | 23 | 1 | [cli/rag/regist.md](cli/rag/regist.md) |
| save | 79 | 2 | [cli/rag/save.md](cli/rag/save.md) |
| search | 51 | 1 | [cli/rag/search.md](cli/rag/search.md) |

## server

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| list | 3 | 1 | [cli/server/list.md](cli/server/list.md) |
| start | 7 | 1 | [cli/server/start.md](cli/server/start.md) |
| stop | 3 | 1 | [cli/server/stop.md](cli/server/stop.md) |

## test

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| gen_cli_spec | 28 | 2 | [cli/test/gen_cli_spec.md](cli/test/gen_cli_spec.md) |
| gen_test_spec | 15 | 2 | [cli/test/gen_test_spec.md](cli/test/gen_test_spec.md) |
| run_spec | 30 | 2 | [cli/test/run_spec.md](cli/test/run_spec.md) |

## tts

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| install | 58 | 0 | [cli/tts/install.md](cli/tts/install.md) |
| list | 9 | 0 | [cli/tts/list.md](cli/tts/list.md) |
| say | 25 | 2 | [cli/tts/say.md](cli/tts/say.md) |
| uninstall | 14 | 0 | [cli/tts/uninstall.md](cli/tts/uninstall.md) |

## web

| cmd | テストケース数 | 成果物確認 | 仕様書 |
| --- | ---: | ---: | --- |
| apikey_add | 15 | 0 | [cli/web/apikey_add.md](cli/web/apikey_add.md) |
| apikey_del | 15 | 0 | [cli/web/apikey_del.md](cli/web/apikey_del.md) |
| gencert | 39 | 4 | [cli/web/gencert.md](cli/web/gencert.md) |
| genpass | 38 | 0 | [cli/web/genpass.md](cli/web/genpass.md) |
| group_add | 19 | 0 | [cli/web/group_add.md](cli/web/group_add.md) |
| group_del | 10 | 0 | [cli/web/group_del.md](cli/web/group_del.md) |
| group_edit | 19 | 0 | [cli/web/group_edit.md](cli/web/group_edit.md) |
| group_list | 9 | 0 | [cli/web/group_list.md](cli/web/group_list.md) |
| start | 91 | 0 | [cli/web/start.md](cli/web/start.md) |
| stop | 7 | 1 | [cli/web/stop.md](cli/web/stop.md) |
| user_add | 38 | 0 | [cli/web/user_add.md](cli/web/user_add.md) |
| user_del | 10 | 0 | [cli/web/user_del.md](cli/web/user_del.md) |
| user_edit | 38 | 0 | [cli/web/user_edit.md](cli/web/user_edit.md) |
| user_list | 9 | 0 | [cli/web/user_list.md](cli/web/user_list.md) |
