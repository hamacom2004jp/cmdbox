from cmdbox.app import common, client, feature
from cmdbox.app.options import Options
from cmdbox.app.commons import convert
from cmdbox.app.features.cli import (
    cmdbox_client_file_list,
    cmdbox_cmd_load,
    cmdbox_embed_start,
    cmdbox_embed_embedding,
    cmdbox_extract_load,
    cmdbox_rag_load,
)
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class RAGBase(feature.ResultEdgeFeature):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)
        self.cmdload = cmdbox_cmd_load.CmdLoad(appcls, ver, language)
        self.ragload = cmdbox_rag_load.RagLoad(appcls, ver, language)
        self.embedstarter = cmdbox_embed_start.EmbedStart(appcls, ver, language)
        self.embedembedding = cmdbox_embed_embedding.EmbedEmbedding(appcls, ver, language)
        self.extractload = cmdbox_extract_load.ExtractLoad(appcls, ver, language)
        self.client_file_list = cmdbox_client_file_list.ClientFileList(appcls, ver, language)

    def load_rag_config(self, args:argparse.Namespace, cl:client.Client, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], client.Client]:
        """
        RAG設定の読込みを行います

        Args:
            args (argparse.Namespace): 引数
            cl (client.Client): クライアント
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], client.Client]: 終了コード, RAG設定, クライアント
        """
        ragload_payload = dict(rag_name=args.rag_name)
        ragload_payload_b64 = convert.str2b64str(common.to_str(ragload_payload))
        ragload_res = cl.redis_cli.send_cmd(self.ragload.get_svcmd(), [ragload_payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        if 'success' not in ragload_res:
            common.print_format(ragload_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ragload_res, cl
        rag_config = ragload_res['success']
        if 'extract' not in rag_config or not rag_config['extract'] or len(rag_config['extract']) == 0:
            msg = dict(warn=f"RAG configuration '{args.rag_name}' does not contain any extract names.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl
        return self.RESP_SUCCESS, rag_config, cl

    def check_signin(self, args:argparse.Namespace, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], None]:
        """
        サインイン情報の確認を行います

        Args:
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], None]: 終了コード, サインイン情報, None
        """
        from cmdbox.app.auth import signin
        scope = signin.get_request_scope()
        signin_data = signin.Signin.load_signin_file(args.signin_file)
        req = scope.get("req") if scope.get("req") is not None else scope.get("websocket")
        if req is None:
            msg = dict(warn=f"Request information cannot be retrieved. This command is only available in web mode.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        sign = signin.Signin._check_signin(req, scope.get("res"), signin_data, logger)
        if sign is not None or "signin" not in req.session or "groups" not in req.session["signin"]:
            msg = dict(warn=f"Login information cannot be retrieved.This command is only available in web mode.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        user_name = req.session["signin"]["name"]
        msg = dict(success=dict(user_name=user_name, scope=scope, signin_data=signin_data))
        return self.RESP_SUCCESS, msg, None

    def embedstart(self, rag_config:Dict, args:argparse.Namespace, cl:client.Client, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], client.Client]:
        """
        Embed start処理を行います

        Args:
            rag_config (Dict): RAG設定
            args (argparse.Namespace): 引数
            cl (client.Client): クライアント
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], client.Client]: 終了コード, 結果, クライアント
        """
        embedstart_payload = dict(embed_name=rag_config.get('embed', 'None'))
        embedstart_payload_b64 = convert.str2b64str(common.to_str(embedstart_payload))
        embedstart_res = cl.redis_cli.send_cmd(self.embedstarter.get_svcmd(), [embedstart_payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        if 'success' not in embedstart_res:
            common.print_format(embedstart_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, embedstart_res, cl
        return self.RESP_SUCCESS, embedstart_res['success'], cl
    
    def embedding(self, rag_config:Dict, original_data:List[Any], args:argparse.Namespace, cl:client.Client, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], client.Client]:
        """
        Embed embedding処理を行います

        Args:
            rag_config (Dict): RAG設定
            original_data (List[Any]): 埋め込み対象の元データ
            args (argparse.Namespace): 引数
            cl (client.Client): クライアント
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], client.Client]: 終了コード, 結果, クライアント
        """
        if 'embed' not in rag_config or rag_config['embed'] is None:
            msg = dict(warn=f"RAG configuration does not specify embed model name.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl
        if original_data is None:
            msg = dict(warn=f"Original data for embedding is None.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl
        embedding_payload = dict(embed_name=rag_config.get('embed'), original_data=original_data)
        embedding_payload_b64 = convert.str2b64str(common.to_str(embedding_payload))
        embedding_res = cl.redis_cli.send_cmd(self.embedembedding.get_svcmd(), [embedding_payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        if 'success' not in embedding_res:
            common.print_format(embedding_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, embedding_res, cl
        return self.RESP_SUCCESS, embedding_res['success'], cl

    def load_extract_config(self, extract_name:str, args:argparse.Namespace, cl:client.Client, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], client.Client]:
        """
        Extract設定の読込みを行います

        Args:
            extract_name (str): Extract設定の名前
            args (argparse.Namespace): 引数
            cl (client.Client): クライアント
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], client.Client]: 終了コード, Extract設定, クライアント
        """
        extractload_payload = dict(extract_name=extract_name)
        extractload_payload_b64 = convert.str2b64str(common.to_str(extractload_payload))
        extractload_res = cl.redis_cli.send_cmd(self.extractload.get_svcmd(), [extractload_payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        if 'success' not in extractload_res:
            common.print_format(extractload_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, extractload_res, cl
        return self.RESP_SUCCESS, extractload_res['success'], cl

    def load_extract_cmd(self, extract_conf:Dict, options:Options, args:argparse.Namespace, cl:client.Client, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], client.Client]:
        """
        Extractコマンドの読込みを行います

        Args:
            extract_conf (Dict): Extract設定
            options (Options): オプション
            args (argparse.Namespace): 引数
            cl (client.Client): クライアント
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], client.Client]: 終了コード, Extractコマンド情報, クライアント
        """
        cmd_title = extract_conf.get('extract_cmd')
        cmd_args = argparse.Namespace(cmd_title=cmd_title, data=args.data, signin_file=args.signin_file, groups=args.groups,
                                    format=args.format, output_json=args.output_json, output_json_append=args.output_json_append)
        st, cmd_res, _ = self.cmdload.apprun(logger, cmd_args, tm, pf)
        if 'success' not in cmd_res:
            common.print_format(cmd_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, cmd_res, cl
        extract_opt:dict = cmd_res['success']
        extract_feat = options.get_cmd_attr(extract_opt.get('mode'), extract_opt.get('cmd'), 'feature')
        extract_opt.update(dict(data=args.data, signin_file=args.signin_file, groups=args.groups,
            format=args.format, output_json=args.output_json, output_json_append=args.output_json_append))
        extract_args = argparse.Namespace(**extract_opt)
        msg = dict(success=dict(extract_feat=extract_feat, extract_opt=extract_opt, extract_args=extract_args))
        return self.RESP_SUCCESS, msg, cl

    def check_cmd_permission(self, signin_data:Dict, user_name:str, extract_opt:dict, extract_args:argparse.Namespace, args:argparse.Namespace, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], None]:
        """
        Extractコマンドの実行権限チェックを行います

        Args:
            signin_data (Dict): サインイン情報
            user_name (str): ユーザー名
            extract_opt (dict): Extractコマンドのオプション
            extract_args (argparse.Namespace): Extractコマンドの引数
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], None]: 終了コード, チェック
        """
        from cmdbox.app.auth import signin
        sign = signin.Signin._check_cmd(signin_data, args.groups,
                                        extract_opt.get('mode'), extract_opt.get('cmd'),
                                        extract_opt, user_name, logger)
        if not sign:
            msg = dict(warn=f"You do not have permission to execute the extract command '{extract_opt.get('title')}' required for RAG registration."
                            f" mode={extract_opt.get('mode')}, cmd={extract_opt.get('cmd')}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        return self.RESP_SUCCESS, None, None

    def list_file(self, file_list_opt:Dict, options:Options, args:argparse.Namespace, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], None]:
        """
        Extract対象ファイル一覧の取得を行います

        Args:
            file_list_opt (Dict): ClientFileListコマンドのオプション
            options (Options): オプション
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], None]: 終了コード, Extract対象ファイル一覧, None
        """
        file_list_opt.update(dict(svpath=file_list_opt.get('loadpath', '/'),
                                  listregs=file_list_opt.get('loadregs', '.*')))
        file_list_args = argparse.Namespace(**file_list_opt)
        st, list_file_res, _ = self.client_file_list.apprun(logger, file_list_args, tm, pf)
        if 'success' not in list_file_res:
            common.print_format(list_file_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, list_file_res, None
        return self.RESP_SUCCESS, list_file_res['success'], None

    def exec_extract_cmd(self, extract_feat:feature.Feature, extract_args:argparse.Namespace, options:Options, args:argparse.Namespace, tm:float, pf, logger:logging.Logger) -> Tuple[int, Dict[str, Any], None]:
        """
        Extractコマンドの実行を行います

        Args:
            extract_feat (feature.Feature): Extractコマンドの機能
            extract_args (argparse.Namespace): Extractコマンドの引数
            options (Options): オプション
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf: パフォーマンス情報
            logger (logging.Logger): ロガー
        Returns:
            Tuple[int, Dict[str, Any], None]: 終了コード, 実行結果
        """
        if extract_feat is not None and isinstance(extract_feat, feature.Feature):
            options.audit_exec(extract_args, logger, extract_feat, audit_type=Options.AT_EVENT)
            _, extract_res, _ = common.exec_sync(extract_feat.apprun, logger, extract_args, tm, pf, True)
        else:
            msg = dict(warn=f"Not Found feature. mode={extract_args.mode}, cmd={extract_args.cmd}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if 'success' not in extract_res:
            common.print_format(extract_res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, extract_res, None
        return self.RESP_SUCCESS, extract_res['success'].get('data', []), None
