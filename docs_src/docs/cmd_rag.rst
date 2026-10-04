.. -*- coding: utf-8 -*-

******************************
Command Reference ( rag mode )
******************************

List of rag mode commands.

rag ( build ) : ``cmdbox -m rag -c build <Option>``
===================================================

- We build the database based on the RAG (Retrieval-Augmented Generation) configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--rag_name <rag_name>","str","","required","","","Specify the name of the RAG configuration to build."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( corpus2skill_compile ) : ``cmdbox -m rag -c corpus2skill_compile <Option>``
=================================================================================

- Compile a document collection into a Corpus2Skill hierarchy.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--svpath <svpath>","dir","","required","/","","Specify the directory path under the server's data folder. Supports text (.txt), markdown (.md), JSON (.json), and JSONL (.jsonl) formats. Each document should have 'id' and 'contents' fields."
    "--scope <scope>","str","","required","server","server | current | client","Specify the access scope. Only 'server' is supported. 'current' and 'client' are not supported."
    "--fwpath <fwpath>","file","multi","","","","Specify a path to determine whether the specified path is out of bounds. If it is not under this path, it is interpreted as having specified this path."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--ragcorpus_name <ragcorpus_name>","str","","required","","","Specify the RAG corpus name. The skill tree will be generated in data_dir/.ragcorpus/<ragcorpus_name>."
    "--llmname <llmname>","str","","","claude-sonnet-4-6","","Specify the LLM name for clustering and summarization. Default is claude-sonnet-4-6."
    "--llmname_embed <llmname_embed>","str","","","text-embedding-3-small","","Specify the LLM name for embedding. Default is text-embedding-3-small."
    "--doc_summary_model <doc_summary_model>","str","","","claude-haiku-4-5","","Specify the LLM name for per-document summary card generation. Default is claude-haiku-4-5."
    "--p <p>","int","","","10","","Specify the branching ratio (children per cluster). Default is 10."
    "--max_top <max_top>","int","","","8","","Specify the maximum number of top-level skills. Default is 8."
    "--min_cluster_size <min_cluster_size>","int","","","3","","Specify the minimum cluster size. Default is 3."
    "--max_doc_chars <max_doc_chars>","int","","","8000","","Specify the maximum characters per document. Default is 8000."
    "--no_doc_summaries <no_doc_summaries>","bool","","","False","True | False","If True, skip document summary card generation. Faster but lower quality."
    "--compact <compact>","bool","","","False","True | False","If True, merge leaf INDEX.md into parent to reduce file count."
    "--dry_run <dry_run>","bool","","","False","True | False","If True, show execution plan without actually running."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "message": "string",
        "documents_count": 0,
        "ragcorpus_dir": "string",
        "compile_info": {
          "input_dir": "string",
          "ragcorpus_dir": "string",
          "num_documents": 0,
          "llm_model": "string",
          "embed_model": "string",
          "p": 0,
          "max_top": 0,
          "doc_summary_cards_enabled": false,
          "compact": false,
          "dry_run": false,
          "status": "string"
        },
        "elapsed_seconds": 0.0
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.message","str","yes","(必須)","処理結果のメッセージ"
    "success.documents_count","int","yes","(必須)","処理されたドキュメント数"
    "success.ragcorpus_dir","str","yes","(必須)","コーパスディレクトリパス"
    "success.compile_info","CompileInfo","yes","(必須)","コンパイル情報"
    "success.compile_info.input_dir","str","yes","(必須)","入力ディレクトリ"
    "success.compile_info.ragcorpus_dir","str","yes","(必須)","コーパスディレクトリ"
    "success.compile_info.num_documents","int","yes","(必須)","ドキュメント数"
    "success.compile_info.llm_model","str","yes","(必須)","LLMモデル名"
    "success.compile_info.embed_model","str","yes","(必須)","埋め込みモデル名"
    "success.compile_info.p","int","yes","(必須)","分岐比"
    "success.compile_info.max_top","int","yes","(必須)","最大トップレベルスキル数"
    "success.compile_info.doc_summary_cards_enabled","bool","yes","(必須)","ドキュメント要約カード有効フラグ"
    "success.compile_info.compact","bool","yes","(必須)","コンパクト出力フラグ"
    "success.compile_info.dry_run","bool","yes","(必須)","ドライランフラグ"
    "success.compile_info.status","str","yes","(必須)","処理ステータス"
    "success.elapsed_seconds","float","yes","(必須)","処理時間（秒）"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( corpus2skill_query ) : ``cmdbox -m rag -c corpus2skill_query <Option>``
=============================================================================

- Execute a query against the compiled Corpus2Skill hierarchy and generate an answer.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--ragcorpus_name <ragcorpus_name>","str","","required","","","Specify the RAG corpus name to query. The skill hierarchy will be loaded from data_dir/.ragcorpus/<ragcorpus_name>."
    "--query <query>","str","","required","","","Specify the query (question) to execute."
    "--llmname <llmname>","str","","","claude-3-5-sonnet-20241022","","Specify the LLM model name for answer generation."
    "--max_turns <max_turns>","int","","","10","","Specify the maximum number of agent turns."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "message": "string",
        "answer": "string",
        "query": "string",
        "usage": {},
        "turns": [
          {}
        ]
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.message","str","yes","(必須)","処理結果のメッセージ"
    "success.answer","str","yes","(必須)","クエリに対する回答"
    "success.query","str","yes","(必須)","実行されたクエリ"
    "success.usage","dict[str, any]","yes","(必須)","トークン使用情報"
    "success.turns","list[dict[str, str]]","yes","(必須)","マルチターンのやり取り履歴"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( del ) : ``cmdbox -m rag -c del <Option>``
===============================================

- Delete the RAG (Retrieval-Augmented Generation) configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--rag_name <rag_name>","str","","required","","","Specify the name of the RAG configuration to delete."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( list ) : ``cmdbox -m rag -c list <Option>``
=================================================

- Display a list of saved RAG settings.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "name": "string",
            "path": "<class 'pathlib.Path'>"
          }
        ]
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[NamePath]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","Path | str | null","no","null","パス"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( load ) : ``cmdbox -m rag -c load <Option>``
=================================================

- Loads the settings for RAG (Retrieval-Augmented Generation).

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--rag_name <rag_name>","str","","required","","","Specify the name of the RAG configuration to load."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "rag_name": "string",
        "rag_datasource": "string",
        "savetype": "string",
        "extract": [
          "string"
        ],
        "llm_name": "string",
        "embed_vector_dim": 0
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.rag_name","str | null","no","null","RAG名"
    "success.rag_datasource","str | null","no","null","RAGのデータソース識別名"
    "success.savetype","str | null","no","null","保存タイプ"
    "success.extract","list[str] | null","no","null","エクストラクト設定リスト"
    "success.llm_name","str | null","no","null","LLM名"
    "success.embed_vector_dim","int | null","no","null","エンベッディングベクトル次元数"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( regist ) : ``cmdbox -m rag -c regist <Option>``
=====================================================

- Execute the RAG (Retrieval-Augmented Generation) registration process.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--rag_name <rag_name>","str","","required","","","Specify the name of the RAG configuration to use for registration."
    "--data <data>","dir","","required","C:\Users\hama\.cmdbox","","When omitted, `$HOME/.cmdbox` is used."
    "--signin_file <signin_file>","file","","required",".cmdbox/user_list.yml","","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","str","multi","required","","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( save ) : ``cmdbox -m rag -c save <Option>``
=================================================

- Saves the settings for RAG (Retrieval-Augmented Generation).

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--rag_name <rag_name>","str","","required","","","Specify the name of the RAG configuration."
    "--rag_datasource <rag_datasource>","str","","required","","","Specify the data source where RAG will be stored."
    "--extract <extract>","str","multi","required","","","Specify the registered name for the Extract process used in RAG. If no candidates exist, you must register a command in extract mode."
    "--llm_name <llm_name>","str","","required","","","Specify the name of the LLM configuration to use for embedding. Use one that has llmtype set to embedding in the llm mode save command."
    "--embed_vector_dim <embed_vector_dim>","int","","","256","","Specify the vector dimension for embedding."
    "--savetype <savetype>","str","","","per_doc","per_doc | per_service | add_only","Specify the storage pattern. `per_doc` :per document, `per_service` :per service, `add_only` :add only"

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


rag ( search ) : ``cmdbox -m rag -c search <Option>``
=====================================================

- Execute the RAG (Retrieval-Augmented Generation) search process.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--rag_name <rag_name>","str","","required","","","Specify the name of the RAG configuration to use for registration."
    "--query <query>","str","","","","","Specifies a search query."
    "--kcount <kcount>","int","","required","5","","Specify the number of search results. If filter conditions are specified, the results will be filtered from the number of results specified here."
    "--select <select>","str","multi","","","","Specifies the items to be retrieved. If not specified, all items are returned."
    "--filter_origin_name <filter_origin_name>","str","","","","","Specifies the origin_name of the filter condition."
    "--filter_dict <filter_dict>","dict","multi","","","","Specify arbitrary filter conditions, allowing multiple cmeta item names and values. Item values can be ambiguously searched by using `％`.  You can use the value of the query parameter by including the notation {args.query}."
    "--sort_dict <sort_dict>","dict","multi","",""," | ASC | DESC","Specifies the sort conditions when no query is specified. Multiple cmeta field names and sort orders (`ASC` (ascending) or `DESC` (descending)) can be specified."
    "--data <data>","dir","","required","C:\Users\hama\.cmdbox","","When omitted, `$HOME/.cmdbox` is used."
    "--signin_file <signin_file>","file","","required",".cmdbox/user_list.yml","","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","str","multi","required","","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          null
        ]
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[any] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

