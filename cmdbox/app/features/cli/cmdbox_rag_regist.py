from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, validator
from cmdbox.app.features.cli.rag import rag_base, rag_store
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class RagRegist(rag_base.RAGBase, validator.Validator):

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
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
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
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="groups", type=Options.T_STR, default=None, required=True, multi=True, hide=True, choice=None, web="mask",
                     description_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。",
                     description_en="Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."),
            ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl

        if not re.match(r'^[\w\-]+$', args.rag_name):
            msg = dict(warn="RAG name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        options = Options.getInstance(appcls=self.appcls, ver=self.ver)
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        try:
            # RAG設定の読込み
            self.put_resqueue(args, dict(process=dict(message="Loading RAG configuration...")))
            st, rag_config, cl = self.load_rag_config(args, cl, tm, pf, logger)
            if st != self.RESP_SUCCESS:
                return st, rag_config, cl

            # サインイン情報を取得
            self.put_resqueue(args, dict(process=dict(message="Checking signin information...")))
            st, signin_res, _ = self.check_signin(args, tm, pf, logger)
            if st != self.RESP_SUCCESS:
                return st, signin_res, cl
            user_name = signin_res['success']['user_name']
            scope = signin_res['success']['scope']
            signin_data = signin_res['success']['signin_data']

            # Embeddingの起動
            self.put_resqueue(args, dict(process=dict(message="Starting embedding...")))
            st, embedstart_res, cl = self.embedstart(rag_config, args, cl, tm, pf, logger)
            if st != self.RESP_SUCCESS:
                return st, embedstart_res, cl

            # Extract設定の読込み
            self.put_resqueue(args, dict(process=dict(message="Loading extract configuration...")))
            extract_names = rag_config.get('extract', [])
            if not isinstance(extract_names, list) or len(extract_names) == 0:
                msg = dict(warn=f"RAG configuration '{args.rag_name}' does not contain valid extract names.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, cl

            # RagStoreの作成
            self.put_resqueue(args, dict(process=dict(message="Creating RAG store...")))
            store = rag_store.RagStore.create(rag_config, logger)

            # Extract結果のRAGストアへの登録
            with store.connect() as conn:
                conn.autocommit = False
                if args.savetype == 'per_service':
                    self.put_resqueue(args, dict(process=dict(message=f"Deleting existing RAG documents...servicename={args.rag_name}")))
                    store.delete_doc(connection=conn, servicename=args.rag_name,)
                for extract_name in extract_names:
                    # Extract設定の取得
                    self.put_resqueue(args, dict(process=dict(message=f"Loading extract configuration...extract_name={extract_name}")))
                    st, extract_conf, cl = self.load_extract_config(extract_name, args, cl, tm, pf, logger)
                    if st != self.RESP_SUCCESS:
                        msg = dict(warn=f"Failed to load extract configuration for '{extract_name}'.", res=extract_conf)
                        self.put_resqueue(args, msg)
                        return st, extract_conf, cl

                    # Extractコマンドの取得
                    self.put_resqueue(args, dict(process=dict(message=f"Loading extract command...extract_name={extract_name}")))
                    st, extract_cmd_res, cl = self.load_extract_cmd(extract_conf, options, args, cl, tm, pf, logger)
                    if st != self.RESP_SUCCESS:
                        msg = dict(warn=f"Failed to load extract command for '{extract_name}'.", res=extract_cmd_res)
                        self.put_resqueue(args, msg)
                        return st, extract_cmd_res, cl
                    extract_feat = extract_cmd_res['success']['extract_feat']
                    extract_opt = extract_cmd_res['success']['extract_opt']
                    extract_args = extract_cmd_res['success']['extract_args']

                    # Extractコマンドの実行権限チェック
                    self.put_resqueue(args, dict(process=dict(message=f"Checking permission for extract command...extract_name={extract_name}")))
                    st, check_res, _ = self.check_cmd_permission(signin_data, user_name,
                                                                extract_opt, extract_args, args, tm, pf, logger)
                    if st != self.RESP_SUCCESS:
                        msg = dict(warn=f"Permission check failed for extract command '{extract_name}'.", res=check_res)
                        self.put_resqueue(args, msg)
                        return st, check_res, cl

                    # Extract対象ファイル一覧を取得
                    marge_opt = extract_opt.copy()
                    marge_opt.update(extract_conf)
                    self.put_resqueue(args, dict(process=dict(message=f"Listing target files for extract command...extract_name={extract_name}")))
                    st, file_list, _ = self.list_file(marge_opt, options, args, tm, pf, logger)
                    if st != self.RESP_SUCCESS:
                        msg = dict(warn=f"Failed to list target files for extract command '{extract_name}'.", res=file_list)
                        self.put_resqueue(args, msg)
                        return st, file_list, cl

                    # ファイル一覧に対してExtractコマンドの実行とRAGストアへの登録を実施
                    for k, v in file_list.items():
                        if not isinstance(v, dict) or v.get('children', None) is None:
                            continue
                        children_count = len(v['children'])
                        children_index = 0
                        for kc, kv in v['children'].items():
                            children_index += 1
                            if not isinstance(kv, dict) or kv.get('path', None) is None or kv.get('is_dir', None) is None:
                                continue
                            if kv['is_dir']:
                                continue
                            marge_opt['loadpath'] = kv['path']
                            marge_args = argparse.Namespace(**marge_opt)
                            # Extractコマンドの実行の実行
                            self.put_resqueue(args, dict(process=dict(message=f"({children_index}/{children_count}) Executing extract command...file={kv['path']}",
                                                                      count=children_count, index=children_index, filename=Path(kv['path']).name)))
                            st, extract_res, _ = self.exec_extract_cmd(extract_feat, marge_args, options, args, tm, pf, logger)
                            if st != self.RESP_SUCCESS:
                                msg = dict(warn=f"Failed to execute extract command for file '{kv['path']}'. Skipping registration for this file.", res=extract_res)
                                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                self.put_resqueue(args, msg)
                                continue
                            # save_typeの処理
                            if args.savetype == 'per_doc':
                                self.put_resqueue(args, dict(process=dict(message=f"Deleting existing documents for file '{marge_opt['loadpath']}'",
                                                                          filename=Path(marge_opt['loadpath']).name)))
                                store.delete_doc(connection=conn, servicename=args.rag_name, origin_name=marge_opt['loadpath'],)

                            # チャンク毎に登録実施
                            doc_count = len(extract_res)
                            doc_index = 0
                            doc_bcount = 50
                            for i in range(0, len(extract_res), doc_bcount):
                                docs = extract_res[i:i+doc_bcount]
                                doc_index += len(docs)
                                if len([doc for doc in docs if 'content' not in doc]) > 0:
                                    msg = dict(warn=f"Extracted document does not contain 'content' field.")
                                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                    continue
                                if len([doc for doc in docs if 'metadata' not in doc]) > 0:
                                    msg = dict(warn=f"Extracted document does not contain 'metadata' field.")
                                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                    self.put_resqueue(args, msg)
                                    continue

                                # Embeddingの実行
                                self.put_resqueue(args, dict(process=dict(message=f"({doc_index}/{doc_count}) Executing embedding for extracted document...file={marge_opt['loadpath']}",
                                                                          count=doc_count, index=doc_index, filename=Path(marge_opt['loadpath']).name)))
                                st, embed_res, _ = self.embedding(rag_config, [doc['content'] for doc in docs], args, cl, tm, pf, logger)
                                if st != self.RESP_SUCCESS:
                                    msg = dict(warn=f"Failed to execute embedding for extracted document from file '{kv['path']}'.", res=embed_res)
                                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                    self.put_resqueue(args, msg)
                                    return st, embed_res, cl
                                # RAGストアへの登録
                                self.put_resqueue(args, dict(process=dict(message=f"({doc_index}/{doc_count}) Registering extracted document to RAG store...file={marge_opt['loadpath']}",
                                                                          count=doc_count, index=doc_index, filename=Path(marge_opt['loadpath']).name)))
                                for embed_i, embed_data in enumerate(embed_res.get('data', [])):
                                    vec_npy = convert.b64str2npy(embed_data['embed'], shape=embed_data['shape'], dtype=embed_data['type'])
                                    vev_list = vec_npy.tolist()
                                    store.insert_doc(connection=conn,
                                                    servicename=args.rag_name,
                                                    content_text=embed_data['data'],
                                                    origin_name=marge_opt['loadpath'],
                                                    metadata=docs[embed_i]['metadata'],
                                                    vec_model=rag_config.get('embed'),
                                                    vec_data=vev_list)
                                conn.commit()

            ret = dict(success="RAG registration completed successfully.")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            self.put_resqueue(args, ret)
            if 'success' not in ret:
                return self.RESP_WARN, ret, cl
            return self.RESP_SUCCESS, ret, cl
        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            self.put_resqueue(args, msg)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl
