from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import re


class RagSave(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'rag'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'save'

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="RAG（検索拡張生成）の設定を保存します。",
            description_en="Saves the settings for RAG (Retrieval-Augmented Generation).",
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
                     description_ja="サーバーのサービス名を指定します。",
                     description_en="Specify the service name of the inference server."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。",
                     description_en="Specifies the number of reconnections to the Redis server."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="rag_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="RAG設定の名前を指定します。",
                     description_en="Specify the name of the RAG configuration."),
                dict(opt="rag_datasource", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('datasource','list',{},(res)=>{"
                            + "const val = $(\"[name='rag_datasource']\").val();"
                            + "$(\"[name='rag_datasource']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='rag_datasource']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='rag_datasource']\").val(val);"
                            + "},$(\"[name='title']\").val(),'rag_datasource');"
                            + "}",
                    description_ja="RAGの保存先データソースを指定します。",
                    description_en="Specify the data source where RAG will be stored."),
                dict(opt="extract", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('extract','list',{},(res)=>{"
                             + "const val = $(\"[name='extract']\").val();"
                             + "$(\"[name='extract']\").empty().append('<option></option>');"
                             + "res['data'].map(elm=>{$(\"[name='extract']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='extract']\").val(val);"
                             + "},$(\"[name='title']\").val(),'extract');"
                             + "}",
                     description_ja="RAGで使用するExtract処理の登録名を指定します。候補がない場合はextractモードのコマンドの登録が必要です。",
                     description_en="Specify the registered name for the Extract process used in RAG. If no candidates exist, you must register a command in extract mode."),
                dict(opt="embed", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('embed','list',{},(res)=>{"
                             + "const val = $(\"[name='embed']\").val();"
                             + "$(\"[name='embed']\").empty().append('<option></option>');"
                             + "res['data'].map(elm=>{$(\"[name='embed']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='embed']\").val(val);"
                             + "},$(\"[name='title']\").val(),'embed');"
                             + "}",
                     description_ja="エンベッドモデルの登録名を指定します。",
                     description_en="Specify the registration name of the embed model."),
                dict(opt="embed_vector_dim", type=Options.T_INT, default=256, required=False, multi=False, hide=False, choice=None,
                     description_ja="Embed時のベクトル次元数を指定します。",
                     description_en="Specify the vector dimension for embedding."),
                dict(opt="savetype", type=Options.T_STR, default="per_doc", required=False, multi=False, hide=False, choice=["per_doc", "per_service", "add_only"],
                    description_ja="保存パターンを指定します。 `per_doc` :ドキュメント単位、 `per_service` :サービス単位、 `add_only` :追加のみ",
                    description_en="Specify the storage pattern. `per_doc` :per document, `per_service` :per service, `add_only` :add only",),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:

        payload = dict(
            rag_name=args.rag_name,
            rag_datasource=args.rag_datasource if hasattr(args, 'rag_datasource') else None,
            savetype=args.savetype,
            extract=list(set(args.extract)) if hasattr(args, 'extract') and args.extract is not None else None,
            embed=args.embed if hasattr(args, 'embed') else None,
            embed_vector_dim=args.embed_vector_dim if hasattr(args, 'embed_vector_dim') else None,
        )

        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))

            configure_path = data_dir / ".agent" / f"rag-{configure['rag_name']}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"RAG configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
