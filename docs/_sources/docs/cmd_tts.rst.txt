.. -*- coding: utf-8 -*-

******************************
Command Reference ( tts mode )
******************************

List of tts mode commands.

tts ( install ) : ``cmdbox -m tts -c install <Option>``
=======================================================

- Installs the Text-to-Speech (TTS) engine.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HONE/.cmdbox` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","300","","Specify the maximum waiting time until the server responds."
    "--client_only <client_only>","bool","","","False","True | False","Do not make connections to the server."
    "--force_install <force_install>","bool","","","False","True | False","Overwrite the installation even if it is already installed."
    "--tts_engine <tts_engine>","str","","required","voicevox"," | voicevox","Specify the TTS engine to use."
    "--voicevox_ver <voicevox_ver>","str","","","0.16.3"," | 0.16.3","Specify the version of VOICEVOX to use."
    "--voicevox_whl <voicevox_whl>","str","","","voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl"," | voicevox_core-0.16.3-cp310-abi3-win32.whl | voicevox_core-0.16.3-cp310-abi3-win_amd64.whl | voicevox_core-0.16.3-cp310-abi3-macosx_10_12_x86_64.whl | voicevox_core-0.16.3-cp310-abi3-macosx_11_0_arm64.whl | voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_aarch64.whl | voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl","Specify the VOICEVOX wheel file to use."
    "--openjtalk_ver <openjtalk_ver>","str","","","v1.11.1"," | v1.11.1","Specify the version of openjtalk to use."
    "--openjtalk_dic <openjtalk_dic>","str","","","open_jtalk_dic_utf_8-1.11.tar.gz"," | open_jtalk_dic_utf_8-1.11.tar.gz","Specify the openjtalk dictionary file to use."
    "--onnxruntime_ver <onnxruntime_ver>","str","","","voicevox_onnxruntime-1.17.3"," | voicevox_onnxruntime-1.17.3","Specify the version of ONNX Runtime to use."
    "--onnxruntime_lib <onnxruntime_lib>","str","","","voicevox_onnxruntime-linux-x64-1.17.3.tgz"," | voicevox_onnxruntime-linux-arm64-1.17.3.tgz | voicevox_onnxruntime-linux-armhf-1.17.3.tgz | voicevox_onnxruntime-linux-x64-1.17.3.tgz | voicevox_onnxruntime-linux-x64-cuda-1.17.3.tgz | voicevox_onnxruntime-osx-arm64-1.17.3.tgz | voicevox_onnxruntime-osx-x86_64-1.17.3.tgz | voicevox_onnxruntime-win-x64-1.17.3.tgz | voicevox_onnxruntime-win-x64-cuda-1.17.3.tgz | voicevox_onnxruntime-win-x64-dml-1.17.3.tgz | voicevox_onnxruntime-win-x86-1.17.3.tgz","Specify the ONNX Runtime library file to use."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
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
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


tts ( list ) : ``cmdbox -m tts -c list <Option>``
=================================================

- Lists the Text-to-Speech (TTS) engines.

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
    "--tts_engine <tts_engine>","str","","required","voicevox"," | voicevox","Specify the TTS engine to use."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "engine": "string",
            "model": "string",
            "character": "string",
            "style": "string"
          }
        ]
      },
      "warn": {},
      "error": "string",
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[TtsRecord] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","str | null","no","null","エラーが発生した場合の結果"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


tts ( say ) : ``cmdbox -m tts -c say <Option>``
===============================================

- Converts text to speech using the Text-to-Speech (TTS) engine.

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
    "--tts_engine <tts_engine>","str","","required","voicevox"," | voicevox","Specify the TTS engine to use."
    "--voicevox_model <voicevox_model>","str","","","","No.7アナウンス | No.7ノーマル | No.7読み聞かせ | Voidollノーマル | WhiteCULかなしい | WhiteCULたのしい | WhiteCULびえーん | WhiteCULノーマル | †聖騎士 紅桜†ノーマル | あいえるたんノーマル | ずんだもんあまあま | ずんだもんささやき | ずんだもんなみだめ | ずんだもんセクシー | ずんだもんツンツン | ずんだもんノーマル | ずんだもんヒソヒソ | ずんだもんヘロヘロ | ぞん子ノーマル | ぞん子低血圧 | ぞん子実況風 | ぞん子覚醒 | ちび式じいノーマル | もち子さんのんびり | もち子さんセクシー／あん子 | もち子さんノーマル | もち子さん喜び | もち子さん怒り | もち子さん泣き | ナースロボ＿タイプＴノーマル | ナースロボ＿タイプＴ内緒話 | ナースロボ＿タイプＴ恐怖 | ナースロボ＿タイプＴ楽々 | ユーレイちゃんささやき | ユーレイちゃんツクモちゃん | ユーレイちゃんノーマル | ユーレイちゃん哀しみ | ユーレイちゃん甘々 | 中国うさぎおどろき | 中国うさぎこわがり | 中国うさぎへろへろ | 中国うさぎノーマル | 中部つるぎおどおど | 中部つるぎノーマル | 中部つるぎヒソヒソ | 中部つるぎ怒り | 中部つるぎ絶望と敗北 | 九州そらあまあま | 九州そらささやき | 九州そらセクシー | 九州そらツンツン | 九州そらノーマル | 冥鳴ひまりノーマル | 剣崎雌雄ノーマル | 四国めたんあまあま | 四国めたんささやき | 四国めたんセクシー | 四国めたんツンツン | 四国めたんノーマル | 四国めたんヒソヒソ | 小夜/SAYOノーマル | 後鬼ぬいぐるみver. | 後鬼人間ver. | 後鬼人間（怒り）ver. | 後鬼鬼ver. | 春日部つむぎノーマル | 春歌ナナノーマル | 東北きりたんノーマル | 東北ずん子ノーマル | 東北イタコノーマル | 栗田まろんノーマル | 櫻歌ミコノーマル | 櫻歌ミコロリ | 櫻歌ミコ第二形態 | 波音リツクイーン | 波音リツノーマル | 満別花丸ささやき | 満別花丸ぶりっ子 | 満別花丸ノーマル | 満別花丸ボーイ | 満別花丸元気 | 猫使アルうきうき | 猫使アルおちつき | 猫使アルつよつよ | 猫使アルへろへろ | 猫使アルノーマル | 猫使ビィおちつき | 猫使ビィつよつよ | 猫使ビィノーマル | 猫使ビィ人見知り | 玄野武宏ツンギレ | 玄野武宏ノーマル | 玄野武宏喜び | 玄野武宏悲しみ | 琴詠ニアノーマル | 白上虎太郎おこ | 白上虎太郎びえーん | 白上虎太郎びくびく | 白上虎太郎ふつう | 白上虎太郎わーい | 雀松朱司ノーマル | 離途シリアス | 離途ノーマル | 雨晴はうノーマル | 青山龍星かなしみ | 青山龍星しっとり | 青山龍星ノーマル | 青山龍星不機嫌 | 青山龍星喜び | 青山龍星囁き | 青山龍星熱血 | 麒ヶ島宗麟ノーマル | 黒沢冴白ノーマル","Specify the model of the TTS engine to use."
    "--tts_text <tts_text>","text","","required","","","Specifies the text to convert."
    "--tts_output <tts_output>","file","","","","","Specifies the output file for the converted audio."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string",
        "format": "string",
        "model": "string"
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
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "success.format","str | null","no","null","フォーマット"
    "success.model","str | null","no","null","モデル名"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


tts ( uninstall ) : ``cmdbox -m tts -c uninstall <Option>``
===========================================================

- Uninstalls the Text-to-Speech (TTS) engine.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HONE/.cmdbox` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","300","","Specify the maximum waiting time until the server responds."
    "--client_only <client_only>","bool","","","False","True | False","Do not make connections to the server."
    "--tts_engine <tts_engine>","str","","required","voicevox"," | voicevox","Specify the TTS engine to use."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
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
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

