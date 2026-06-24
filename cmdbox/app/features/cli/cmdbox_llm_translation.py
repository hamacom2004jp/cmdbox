from cmdbox.app import common, client
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_llm_chat, cmdbox_llm_list
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import re


class LLMTranslation(cmdbox_llm_chat.LLMChat):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language)
        self.llm_list = cmdbox_llm_list.LLMList(appcls, ver, language)
        self.translation_cache = dict()  # {target_lang: {word: translation}}

    TRANSLATION_FILE = "translation.json"

    def get_mode(self) -> Union[str, List[str]]:
        return 'llm'

    def get_cmd(self) -> str:
        return 'translation'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
            description_ja="単語リストをLLMで翻訳し、結果をJSON形式で返します。翻訳済みの単語はキャッシュして再利用します。",
            description_en="Translates a list of words using LLM and returns the result in JSON format. Already-translated words are reused from cache.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja="Redisサーバーのサービスホストを指定します。",
                    description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja="Redisサーバーのサービスポートを指定します。",
                    description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                    description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                    description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                    description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                    description_en="Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーに再接続までの秒数を指定します。",
                    description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="600", required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定します。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="llmname", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                            + "const val = $(\"[name='llmname']\").val();"
                            + "$(\"[name='llmname']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llmname']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llmname']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llmname');"
                            + "}",
                    description_ja="使用するLLM設定の名前を指定します。省略した場合はLLM設定の優先度が一番高いものが自動的に選択されます。",
                    description_en="Specify the name of the LLM configuration to use. If omitted, the LLM configuration with the highest priority is automatically selected."),
                dict(opt="words", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=None,
                    description_ja="翻訳する単語のリストを指定します。複数指定可能です。",
                    description_en="Specify the list of words to translate. Multiple values can be specified."),
                dict(opt="target_lang", type=Options.T_STR, default="en_US", required=True, multi=False, hide=False, choice=None,
                    description_ja="翻訳先の言語を指定します。",
                    description_en="Specify the target language."),
                dict(opt="nosave", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="翻訳結果を保存しない場合は指定します。",
                    description_en="Specify if the translation result should not be saved."),
                dict(opt="clear_cache", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="翻訳キャッシュをクリアする場合は指定します。",
                    description_en="Specify if the translation cache should be cleared."),
            ]
        )

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:

        words = args.words if isinstance(args.words, list) else [args.words]

        # キャッシュクリアオプションが指定された場合はキャッシュをクリアする
        if args.clear_cache: self.translation_cache = {}

        # 翻訳キャッシュを確認し、要求された単語がすべて存在する場合はキャッシュから返す
        lang_cache = self.translation_cache.get(args.target_lang, {})
        if all(word in lang_cache for word in words):
            result = {word: lang_cache[word] for word in words}
            msg = dict(success=dict(data=result))
            return self.RESP_SUCCESS, msg, None

        payload = dict(
            llmname=args.llmname,
            words=words,
            target_lang=args.target_lang,
            nosave=args.nosave,
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        if not args.nosave:
            # 新しい翻訳結果をキャッシュに追加
            self.translation_cache[args.target_lang] = self.translation_cache.get(args.target_lang, {})
            self.translation_cache[args.target_lang] = {
                **ret['success']['data'],
                **self.translation_cache[args.target_lang]}
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[Dict[str, str], None] = pydantic.Field(default=None, description="翻訳結果。{元の単語: 翻訳後の文字列} の辞書形式。")
        class Result(resdata.Result):
            success: Union[Data, str, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    @limiter.svrun_check_limit
    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            llmname = payload.get('llmname')
            words = payload.get('words', [])
            target_lang = payload.get('target_lang', 'en_US')
            nosave = payload.get('nosave', False)

            data = [] if not llmname else [dict(llmname=llmname, priority=0, type='chat')]
            data = data + self.llm_list.get_llmlist("", data_dir)
            # 優先度の高いものから順に試す
            for llm in data:
                if llm.get('type', 'chat') != 'chat': continue
                name = llm.get('name')
                try:
                    st, result = self.translate(data_dir, logger, name, words, target_lang, nosave=nosave)
                    if st == self.RESP_SUCCESS:
                        redis_cli.rpush(reskey, result)
                        return st
                except Exception as e:
                    logger.warning(f"Failed to translate using LLM '{name}': {e}. Trying next LLM if available.")
                    continue
            # すべてのLLMで翻訳できなかった場合は、元の単語を返す
            redis_cli.rpush(reskey, dict(success=dict(data={w: w for w in words})))
            return self.RESP_SUCCESS

            redis_cli.rpush(reskey, dict(warn=f"{self.get_mode()}_{self.get_cmd()}: No available LLM could translate the words."))
            return st

        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN

    def _load_cache(self, data_dir: Path) -> Dict[str, Any]:
        """
        翻訳キャッシュファイルを読み込みます。

        Args:
            data_dir (Path): データディレクトリのパス

        Returns:
            Dict[str, Any]: キャッシュデータ。 {"target_lang": {単語: 翻訳}} の形式。
        """
        cache_path = data_dir / ".agent" / self.TRANSLATION_FILE
        if cache_path.is_file():
            return common.load_file(cache_path, lambda f: json.load(f), encoding='utf-8', nolock=False)
        return {}

    def _save_cache(self, data_dir: Path, cache: Dict[str, Any]) -> None:
        """
        翻訳キャッシュファイルを保存します。

        Args:
            data_dir (Path): データディレクトリのパス
            cache (Dict[str, Any]): 保存するキャッシュデータ
        """
        cache_path = data_dir / ".agent" / self.TRANSLATION_FILE
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        common.save_file(cache_path, lambda f: json.dump(cache, f, ensure_ascii=False, indent=2),
                         encoding='utf-8', nolock=False)

    def _clear_cache(self, data_dir: Path) -> None:
        """
        翻訳キャッシュをクリアします。

        Args:
            data_dir (Path): データディレクトリのパス
        """
        cache_path = data_dir / ".agent" / self.TRANSLATION_FILE
        try:
            if cache_path.is_file():
                cache_path.unlink()
        except Exception as e:
            pass

    def translate(self, data_dir: Path, logger: logging.Logger, llmname: str,
                  words: List[str], target_lang: str, nosave: bool = False) -> Tuple[int, Dict[str, Any]]:
        """
        単語リストを翻訳します。キャッシュに存在する単語はLLMを呼ばずに返します。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            llmname (str): LLM設定の名前
            words (List[str]): 翻訳する単語のリスト
            target_lang (str): 翻訳先の言語コード
            nosave (bool): 翻訳結果を保存しない場合はTrue
        Returns:
            Tuple[int, Dict[str, Any]]: (ステータスコード, {success: {単語: 翻訳}} の辞書)
        """
        try:
            cache = self._load_cache(data_dir)
        except Exception as e:
            logger.warning(f"Failed to load translation cache: {e}", exc_info=True)
            return self.RESP_ERROR, dict(error=f"Failed to load translation cache. {e}")
        lang_cache: Dict[str, str] = cache.get(target_lang, {})

        # 重複を排除しつつ順序を保持
        unique_words = list(dict.fromkeys(words))
        missing = [w for w in unique_words if w not in lang_cache]

        if missing:
            if not llmname:
                # 利用可能なLLM設定が見つからない場合は翻訳できないため、キャッシュがあるものをマージして返す
                result = {w: lang_cache.get(w, w) for w in words}
                return self.RESP_SUCCESS, dict(success=dict(data=result))

            words_json = json.dumps(missing, ensure_ascii=False)
            prompt = (
                f"Translate the following words into {target_lang}.\n"
                f"Return the result strictly as a JSON object where each key is the original word "
                f"and the value is its translation. Output only the JSON, no explanations.\n\n"
                f"Words: {words_json}"
            )

            st, chat_result = self.chat(
                data_dir, logger, llmname,
                msg_role='user',
                msg_text=prompt,
            )
            if st != self.RESP_SUCCESS:
                return st, chat_result

            try:
                data = chat_result.get('success', {}).get('data', [])
                if data:
                    content = data[0].get('content', '')
                    content = content.strip()
                    # コードブロックが含まれる場合は中身を取り出す
                    code_block = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
                    if code_block:
                        content = code_block.group(1).strip()
                    translated: Dict[str, str] = json.loads(content)
                    lang_cache.update(translated)
                    cache[target_lang] = lang_cache
                    if not nosave:
                        self._save_cache(data_dir, cache)
            except Exception as e:
                logger.warning(f"Failed to parse LLM translation response: {e}", exc_info=True)
                # キャッシュ保存は失敗しても既キャッシュ分は返す

        result = {w: lang_cache.get(w, w) for w in words}
        return self.RESP_SUCCESS, dict(success=dict(data=result))
