from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_limiter_counter, cmdbox_limiter_evidences, cmdbox_limiter_list, cmdbox_limiter_load
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import copy
import logging
import pydantic
import json


class LimiterTargets(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language = None):
        super().__init__(appcls, ver, language)
        self.limiter_list = cmdbox_limiter_list.LimiterList(appcls, ver, language)
        self.limiter_load = cmdbox_limiter_load.LimiterLoad(appcls, ver, language)
        self.limiter_counter = cmdbox_limiter_counter.LimiterCounter(appcls, ver, language)
        self.limiter_evidences = cmdbox_limiter_evidences.LimiterEvidences(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'targets'

    def get_option(self) -> Dict[str, Any]:
        op = Options.getInstance(appcls=self.appcls, ver=self.ver)
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="LimitedFeature を継承しているFeature一覧を取得します。",
            description_en="Gets the list of Features that inherit from LimitedFeature.",
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
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定します。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
                dict(opt="filter_target_mode", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     choice_fn=lambda o, webmode, opt: ['']+op.get_mode_keys(),
                     description_ja="対象モードで絞り込みます。指定した場合、そのモードのみの結果を返します。",
                     description_en="Filter by target mode. If specified, returns results for that mode only."),
                dict(opt="filter_target_cmd", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {"
                             + "const res = await get_cmds($(\"[name='filter_target_mode']\").val());"
                             + "const py_load_cmd = await cmdbox.load_cmd($(\"[name='title']\").val());"
                             + "const val = py_load_cmd['filter_target_cmd'];"
                             + "$(\"[name='filter_target_cmd']\").empty();"
                             + "res.map(elm=>{$(\"[name='filter_target_cmd']\").append('<option value=\"'+elm+'\">'+elm+'</option>');});"
                             + "$(\"[name='filter_target_cmd']\").val(val);"
                             + "}",
                     description_ja="対象コマンドで絞り込みます。指定した場合、そのコマンドのみの結果を返します。",
                     description_en="Filter by target command. If specified, returns results for that command only."),
                dict(opt="filter_limiter_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リミッター名で絞り込みます。指定した場合、そのリミッター名のみの結果を返します。",
                     description_en="Filter by limiter name. If specified, returns results for that limiter only."),
                dict(opt="include_history", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="エビデンスファイルの履歴情報を含めるかどうかを指定します。`True` の場合、履歴情報は出力されます。",
                     description_en="Specifies whether to include history information in the evidence file. If set to `True`, the history information is included in the output."),
            ]
        )

    @staticmethod
    def _limiter_matches(entry: Dict[str, Any], feat_mode: Union[str, List[str]], feat_cmd: str) -> bool:
        target_mode = entry.get('target_mode')
        if target_mode:
            if isinstance(feat_mode, list):
                if str(target_mode) not in [str(m) for m in feat_mode]:
                    return False
            elif str(feat_mode) != str(target_mode):
                return False

        target_cmd = entry.get('target_cmd')
        if target_cmd:
            if str(feat_cmd) != str(target_cmd):
                return False

        target_option = entry.get('target_option')
        if target_option:
            if isinstance(feat_mode, list) and target_option.get('mode') not in feat_mode:
                return False
            if not isinstance(feat_mode, list) and target_option.get('mode') and target_option.get('mode') != feat_mode:
                return False
            if target_option.get('cmd') and target_option.get('cmd') != feat_cmd:
                return False

        return True

    def _collect_targets(self, options: Options, lt: List[Dict[str, Any]], filter_target_mode: Union[str, None],
                         filter_target_cmd: Union[str, None], filter_limiter_name: Union[str, None],
                         resolver_fn) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for mode in options.get_mode_keys():
            # target_mode で絞り込み
            if filter_target_mode and str(mode) != str(filter_target_mode):
                continue

            for cmd in options.get_cmd_keys(mode):
                # target_cmd で絞り込み
                if filter_target_cmd and str(cmd) != str(filter_target_cmd):
                    continue

                feat = options.get_cmd_attr(mode, cmd, 'feature')
                if not isinstance(feat, limiter.LimitedFeature):
                    continue
                feat_mode = feat.get_mode()
                feat_cmd = feat.get_cmd()
                matched_limiters: List[Dict[str, Any]] = []
                for entry in lt:
                    # limiter_name で絞り込み
                    if filter_limiter_name and str(entry['name']) != str(filter_limiter_name):
                        continue

                    if not self._limiter_matches(entry, feat_mode, feat_cmd):
                        continue

                    cfg = resolver_fn(entry)
                    matched_limiters.append(cfg)

                if filter_limiter_name and not matched_limiters:
                    continue
                results.append(dict(
                    mode=feat_mode,
                    cmd=feat_cmd,
                    limiters=matched_limiters,
                ))
        return results

    def _resolve_limiter_client(self, logger: logging.Logger, args: argparse.Namespace, tm: float,
                                pf: List[Dict[str, float]], entry: Dict[str, Any]) -> Dict[str, Any]:
        load_args = copy.copy(args)
        load_args.limiter_name = entry['name']
        # 制限設定をロード
        st_l, res_l, _ = self.limiter_load.apprun(logger, load_args, tm, pf)
        if st_l == self.RESP_SUCCESS:
            cfg = res_l.get('success', {}).get('data', {})
        else:
            cfg = {'limiter_name': entry['name']}
        cfg = {k: v for k, v in cfg.items() if v}

        # Counter を取得
        st_c, res_c, _ = self.limiter_counter.apprun(logger, load_args, tm, pf)
        if st_c != self.RESP_SUCCESS:
            cfg['counter'] = {}
        else:
            cfg['counter'] = res_c.get('success', {}).get('data', {})

        # Evidences を取得
        ev_args = copy.copy(args)
        ev_args.limiter_name = entry['name']
        ev_args.include_history = getattr(args, 'include_history', False)
        st_e, res_e, _ = self.limiter_evidences.apprun(logger, ev_args, tm, pf)
        if st_e == self.RESP_SUCCESS:
            cfg['evidences'] = res_e.get('success', {}).get('data', [])
        else:
            cfg['evidences'] = []
        return cfg

    def _resolve_limiter_server(self, data_dir: Any, logger: logging.Logger, redis_cli: redis_client.RedisClient,
                                limiter_name: str, scope: str = 'server', include_history: bool = False) -> Dict[str, Any]:
        try:
            cfg = self.limiter_load._load_limiter_config(data_dir, limiter_name)
        except FileNotFoundError:
            cfg = {'limiter_name': limiter_name}
        cfg = {k: v for k, v in cfg.items() if v}
        cfg['counter'] = self.limiter_counter._load_limiter_counter(data_dir, limiter_name, redis_cli, logger,
                                                                    scope=scope, load_history=include_history)
        cfg['evidences'] = self.limiter_evidences._load_evidences(data_dir, limiter_name, include_history=include_history)
        return cfg

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        scope = getattr(args, 'scope', 'server')

        if scope == 'server':
            payload = dict(
                filter_target_mode=getattr(args, 'filter_target_mode', None),
                filter_target_cmd=getattr(args, 'filter_target_cmd', None),
                filter_limiter_name=getattr(args, 'filter_limiter_name', None),
                include_history=getattr(args, 'include_history', False),
            )
            payload_b64 = convert.str2b64str(common.to_str(payload))
            cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in ret:
                return self.RESP_WARN, ret, cl
            return self.RESP_SUCCESS, ret, cl

        options = Options.getInstance()
        st, res, _ = self.limiter_list.apprun(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return st, res, None
        lt = res.get('success', {}).get('data', [])

        # 絞り込み条件を取得
        filter_target_mode = getattr(args, 'filter_target_mode', None)
        filter_target_cmd = getattr(args, 'filter_target_cmd', None)
        filter_limiter_name = getattr(args, 'filter_limiter_name', None)

        results = self._collect_targets(
            options,
            lt,
            filter_target_mode,
            filter_target_cmd,
            filter_limiter_name,
            lambda entry: self._resolve_limiter_client(logger, args, tm, pf, entry),
        )

        ret = dict(success=dict(data=results))
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS, ret, None

    def output_schema(self) -> type:
        class TargetRecord(resdata.Base):
            mode: Union[str, List[str]] = pydantic.Field(..., description="フィーチャーのモード")
            cmd: str = pydantic.Field(..., description="フィーチャーのコマンド")
            limiters: List[Dict[str, Any]] = pydantic.Field(default_factory=list, description="適合する制限設定の詳細内容リスト")
        class Data(resdata.Data):
            data: List[TargetRecord] = pydantic.Field(default_factory=list, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir: Any, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            options = Options.getInstance()
            filter_target_mode = payload.get('filter_target_mode', None)
            filter_target_cmd = payload.get('filter_target_cmd', None)
            filter_limiter_name = payload.get('filter_limiter_name', None)
            include_history = payload.get('include_history', False)

            lt: List[Dict[str, Any]] = []
            limiter_dir = data_dir / '.limiter'
            if limiter_dir.exists() and limiter_dir.is_dir():
                for p in sorted(limiter_dir.glob("limiter-*.json")):
                    name = p.stem
                    if not name.startswith('limiter-'):
                        continue
                    with p.open('r', encoding='utf-8') as f:
                        cfg = json.load(f)
                    lt.append(dict(
                        name=name[len('limiter-'):],
                        limiter_title=cfg.get('limiter_title', None),
                        target_mode=cfg.get('target_mode', None),
                        target_cmd=cfg.get('target_cmd', None),
                        target_option=cfg.get('target_option', None),
                        history_end=cfg.get('history_end', None),
                    ))

            results = self._collect_targets(
                options,
                lt,
                filter_target_mode,
                filter_target_cmd,
                filter_limiter_name,
                lambda entry: self._resolve_limiter_server(data_dir, logger, redis_cli, entry['name'],
                                                           scope='server', include_history=include_history),
            )

            redis_cli.rpush(reskey, dict(success=dict(data=results)))
            return self.RESP_SUCCESS
        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
