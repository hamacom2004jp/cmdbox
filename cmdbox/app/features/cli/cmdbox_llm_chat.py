from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class LLMChat(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'llm'

    def get_cmd(self) -> str:
        return 'chat'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
            description_ja="LLMに対しチャットメッセージを送信します。",
            description_en="Send a chat message to the LLM.",
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
                    description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーに再接続までの秒数を指定します。",
                    description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="600", required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="llmname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                            + "const val = $(\"[name='llmname']\").val();"
                            + "$(\"[name='llmname']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llmname']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llmname']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llmname');"
                            + "}",
                    description_ja="読み込むLLM設定の名前を指定します。",
                    description_en="Specify the name of the LLM configuration to load."),
                dict(opt="msg_role", type=Options.T_STR, default="user", required=True, multi=False, hide=False, choice=["user", "assistant", "system", "function", "tool"],
                    description_ja="メッセージ送信者の役割を指定します。",
                    description_en="Specify the role of the message sender."),
                dict(opt="msg_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="メッセージ送信者の名前を指定します。msg_roleが `function` または `tool` の場合は必須です。",
                    description_en="Specify the name of the message sender. Required if msg_role is `function` or `tool`."),
                dict(opt="msg_text", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="送信するテキストの内容を指定します。",
                    description_en="Specify the content of the text to be sent."),
                dict(opt="msg_text_system", type=Options.T_TEXT, default="次のユーザーの依頼にこたえてください。\\n\\n{{msg_text}}", required=False, multi=False, hide=False, choice=None,
                    description_ja="送信するシステムプロンプトを指定します。 `{{AAA}}` と表記すると `AAA` のパラメータを設定できます。なお `{{msg_text}}` と指定すると `msg_text` オプションの値が設定されます。",
                    description_en="Specify the system prompt to send. Using `{{AAA}}` allows you to set the `AAA` parameter. Note that specifying `{{msg_text}}` sets the value of the `msg_text` option."),
                dict(opt="msg_text_param", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="送信するテキストのパラメータを指定します。",
                    description_en="Specify the parameters for the text."),
                dict(opt="msg_image_url", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="送信する画像のURLを指定します。",
                    description_en="Specify the URL of the image to be sent."),
                dict(opt="msg_audio", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="送信する音声の内容を指定します。",
                    description_en="Specify the content of the audio to be sent."),
                dict(opt="msg_audio_format", type=Options.T_STR, default="wav", required=False, multi=False, hide=False, choice=["wav", "mp3", "ogg", "flac"],
                    description_ja="送信する音声のフォーマットを指定します。",
                    description_en="Specify the format of the audio to be sent."),
                dict(opt="msg_video_url", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="送信する動画のURLを指定します。",
                    description_en="Specify the URL of the video to be sent."),
                dict(opt="msg_file_url", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="送信するファイルのURLを指定します。",
                    description_en="Specify the URL of the file to be sent."),
                dict(opt="msg_doc", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="送信するドキュメントの内容を指定します。",
                    description_en="Specify the content of the document to be sent."),
                dict(opt="msg_doc_mime", type=Options.T_STR, default="application/pdf", required=False, multi=False, hide=False, choice=None,
                    description_ja="送信するドキュメントのMIMEタイプを指定します。",
                    description_en="Specify the MIME type of the document to be sent."),
            ]
        )

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl

        if not re.match(r'^[\w\-]+$', args.llmname):
            msg = dict(warn="LLM name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        if args.msg_audio:
            try:
                with open(args.msg_audio, 'rb') as f:
                    args.msg_audio = convert.bytes2b64str(f.read())
            except Exception as e:
                msg = dict(warn=f"Failed to read audio file: {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        if args.msg_doc:
            try:
                with open(args.msg_doc, 'rb') as f:
                    args.msg_doc = convert.bytes2b64str(f.read())
            except Exception as e:
                msg = dict(warn=f"Failed to read document file: {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        payload = dict(llmname=args.llmname,
                       msg_role=args.msg_role,
                       msg_name=args.msg_name,
                       msg_text=args.msg_text,
                       msg_text_system=args.msg_text_system,
                       msg_text_param=args.msg_text_param,
                       msg_image_url=args.msg_image_url,
                       msg_audio=args.msg_audio,
                       msg_audio_format=args.msg_audio_format,
                       msg_video_url=args.msg_video_url,
                       msg_file_url=args.msg_file_url,
                       msg_doc=args.msg_doc,
                       msg_doc_mime=args.msg_doc_mime,
                       )
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        サーバー側で受け取ったloadコマンドを処理します。
        """
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            llmname = payload.get('llmname')

            st, msg = self.chat(data_dir, logger, llmname,
                            msg_role=payload.get('msg_role', 'user'),
                            msg_name=payload.get('msg_name', None),
                            msg_text=payload.get('msg_text', None),
                            msg_text_system=payload.get('msg_text_system', None),
                            msg_text_param=payload.get('msg_text_param', None),
                            msg_image_url=payload.get('msg_image_url', None),
                            msg_audio=payload.get('msg_audio', None),
                            msg_audio_format=payload.get('msg_audio_format', None),
                            msg_video_url=payload.get('msg_video_url', None),
                            msg_file_url=payload.get('msg_file_url', None),
                            msg_doc=payload.get('msg_doc', None),
                            msg_doc_mime=payload.get('msg_doc_mime', None),
                            )
            redis_cli.rpush(reskey, msg)
            return st

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def chat(self, data_dir:Path, logger:logging.Logger, llmname:str, *,
             msg_role:str=None, msg_name:str=None, msg_text:str=None, msg_text_system:str=None, msg_text_param:Dict[str, Any]=None,
             msg_image_url:str=None, msg_audio:str=None, msg_audio_format:str=None, msg_video_url:str=None, msg_file_url:str=None,
             msg_doc:str=None, msg_doc_mime:str=None) -> Tuple[int, List[Dict[str, Any]]]:
        """
        LLMにチャットメッセージを送信します。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            llmname (str): LLM設定の名前
            msg_role (str, optional): メッセージ送信者の役割。
            msg_name (str, optional): メッセージ送信者の名前。
            msg_text (str, optional): 送信するテキストの内容。
            msg_text_system (str, optional): 送信するシステムプロンプト。 `{{AAA}}` と表記すると `AAA` のパラメータを設定できます。なお `{{msg_text}}` と指定すると `msg_text` オプションの値が設定されます。
            msg_text_param (Dict[str, Any], optional): 送信するテキストのパラメータ。
            msg_image_url (str, optional): 送信する画像のURL。
            msg_audio (str, optional): 送信する音声の内容。Base64エンコードされた文字列で指定します。
            msg_audio_format (str, optional): 送信する音声のフォーマット。 `wav`, `mp3`, `ogg`, `flac` のいずれかを指定します。
            msg_video_url (str, optional): 送信する動画のURL。
            msg_file_url (str, optional): 送信するファイルのURL。
            msg_doc (str, optional): 送信するドキュメントの内容。Base64エンコードされた文字列で指定します。
            msg_doc_mime (str, optional): 送信するドキュメントのMIMEタイプ。
        Returns:
            Tuple[int, List[Dict[str, Any]]]: (ステータスコード, LLMからの応答メッセージのリスト)
        """

        configure_path = data_dir / ".agent" / f"llm-{llmname}.json"
        if not configure_path.exists():
            msg = dict(warn=f"Specified LLM configuration '{llmname}' not found on server at '{str(configure_path)}'.")
            return self.RESP_WARN, msg
        with configure_path.open('r', encoding='utf-8') as f:
            configure = json.load(f)

        if msg_text_system:
            if msg_text_param:
                for k, v in msg_text_param.items():
                    placeholder = f"{{{k}}}"
                    if placeholder in msg_text_system:
                        msg_text_system = msg_text_system.replace(placeholder, str(v))
            if msg_text:
                placeholder = "{{msg_text}}"
                if placeholder in msg_text_system:
                    msg_text_system = msg_text_system.replace(placeholder, str(msg_text))
                else:
                    msg_text_system += f"\n\n{msg_text}"
            msg_text = msg_text_system

        message = dict(role=msg_role, content=[])
        if msg_text:
            message['content'].append(dict(type="text", text=msg_text))
        if msg_image_url:
            message['content'].append(dict(type="image_url", image_url=dict(url=msg_image_url)))
        if msg_audio:
            message['content'].append(dict(type="input_audio", input_audio=dict(data=msg_audio, format=msg_audio_format)))
        if msg_video_url:
            message['content'].append(dict(type="video_url", video_url=dict(url=msg_video_url)))
        if msg_file_url:
            message['content'].append(dict(type="file", file=dict(file_id=msg_file_url)))
        if msg_doc:
            message['content'].append(dict(type="document", source=dict(type="text", data=msg_doc, media_type=msg_doc_mime)))

        import litellm
        llmprov = configure.get('llmprov', None)
        if llmprov == 'openai':
            llmmodel = configure.get('llmmodel', None)
            llmapikey = configure.get('llmapikey', None)
            llmendpoint = configure.get('llmendpoint', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmapikey is None: raise ValueError("llmapikey is required.")
            response = litellm.completion(
                model=llmmodel,
                api_key=llmapikey,
                endpoint=llmendpoint,
                messages=[message],)
            res = []
            for choice in response.get("choices", []):
                message = choice.get("message", {})
                res.append(dict(role=message.get("role"), content=message.get("content")))
        elif llmprov == 'azureopenai':
            llmmodel = configure.get('llmmodel', None)
            llmapikey = configure.get('llmapikey', None)
            llmendpoint = configure.get('llmendpoint', None)
            llmapiversion = configure.get('llmapiversion', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmendpoint is None: raise ValueError("llmendpoint is required.")
            if "/openai/deployments" in llmendpoint:
                llmendpoint = llmendpoint.split("/openai/deployments")[0]
            if llmapikey is None: raise ValueError("llmapikey is required.")
            if llmapiversion is None: raise ValueError("llmapiversion is required.")
            if not llmmodel.startswith("azure/"):
                llmmodel = f"azure/{llmmodel}"
            response = litellm.completion(
                model=llmmodel,
                api_key=llmapikey,
                api_base=llmendpoint,
                api_version=llmapiversion,
                base_url=llmendpoint,
                messages=[message],)
            res = []
            for choice in response.get("choices", []):
                message = choice.get("message", {})
                res.append(dict(role=message.get("role"), content=message.get("content")))
        elif llmprov == 'vertexai':
            llmprojectid = configure.get('llmprojectid', None)
            llmsvaccountfile = configure.get('llmsvaccountfile', None)
            llmmodel = configure.get('llmmodel', None)
            llmlocation = configure.get('llmlocation', None)
            llmsvaccountfile_data = configure.get('llmsvaccountfile_data', {})
            llmtemperature = configure.get('llmtemperature', None)
            llmseed = configure.get('llmseed', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmlocation is None: raise ValueError("llmlocation is required.")
            if llmsvaccountfile_data is None: raise ValueError("llmsvaccountfile_data is required.")
            from google.adk.planners import BuiltInPlanner
            from google.genai import types
            response = litellm.completion(
                model=llmmodel,
                vertex_credentials=llmsvaccountfile_data,
                vertex_location=llmlocation,
                seed=llmseed,
                temperature=llmtemperature,
                messages=[message],)
            res = []
            for choice in response.get("choices", []):
                message = choice.get("message", {})
                res.append(dict(role=message.get("role"), content=message.get("content")))
        else:
            raise ValueError(f"Unsupported LLM provider: {llmprov}")
        return self.RESP_SUCCESS, res

