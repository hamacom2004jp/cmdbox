from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli.rag import rag_base, rag_store
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class RagRegist(rag_base.RAGBase):

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
        return 'regist'

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="RAG（検索拡張生成）の登録処理を実行します。",
            description_en="Execute the RAG (Retrieval-Augmented Generation) registration process.",
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
                     description_ja="登録に使用するRAG設定の名前を指定します。",
                     description_en="Specify the name of the RAG configuration to use for registration."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=True, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="signin_file", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="groups", type=Options.T_STR, default=None, required=True, multi=True, hide=True, choice=None, web="mask",
                     description_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。",
                     description_en="Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                    description_ja="処理結果jsonの保存先ファイルを指定。",
                    description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="処理結果jsonファイルを追記保存します。",
                    description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                    description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
            ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not hasattr(args, 'rag_name') or args.rag_name is None:
            msg = dict(warn="Please specify --rag_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.rag_name):
            msg = dict(warn="RAG name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'data') or args.data is None:
            msg = dict(warn="Please specify --data")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'groups') or args.groups is None:
            msg = dict(warn="Please specify --groups")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'signin_file') or args.signin_file is None:
            msg = dict(warn="Please specify --signin_file")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        options = Options.getInstance(appcls=self.appcls, ver=self.ver)
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        # RAG設定の読込み
        st, rag_config, cl = self.load_rag_config(args, cl, tm, pf, logger)
        if st != self.RESP_SUCCESS:
            return st, rag_config, cl

        # サインイン情報を取得
        st, signin_res, _ = self.check_signin(args, tm, pf, logger)
        if st != self.RESP_SUCCESS:
            return st, signin_res, cl
        user_name = signin_res['success']['user_name']
        scope = signin_res['success']['scope']
        signin_data = signin_res['success']['signin_data']

        # Embeddingの起動
        st, embedstart_res, cl = self.embedstart(rag_config, args, cl, tm, pf, logger)
        if st != self.RESP_SUCCESS:
            return st, embedstart_res, cl

        # Extract設定の読込み
        extract_names = rag_config.get('extract', [])
        if not isinstance(extract_names, list) or len(extract_names) == 0:
            msg = dict(warn=f"RAG configuration '{args.rag_name}' does not contain valid extract names.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl

        # RagStoreの作成
        store = rag_store.RagStore.create(rag_config, logger)

        # Extract結果のRAGストアへの登録
        with store.connect() as conn:
            conn.autocommit = False
            for extract_name in extract_names:
                # Extract設定の取得
                st, extract_conf, cl = self.load_extract_config(extract_name, args, cl, tm, pf, logger)
                if st != self.RESP_SUCCESS:
                    return st, extract_conf, cl

                # Extractコマンドの取得
                st, extract_cmd_res, cl = self.load_extract_cmd(extract_conf, options, args, cl, tm, pf, logger)
                if st != self.RESP_SUCCESS:
                    return st, extract_cmd_res, cl
                extract_feat = extract_cmd_res['success']['extract_feat']
                extract_opt = extract_cmd_res['success']['extract_opt']
                extract_args = extract_cmd_res['success']['extract_args']

                # Extractコマンドの実行権限チェック
                st, check_res, _ = self.check_cmd_permission(signin_data, user_name,
                                                            extract_opt, extract_args, args, tm, pf, logger)
                if st != self.RESP_SUCCESS:
                    return st, check_res, cl

                # Extract対象ファイル一覧を取得
                marge_opt = extract_opt.copy()
                marge_opt.update(extract_conf)
                st, file_list, _ = self.list_file(marge_opt, options, args, tm, pf, logger)
                if st != self.RESP_SUCCESS:
                    return st, file_list, cl

                # ファイル一覧に対してExtractコマンドの実行とRAGストアへの登録を実施
                for k, v in file_list.items():
                    if not isinstance(v, dict) or v.get('children', None) is None:
                        continue
                    for kc, kv in v['children'].items():
                        if not isinstance(kv, dict) or kv.get('path', None) is None or kv.get('is_dir', None) is None:
                            continue
                        if kv['is_dir']:
                            continue
                        marge_opt['loadpath'] = kv['path']
                        marge_args = argparse.Namespace(**marge_opt)
                        # Extractコマンドの実行の実行
                        st, extract_res, _ = self.exec_extract_cmd(extract_feat, marge_args, options, args, tm, pf, logger)
                        if st != self.RESP_SUCCESS:
                            msg = dict(warn=f"Failed to execute extract command for file '{kv['path']}'. Skipping registration for this file. Warning: {extract_res.get('warn', 'Unknown error')}")
                            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                            continue

                        # チャンク毎に登録実施
                        for doc in extract_res:
                            if 'content' not in doc:
                                msg = dict(warn=f"Extracted document does not contain 'content' field: {doc}")
                                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                continue
                            if 'metadata' not in doc:
                                msg = dict(warn=f"Extracted document does not contain 'metadata' field: {doc}")
                                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                continue

                            # Embeddingの実行
                            st, embed_res, _ = self.embedding(rag_config, [doc['content']], args, cl, tm, pf, logger)
                            if st != self.RESP_SUCCESS:
                                return st, embed_res, cl
                            # RAGストアへの登録
                            embed_data = embed_res['data'][0]
                            vec_npy = convert.b64str2npy(embed_data['embed'], shape=embed_data['shape'], dtype=embed_data['type'])
                            vev_list = vec_npy.tolist()
                            store.insert_doc(connection=conn,
                                            servicename=args.rag_name,
                                            content_text=embed_data['data'],
                                            metadata=doc['metadata'],
                                            vec_model=rag_config.get('embed'),
                                            vec_data=vev_list)
            conn.commit()

        ret = dict(success="RAG registration completed successfully.")
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))

            rag_name = payload.get('rag_name')
            configure_path = data_dir / ".agent" / f"rag-{rag_name}.json"
            if not configure_path.exists():
                msg = dict(warn=f"Specified RAG configuration '{rag_name}' not found on server at '{str(configure_path)}'.")
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            with configure_path.open('r', encoding='utf-8') as f:
                configure = json.load(f)

            msg = dict(success=configure)
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN, msg, None
