from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, validator
from cmdbox.app.features.cli.rag import rag_base, rag_store
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import re


class RagSearch(rag_base.RAGBase, validator.Validator):

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
        return 'search'

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
            description_ja="RAG（検索拡張生成）の検索処理を実行します。",
            description_en="Execute the RAG (Retrieval-Augmented Generation) search process.",
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
                dict(opt="timeout", type=Options.T_INT, default=600, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="rag_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('rag','list',{},(res)=>{"
                            + "const val = $(\"[name='rag_name']\").val();"
                            + "$(\"[name='rag_name']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='rag_name']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='rag_name']\").val(val);"
                            + "},$(\"[name='title']\").val(),'rag_name');"
                            + "}",
                     description_ja="登録に使用するRAG設定の名前を指定します。",
                     description_en="Specify the name of the RAG configuration to use for registration."),
                dict(opt="query", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="検索クエリーを指定します。",
                     description_en="Specifies a search query."),
                dict(opt="kcount", type=Options.T_INT, default=5, required=True, multi=False, hide=False, choice=None,
                     description_ja="検索結果件数を指定します。フィルタ条件を指定するとここで指定した件数の中からフィルタします。",
                     description_en="Specify the number of search results. If filter conditions are specified, the results will be filtered from the number of results specified here."),
                dict(opt="select", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="取得する項目を指定します。未指定の場合はすべての項目を返します。",
                     description_en="Specifies the items to be retrieved. If not specified, all items are returned."),
                dict(opt="filter_origin_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="フィルタ条件のorigin_nameを指定します。",
                     description_en="Specifies the origin_name of the filter condition."),
                dict(opt="filter_dict", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="任意のフィルタ条件を指定します。cmetaの項目名と項目値を複数指定できます。項目値は `％` を使用することであいまい検索できます。 {args.query}という表記を含めるとqueryパラメータの値を使用できます。",
                     description_en="Specify arbitrary filter conditions, allowing multiple cmeta item names and values. Item values can be ambiguously searched by using `％`.  You can use the value of the query parameter by including the notation {args.query}."),
                dict(opt="sort_dict", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=['', 'ASC', 'DESC'],
                     description_ja="queryを指定しないときのソート条件を指定します。cmetaの項目名とソート順（ `ASC` (昇順) 又は `DESC` (降順)）を複数指定できます。",
                     description_en="Specifies the sort conditions when no query is specified. Multiple cmeta field names and sort orders (`ASC` (ascending) or `DESC` (descending)) can be specified."),
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

            # RagStoreの作成
            store = rag_store.RagStore.create(rag_config, logger)

            # Extract結果のRAGストアの検索を実行
            with store.connect() as conn:
                conn.autocommit = False
                # フィルタ条件の作成
                filter_dict = {}
                if args.filter_dict is not None and isinstance(args.filter_dict, dict):
                    for k, v in args.filter_dict.items():
                        if k is not None and v is not None:
                            filter_dict[k] = eval(f'f"{v}"', dict(re=re), dict(args=args))
                vec_data = None
                if args.query is not None:
                    # Embeddingの実行
                    st, embed_res, _ = self.embedding(rag_config, [args.query], args, cl, tm, pf, logger)
                    if st != self.RESP_SUCCESS:
                        msg = dict(warn=f"Failed to execute embedding for query '{args.query}'.", res=embed_res)
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return st, embed_res, cl
                    embed_data = embed_res['data'][0]
                    embed_npy = convert.b64str2npy(embed_data['embed'], shape=embed_data['shape'], dtype=embed_data['type'])
                    vec_data = common.to_str(embed_npy.tolist())

                # 検索
                recodes = store.select_doc(connection=conn, select=args.select,
                                           servicename=args.rag_name, origin_name=args.filter_origin_name,
                                           vec_data=vec_data, kcount=args.kcount, metadata=filter_dict)
                res = [record for record in recodes]
                ret = dict(success=res)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                if 'success' not in ret:
                    return self.RESP_WARN, ret, cl
                return self.RESP_SUCCESS, ret, cl
        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, cl
