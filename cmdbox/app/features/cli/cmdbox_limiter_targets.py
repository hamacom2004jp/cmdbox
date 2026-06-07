from cmdbox.app import common, feature
from cmdbox.app.commons import limiter, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_limiter_counter, cmdbox_limiter_list, cmdbox_limiter_load
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

    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'targets'

    def get_option(self) -> Dict[str, Any]:
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
            ]
        )

    @staticmethod
    def _limiter_matches(target_option: Dict[str, Any], feat_mode: Union[str, List[str]], feat_cmd: str) -> bool:
        if not target_option:
            return True
        if isinstance(feat_mode, list) and target_option.get('mode') not in feat_mode:
            return False
        if target_option.get('mode') != feat_mode:
            return False
        if target_option.get('cmd') != feat_cmd:
            return False
        return True

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        options = Options.getInstance()
        results: List[Dict[str, Any]] = []
        st, res, _ = self.limiter_list.apprun(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return st, res, None
        lt = res.get('success', {}).get('data', [])

        def _load_counter(limiter_name: str) -> Dict[str, Any]:
            st, res, _ = self.limiter_counter.apprun(logger, args, tm, pf)
            if st != self.RESP_SUCCESS:
                return {}
            return res.get('success', {}).get('data', {})

        for mode in options.get_mode_keys():
            for cmd in options.get_cmd_keys(mode):
                feat = options.get_cmd_attr(mode, cmd, 'feature')
                if not isinstance(feat, limiter.LimitedFeature):
                    continue
                feat_mode = feat.get_mode()
                feat_cmd = feat.get_cmd()
                matched_limiters: List[Dict[str, Any]] = []
                for entry in lt:
                    if not self._limiter_matches(entry.get('target_option'), feat_mode, feat_cmd):
                        continue
                    load_args = copy.copy(args)
                    load_args.limiter_name = entry['name']
                    # 制限設定をロード
                    st_l, res_l, _ = self.limiter_load.apprun(logger, load_args, tm, pf)
                    if st_l == self.RESP_SUCCESS:
                        cfg = res_l.get('success', {}).get('data', {})
                    else:
                        cfg = {'limiter_name': entry['name']}
                    cfg = {k:v for k,v in cfg.items() if v}
                    # Counter を取得
                    args.limiter_name = entry['name']
                    st, res, _ = self.limiter_counter.apprun(logger, args, tm, pf)
                    if st != self.RESP_SUCCESS:
                        cfg['counter'] = {}
                    else:
                        cfg['counter'] = res.get('success', {}).get('data', {})
                    matched_limiters.append(cfg)
                results.append(dict(
                    mode=feat_mode,
                    cmd=feat_cmd,
                    limiters=matched_limiters,
                ))
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
