from cmdbox.app import common, feature
from cmdbox.app.commons import redis_client
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import argparse
import functools
import json
import logging
import time


def _apprun_pre(self:'LimitedFeature', logger:logging.Logger, args:argparse.Namespace) -> Tuple[int, Dict[str, Any], Any]:
    """
    コマンドの実行制限を検証します。

    Args:
        logger (logging.Logger): ロガー
        args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
    Returns:
        Tuple[int, Dict[str, Any], Any]: ステータス、メッセージ、制限オブジェクト
    """
    mode = getattr(args, 'mode', None)
    cmd = getattr(args, 'cmd', None)
    host = getattr(args, 'host', None)
    port = getattr(args, 'port', None)
    password = getattr(args, 'password', None)
    svname = getattr(args, 'svname', None)
    client_data_path = getattr(args, 'client_data', None)
    if not (host and port and password and svname):
        msg = dict(warn=f"The limiter check is enabled, but the connection information for the Redis server is incomplete. mode={mode}, cmd={cmd}")
        return -1, msg, None
    if not client_data_path or not Path(client_data_path).is_dir():
        msg = dict(warn=f"The limiter check is enabled, but the client_data option is not enabled. mode={mode}, cmd={cmd}")
        return -1, msg, None
    redis_cli = redis_client.RedisClient(logger, host=host, port=port, password=password, svname=svname) if host and port and password and svname else None
    limit = Limiter.getInstance(redis_cli, flush_interval=10, reload_interval=60)
    st, msg = limit.check(feat=self, data_dir=Path(client_data_path), logger=logger, command_options=args.__dict__, scope='client')
    return st, msg, limit

def _apprun_post(self:'LimitedFeature', stime:float, msg:Dict[str, Any], data_dir:Path, logger:logging.Logger, args:argparse.Namespace, limit:'Limiter'):
    """
    コマンド実行後のカウンタ更新を行います。

    Args:
        stime (float): コマンド実行開始時間
        msg (Dict[str, Any]): コマンドの実行結果
        data_dir (Path): データディレクトリのパス
        logger (logging.Logger): ロガー
        args (argparse.Namespace): コマンドの引数
        limit (Limiter): 制限オブジェクト
    """
    # コマンド実行後のカウンタ更新
    exec_time = common.perf_counter() - stime
    input_bytes = len(common.to_str(args.__dict__).encode('utf-8'))
    output_bytes = len(common.to_str(msg).encode('utf-8'))
    process_bytes = self.apprun_process_bytes(data_dir, logger, args, msg)
    registrations = self.apprun_registrations(data_dir, logger, args, msg)
    limit.update(feat=self, data_dir=data_dir, logger=logger, command_options=args.__dict__,
                    exec_time=exec_time, input_bytes=input_bytes, process_bytes=process_bytes,
                    output_bytes=output_bytes, registrations=registrations)

def apprun_check_limit(func: Callable) -> Callable:
    """
    コマンドの実行制限を検証するデコレーター。
    LimitedFeature を継承したクラスのコマンド実行関数に適用することで、コマンドの実行前に制限チェックを行い、実行後にカウンタを更新します。
    それ以外の関数に適用された場合は、単純に元の関数を実行します。

    Args:
        func (Callable): コマンドの実行関数
    Returns:
        Callable: デコレーターでラップされた関数
    """
    #@functools.wraps(func)
    def wrapper(self:'LimitedFeature', logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        if not isinstance(self, LimitedFeature):
            return func(self, logger, args, tm, pf)
        # コマンドの実行前に制限チェック
        limit_st, msg, limit = _apprun_pre(self, logger, args)
        if limit_st == Limiter.CHECK_DENY:
            return feature.Feature.RESP_WARN, msg, None
        stime = common.perf_counter()
        # コマンドの実行
        st, msg, obj = func(self, logger, args, tm, pf)
        if st == feature.Feature.RESP_SUCCESS and limit_st == Limiter.CHECK_ALLOW:
            try:
                # コマンド実行後のカウンタ更新
                _apprun_post(self, stime, msg, Path(args.client_data), logger, args, limit)
            except Exception as e:
                st = feature.Feature.RESP_ERROR
                msg = dict(error=f"Failed to update limiter counter: {e}")
                logger.error(msg)
        return st, msg, obj
    return wrapper

def async_apprun_check_limit(func: Callable) -> Callable:
    """
    コマンドの実行制限を検証するデコレーター。
    LimitedFeature を継承したクラスのコマンド実行関数に適用することで、コマンドの実行前に制限チェックを行い、実行後にカウンタを更新します。
    それ以外の関数に適用された場合は、単純に元の関数を実行します。

    Args:
        func (Callable): コマンドの実行関数
    Returns:
        Callable: デコレーターでラップされた関数
    """
    @functools.wraps(func)
    async def wrapper(self:'LimitedFeature', logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        if not isinstance(self, LimitedFeature):
            return await func(self, logger, args, tm, pf)
        # コマンドの実行前に制限チェック
        limit_st, msg, limit = _apprun_pre(self, logger, args)
        if limit_st == Limiter.CHECK_DENY:
            return feature.Feature.RESP_WARN, msg, None
        stime = common.perf_counter()
        # コマンドの実行
        st, msg, obj = await func(self, logger, args, tm, pf)
        # コマンド実行後のカウンタ更新
        if st == feature.Feature.RESP_SUCCESS and limit_st == Limiter.CHECK_ALLOW:
            try:
            # コマンド実行後のカウンタ更新
                _apprun_post(self, stime, msg, Path(args.client_data), logger, args, limit)
            except Exception as e:
                st = feature.Feature.RESP_ERROR
                msg = dict(error=f"Failed to update limiter counter: {e}")
                logger.error(msg)
        return st, msg, obj
    return wrapper

def _svrun_pre(self:'LimitedFeature', data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str], sessions:Dict[str, Dict[str, Any]]) -> Tuple[int, Dict[str, Any], Any, Dict[str, Any]]:
    """
    svrunの実行前に制限チェックを行います。

    Args:
        self (LimitedFeature): LimitedFeatureのインスタンス
        data_dir (Path): データディレクトリのパス
        logger (logging.Logger): ロガー
        redis_cli (redis_client.RedisClient): Redisクライアント
        msg (List[str]): svrunの引数
        sessions (Dict[str, Dict[str, Any]]): セッション情報

    Returns:
        Tuple[int, Dict[str, Any], Any, Dict[str, Any]]: ステータス、メッセージ、制限オブジェクト、コマンドオプション
    """
    command_options = self.svrun_parse_options(data_dir, logger, redis_cli, msg, sessions=sessions)
    limit = Limiter.getInstance(redis_cli, flush_interval=10, reload_interval=60)
    st, ret = limit.check(feat=self, data_dir=data_dir, logger=logger, command_options=command_options, scope='server')
    return st, ret, limit, command_options

def _svrun_post(self:'LimitedFeature', data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str], command_options:Dict[str, Any], limit:'Limiter', stime:float):
    """
    svrunの実行後に制限カウンタを更新します。

    Args:
        data_dir (Path): データディレクトリのパス
        logger (logging.Logger): ロガー
        redis_cli (redis_client.RedisClient): Redisクライアント
        msg (List[str]): svrunの引数
        command_options (Dict[str, Any]): コマンドのオプション
        limit (Limiter): 制限オブジェクト
        stime (float): コマンド実行開始時間
    """
    exec_time = common.perf_counter() - stime
    input_bytes = len(' '.join(msg))
    output_bytes = redis_cli.last_ressize if hasattr(redis_cli, 'last_ressize') and redis_cli.last_ressize is not None else 0
    resval = redis_cli.last_resval if hasattr(redis_cli, 'last_resval') and redis_cli.last_resval is not None else None
    process_bytes = self.svrun_process_bytes(data_dir, logger, command_options, resval)
    registrations = self.svrun_registrations(data_dir, logger, command_options, resval)
    limit.update(feat=self, data_dir=data_dir, logger=logger, command_options=command_options,
                    exec_time=exec_time, input_bytes=input_bytes, process_bytes=process_bytes,
                    output_bytes=output_bytes, registrations=registrations)
    redis_cli.last_ressize = None
    redis_cli.last_resval = None

def svrun_check_limit(func: Callable) -> Callable:
    """
    コマンドの実行制限を検証するデコレーター。
    LimitedFeature を継承したクラスのサーバー側コマンド実行関数に適用することで、コマンドの実行前に制限チェックを行い、実行後にカウンタを更新します。
    それ以外の関数に適用された場合は、単純に元の関数を実行します。

    Args:
        func (Callable): サーバー側コマンドの実行関数
    Returns:
        Callable: デコレーターでラップされた関数
    """
    #@functools.wraps(func)
    def wrapper(self:'LimitedFeature', data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str], sessions:Dict[str, Dict[str, Any]]) -> int:
        if isinstance(self, LimitedFeature):
            limit_st, ret, limit, command_options = _svrun_pre(self, data_dir, logger, redis_cli, msg, sessions)
            if limit_st == Limiter.CHECK_DENY:
                logger.warning(ret)
                redis_cli.rpush(msg[1], ret)
                st = self.RESP_WARN
            else:
                stime = common.perf_counter()
                st = common.exec_svrun_sync(functools.partial(func, self), data_dir, logger, redis_cli, msg, sessions)
                if st == self.RESP_SUCCESS and limit_st == Limiter.CHECK_ALLOW:
                    try:
                        _svrun_post(self, data_dir, logger, redis_cli, msg, command_options, limit, stime)
                    except Exception as e:
                        st = self.RESP_ERROR
                        ret = dict(error=f"Failed to update limiter counter: {e}")
                        redis_cli.rpush(msg[1], ret)
                        logger.error(ret)
        else:
            st = common.exec_svrun_sync(functools.partial(func, self), data_dir, logger, redis_cli, msg, sessions)
        return st
    return wrapper

def async_svrun_check_limit(func: Callable) -> Callable:
    """
    コマンドの実行制限を検証するデコレーター。
    LimitedFeature を継承したクラスのサーバー側コマンド実行関数に適用することで、コマンドの実行前に制限チェックを行い、実行後にカウンタを更新します。
    それ以外の関数に適用された場合は、単純に元の関数を実行します。

    Args:
        func (Callable): サーバー側コマンドの実行関数
    Returns:
        Callable: デコレーターでラップされた関数
    """
    #@functools.wraps(func)
    async def wrapper(self:'LimitedFeature', data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str], sessions:Dict[str, Dict[str, Any]]) -> int:
        if isinstance(self, LimitedFeature):
            limit_st, ret, limit, command_options = _svrun_pre(self, data_dir, logger, redis_cli, msg, sessions)
            if limit_st == Limiter.CHECK_DENY:
                logger.warning(ret)
                redis_cli.rpush(msg[1], ret)
                st = self.RESP_WARN
            else:
                stime = common.perf_counter()
                _func = functools.partial(func, self)
                st = await _func(data_dir, logger, redis_cli, msg, sessions)
                if st == self.RESP_SUCCESS and limit_st == Limiter.CHECK_ALLOW:
                    try:
                        _svrun_post(self, data_dir, logger, redis_cli, msg, command_options, limit, stime)
                    except Exception as e:
                        st = self.RESP_ERROR
                        ret = dict(error=f"Failed to update limiter counter: {e}")
                        redis_cli.rpush(msg[1], ret)
                        logger.error(ret)
        else:
            _func = functools.partial(func, self)
            st = await _func(data_dir, logger, redis_cli, msg, sessions)
        return st
    return wrapper

class LimitedFeature(feature.Feature):
    """
    コマンドの実行制限を検証する機能の基底クラス。
    """
    def svrun_parse_options(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient,
                            msg:List[str], sessions:Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        svrunに渡される引数を解析して、コマンドの実行制限チェックに必要な情報を取得します。
        デフォルトの実装では、Redis クライアントの接続情報とコマンドのモード・コマンド名のみを取得します。
        このメソッドを拡張して、コマンドの引数やセッション情報など、より詳細な情報を取得する処理を実装できます。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        Returns:
            Dict[str, Any]: 解析結果
        """
        ret = dict(
            host=redis_cli.host,
            port=redis_cli.port,
            password=redis_cli.password,
            svname=redis_cli.svname,
            mode=self.get_mode(),
            cmd=self.get_cmd(),
        )
        return ret

    def apprun_process_bytes(self, data_dir:Path, logger:logging.Logger, args:argparse.Namespace, msg:Dict[str, Any]) -> int:
        """
        apprunの実行結果として処理バイト数を取得します。
        デフォルトの実装では、0 を返します。
        このメソッドを拡張して、コマンドの引数やセッション情報などから処理バイト数を算出する処理を実装できます。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            args (argparse.Namespace): コマンドの引数
            msg (Dict[str, Any]): apprunの処理結果
        Returns:
            int: 処理バイト数
        """
        return 0

    def apprun_registrations(self, data_dir:Path, logger:logging.Logger, args:argparse.Namespace, msg:Dict[str, Any]) -> int:
        """
        apprunの実行結果として登録数（又は登録サイズ）を取得します。
        デフォルトの実装では、0 を返します。
        このメソッドを拡張して、コマンドの引数やセッション情報などから登録数を算出する処理を実装できます。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            args (argparse.Namespace): コマンドの引数
            msg (Dict[str, Any]): apprunの処理結果
        Returns:
            int: 登録数
        """
        return 0

    def svrun_process_bytes(self, data_dir:Path, logger:logging.Logger, opt:Dict[str, Any], msg:Union[Dict, str]) -> int:
        """
        svrunの実行結果として処理バイト数を取得します。
        デフォルトの実装では、0 を返します。
        このメソッドを拡張して、コマンドの引数やセッション情報などから処理バイト数を算出する処理を実装できます。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            opt (Dict[str, Any]): コマンドのオプション
            msg (Union[Dict, str]): svrunの処理結果
        Returns:
            int: 処理バイト数
        """
        return 0

    def svrun_registrations(self, data_dir:Path, logger:logging.Logger, opt:Dict[str, Any], msg:Union[Dict, str]) -> int:
        """
        svrunの実行結果として登録数（又は登録サイズ）を取得します。
        デフォルトの実装では、0 を返します。
        このメソッドを拡張して、コマンドの引数やセッション情報などから登録数を算出する処理を実装できます。

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging.Logger): ロガー
            opt (Dict[str, Any]): コマンドのオプション
            msg (Union[Dict, str]): svrunの処理結果
        Returns:
            int: 登録数
        """
        return 0

class Limiter:
    """
    コマンド実行に対する量的制限をチェックするクラス。

    cmdbox_limiter_save で保存した制限設定をロードし、
    コマンド実行前の制限チェックおよび実行後のカウンタ更新を行います。

    制限設定は data_dir/.limiter/limiter-{name}.json に保存されており、
    カウンタは data_dir/.limiter/counter-{name}.json に保存されます。
    """

    LIMITER_DIR = ".limiter"
    CONFIG_PREFIX = "limiter-"
    COUNTER_PREFIX = "counter-"

    # Redis キーの定数
    REDIS_CONFIG_HASH = "limiter:config"
    REDIS_COUNTER_HASH = "limiter:counter"
    REDIS_CONFIG_LOADED_KEY = "limiter:config:loaded"

    CHECK_ALLOW = 0 # 制限なしでコマンド実行を許可
    CHECK_DENY = 1  # 制限によりコマンド実行を拒否
    CHECK_NOT_APPLICABLE = 2  # 制限が適用されない場合

    @classmethod
    def getInstance(cls, redis_client: Optional[redis_client.RedisClient] = None, flush_interval: float = 60.0, reload_interval: float = 60.0) -> 'Limiter':
        """
        Limiter のインスタンスを取得します。

        Args:
            redis_client (Optional[redis_client.RedisClient]): Redis クライアント。
                None の場合はファイルのみを使用します（従来動作）。
            flush_interval (float): カウンタおよび設定キャッシュをファイルに書き込む間隔（秒）。
                Redis が有効な場合、カウンタはこの間隔でファイルに永続化されます。
                設定キャッシュはこの間隔で TTL が切れ、次回 load_configs() 時に
                ファイルから再ロードされます。デフォルトは 60 秒。
            reload_interval (float): 設定をRedisからではなくファイルから再ロードする間隔（秒）。
                Redis が有効な場合、load_configs() 呼び出し時に最終更新からこの間隔以上経過している場合は、
                ファイルから再ロードされます。デフォルトは 60 秒。
        Returns:
            Limiter: Limiter のインスタンス
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls(redis_client=redis_client, flush_interval=flush_interval, reload_interval=reload_interval)
        return cls._instance

    def __init__(self,
                 redis_client: Optional[redis_client.RedisClient] = None,
                 flush_interval: float = 60.0,
                 reload_interval: float = 60.0) -> None:
        """
        Limiter を初期化します。

        Args:
            redis_client (Optional[redis_client.RedisClient]): Redis クライアント。
                None の場合はファイルのみを使用します（従来動作）。
            flush_interval (float): カウンタおよび設定キャッシュをファイルに書き込む間隔（秒）。
                Redis が有効な場合、カウンタはこの間隔でファイルに永続化されます。
                設定キャッシュはこの間隔で TTL が切れ、次回 load_configs() 時に
                ファイルから再ロードされます。デフォルトは 60 秒。
            reload_interval (float): 設定をRedisからではなくファイルから再ロードする間隔（秒）。
                Redis が有効な場合、load_configs() 呼び出し時に最終更新からこの間隔以上経過している場合は、
                ファイルから再ロードされます。デフォルトは 60 秒。
        """
        self.redis_client = redis_client
        self._flush_interval = flush_interval
        self._reload_interval = reload_interval
        # カウンターの最終更新タイムスタンプを保持する辞書
        self._last_counter_flush: Dict[str, float] = {}
        # 設定の最終読込みタイムスタンプ
        self._last_config_loaded: float = 0.0

    # ------------------------------------------------------------------
    # 設定 / カウンタの入出力
    # ------------------------------------------------------------------

    def load_configs(self, data_dir: Path) -> List[Dict[str, Any]]:
        """
        data_dir 以下のすべての制限設定をロードします。

        Redis が有効な場合はまず Redis キャッシュを参照します。
        キャッシュが期限切れまたは未登録の場合はファイルから読み込み、
        ``reload_interval`` 秒間有効なキャッシュとして Redis に保存します。

        Args:
            data_dir (Path): データディレクトリ
        Returns:
            List[Dict[str, Any]]: 制限設定のリスト
        """
        if self.redis_client is not None:
            try:
                now = time.time()
                if now - self._last_config_loaded >= self._reload_interval:
                    configs = self._load_configs_from_file(data_dir)
                    configs = sorted(configs, key=lambda c: c.get('limiter_name', ''))
                    self._last_config_loaded = now
                    pipe = self.redis_client.pipeline()
                    pipe.delete(f"{self.redis_client.lmtname}_{self.REDIS_CONFIG_HASH}")
                    for cfg in configs:
                        name = cfg.get('limiter_name', '')
                        if name:
                            pipe.hset(f"{self.redis_client.lmtname}_{self.REDIS_CONFIG_HASH}", name, json.dumps(cfg))
                    pipe.execute()
                    return configs
                if self.redis_client.exists(f"{self.redis_client.lmtname}_{self.REDIS_CONFIG_LOADED_KEY}"):
                    raw = self.redis_client.hgetall(f"{self.redis_client.lmtname}_{self.REDIS_CONFIG_HASH}")
                    if raw:
                        configs: List[Dict[str, Any]] = []
                        for v in raw.values():
                            try:
                                text = v.decode('utf-8') if isinstance(v, bytes) else v
                                configs.append(json.loads(text))
                            except Exception:
                                pass
                        return sorted(configs, key=lambda c: c.get('limiter_name', ''))
            except Exception as e:
                pass

        configs = self._load_configs_from_file(data_dir)
        return configs

    def _load_configs_from_file(self, data_dir: Path) -> List[Dict[str, Any]]:
        """
        ファイルからすべての制限設定をロードします（内部用）。
        """
        limiter_dir = Path(data_dir) / self.LIMITER_DIR
        if not limiter_dir.exists():
            return []
        configs: List[Dict[str, Any]] = []
        for path in sorted(limiter_dir.glob(f"{self.CONFIG_PREFIX}*.json")):
            try:
                with path.open('r', encoding='utf-8') as f:
                    configs.append(json.load(f))
            except Exception:
                pass
        return configs

    def load_counter(self, data_dir: Path, limiter_name: str) -> Dict[str, Any]:
        """
        指定した制限設定のカウンタをロードします。

        Redis が有効な場合は Redis から取得します。
        Redis にデータがない場合はファイルから読み込みます。
        どちらにもデータがない場合は初期値を返します。

        Args:
            data_dir (Path): データディレクトリ
            limiter_name (str): 制限設定の識別名
        Returns:
            Dict[str, Any]: カウンタ
        """
        if self.redis_client is not None:
            try:
                raw = self.redis_client.hget(f"{self.redis_client.lmtname}_{self.REDIS_COUNTER_HASH}", limiter_name)
                if raw is not None:
                    text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                    return json.loads(text)
            except Exception:
                pass
        counter = self._load_counter_from_file(data_dir, limiter_name)
        self.save_counter(data_dir, limiter_name, counter)  # Redis にも保存しておく
        return counter

    def _load_counter_from_file(self, data_dir: Path, limiter_name: str) -> Dict[str, Any]:
        """
        ファイルからカウンタをロードします（内部用）。
        JSONL 形式のファイルから最終行のみを読み込みます。
        """
        counter_path = Path(data_dir) / self.LIMITER_DIR / f"{self.COUNTER_PREFIX}{limiter_name}.jsonl"
        if not counter_path.exists():
            return self._init_counter(limiter_name)
        try:
            last_line = None
            with counter_path.open('r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        last_line = stripped
            if last_line is None:
                return self._init_counter(limiter_name)
            return json.loads(last_line)
        except Exception:
            return self._init_counter(limiter_name)

    def save_counter(self, data_dir: Path, limiter_name: str, counter: Dict[str, Any]) -> None:
        """
        指定した制限設定のカウンタを保存します。

        Redis が有効な場合は Redis に即時書き込みし、
        ``flush_interval`` 秒以上経過した場合のみファイルにも書き込みます。
        Redis が無効な場合は常にファイルに書き込みます。

        Args:
            data_dir (Path): データディレクトリ
            limiter_name (str): 制限設定の識別名
            counter (Dict[str, Any]): 保存するカウンタ
        """
        if self.redis_client is not None:
            try:
                self.redis_client.hset(
                    f"{self.redis_client.lmtname}_{self.REDIS_COUNTER_HASH}", limiter_name, json.dumps(counter))
            except Exception:
                pass
            now = time.time()
            if now - self._last_counter_flush.get(limiter_name, 0.0) >= self._flush_interval:
                self._save_counter_to_file(data_dir, limiter_name, counter)
                self._last_counter_flush[limiter_name] = now
        else:
            self._save_counter_to_file(data_dir, limiter_name, counter)

    def _save_counter_to_file(self, data_dir: Path, limiter_name: str, counter: Dict[str, Any]) -> None:
        """
        カウンタを JSONL ファイルに追記します（内部用）。
        flush_interval ごとに 1 行追加します。
        """
        counter_path = Path(data_dir) / self.LIMITER_DIR / f"{self.COUNTER_PREFIX}{limiter_name}.jsonl"
        counter_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(counter, ensure_ascii=False)
        common.save_file(counter_path, lambda f: f.write(line + '\n'),
                         mode='a', encoding='utf-8', nolock=False)

    def _init_counter(self, limiter_name: str) -> Dict[str, Any]:
        """
        カウンタの初期値を返します。

        Args:
            limiter_name (str): 制限設定の識別名
        Returns:
            Dict[str, Any]: 初期カウンタ
        """
        return dict(
            limiter_name=limiter_name,
            total_count=0,
            total_time=0,
            total_input=0,
            total_process=0,
            total_output=0,
            total_registrations=0,
            last_refresh=datetime.now().isoformat(),
        )

    # ------------------------------------------------------------------
    # リフレッシュ判定
    # ------------------------------------------------------------------
    def needs_refresh(self, config: Dict[str, Any], counter: Dict[str, Any]) -> bool:
        """
        カウンタのリフレッシュが必要かどうかを判定します。

        ``refresh_datetime`` が指定されており、現在時刻がその日時以降で
        かつ前回リフレッシュ時刻よりも後の場合にリフレッシュが必要と判定します。

        ``refresh_interval`` が指定されており、前回リフレッシュからの経過秒数が
        指定値以上の場合にリフレッシュが必要と判定します。

        Args:
            config (Dict[str, Any]): 制限設定
            counter (Dict[str, Any]): 現在のカウンタ
        Returns:
            bool: リフレッシュが必要な場合は True
        """
        now = datetime.now()

        refresh_dt_str = config.get('refresh_datetime')
        if refresh_dt_str:
            try:
                refresh_dt = datetime.fromisoformat(refresh_dt_str)
                last_refresh = datetime.fromisoformat(
                    counter.get('last_refresh', '1970-01-01T00:00:00'))
                if now >= refresh_dt > last_refresh:
                    return True
            except (ValueError, TypeError):
                pass

        refresh_interval = config.get('refresh_interval')
        if refresh_interval is not None:
            try:
                last_refresh = datetime.fromisoformat(
                    counter.get('last_refresh', '1970-01-01T00:00:00'))
                elapsed = (now - last_refresh).total_seconds()
                if elapsed >= int(refresh_interval):
                    return True
            except (ValueError, TypeError):
                pass

        return False

    def reset_counter(self, limiter_name: str) -> Dict[str, Any]:
        """
        カウンタをリセットした新しいカウンタを返します。

        Args:
            limiter_name (str): 制限設定の識別名
        Returns:
            Dict[str, Any]: リセット後のカウンタ
        """
        counter = self._init_counter(limiter_name)
        return counter

    # ------------------------------------------------------------------
    # マッチング
    # ------------------------------------------------------------------
    def matches(self, config: Dict[str, Any],
                command_options: Dict[str, Any]) -> bool:
        """
        制限設定が現在のコマンドコンテキストに適合するかどうかを判定します。

        ``target_mode`` が指定されている場合、``command_options`` の ``mode`` と一致する場合にマッチします。
        ``target_cmd`` が指定されている場合、``command_options`` の ``cmd`` と一致する場合にマッチします。
        ``target_option`` に設定された各 key/val がすべて
        ``command_options`` と一致する場合にマッチします。
        いずれも未設定の場合はすべてのコマンドに適合します。

        Args:
            config (Dict[str, Any]): 制限設定
            command_options (Dict[str, Any]): 実行コマンドのオプション（例: {'mode': 'llm', 'cmd': 'chat'}）
        Returns:
            bool: 制限設定が適合する場合は True
        """
        target_mode = config.get('target_mode')
        if target_mode:
            mode_val = command_options.get('mode')
            if isinstance(mode_val, list):
                if str(target_mode) not in [str(m) for m in mode_val]:
                    return False
            else:
                if str(mode_val) != str(target_mode):
                    return False

        target_cmd = config.get('target_cmd')
        if target_cmd:
            if str(command_options.get('cmd', '')) != str(target_cmd):
                return False

        target_option = config.get('target_option')
        if target_option:
            # list[dict] 形式（multi=True で複数指定された場合）
            option_dicts: List[Dict[str, Any]] = (
                target_option if isinstance(target_option, list) else [target_option]
            )
            for opt_dict in option_dicts:
                if not isinstance(opt_dict, dict):
                    continue
                for key, val in opt_dict.items():
                    if str(command_options.get(key, '')) != str(val):
                        return False

        return True

    # ------------------------------------------------------------------
    # チェック / 更新
    # ------------------------------------------------------------------
    def check(self, *, feat:LimitedFeature, data_dir: Path, logger: logging.Logger,
              command_options: Dict[str, Any],
              scope: str = 'server') -> Tuple[int, Optional[str]]:
        """
        コマンド実行が量的制限に違反していないかをチェックします。

        マッチするすべての制限設定に対してチェックを行い、
        いずれか 1 つでも違反していた場合は ``(非0, メッセージ)`` を返します。
        すべての制限をパスした場合は ``(0, None)`` を返します。

        登録最大数のチェックには :meth:`get_current_registrations` を呼び出します。

        Args:
            feat (LimitedFeature): 制限対象の機能
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            command_options (Dict[str, Any]): 実行コマンドのオプション
            scope (str): 対象とする制限設定のスコープ。``'server'`` または ``'client'`` のみ有効。
        Returns:
            Tuple[int, Optional[str]]:
                許可する場合は ``Limiter.CHECK_ALLOW``、制限違反の場合は ``Limiter.CHECK_DENY`` 、制限が適用されない場合は ``Limiter.CHECK_NOT_APPLICABLE`` を返します。
        Raises:
            ValueError: ``scope`` が ``'server'`` でも ``'client'`` でもない場合。
        """
        if scope not in ('server', 'client'):
            raise ValueError(f"Limiter.check: invalid scope '{scope}'. Must be 'server' or 'client'.")

        configs = self.load_configs(data_dir)
        now = datetime.now()

        checkfg = self.CHECK_NOT_APPLICABLE
        for config in configs:
            if config.get('scope') != scope:
                continue
            limiter_name = config.get('limiter_name')
            if not limiter_name:
                continue
            if not self.matches(config, command_options):
                continue

            counter = self.load_counter(data_dir, limiter_name)
            if self.needs_refresh(config, counter):
                self.save_counter(data_dir, limiter_name, counter)
                counter = self.reset_counter(limiter_name)

            # 実行可能期間チェック
            period_start = config.get('exec_period_start')
            if period_start:
                try:
                    if now < datetime.fromisoformat(period_start):
                        return self.CHECK_DENY, dict(warn=
                            f"Limiter '{limiter_name}': command is not yet within the "
                            f"executable period (starts: {period_start})."
                        )
                except (ValueError, TypeError):
                    logger.warning(f"Limiter '{limiter_name}': invalid exec_period_start value: {period_start}")

            period_end = config.get('exec_period_end')
            if period_end:
                try:
                    if now > datetime.fromisoformat(period_end):
                        return self.CHECK_DENY, dict(warn=
                            f"Limiter '{limiter_name}': the executable period has expired "
                            f"(ended: {period_end})."
                        )
                except (ValueError, TypeError):
                    logger.warning(f"Limiter '{limiter_name}': invalid exec_period_end value: {period_end}")

            # 登録（又は登録最大サイズ）最大数チェック
            max_registrations = config.get('max_registrations')
            if max_registrations is not None:
                if counter.get('total_registrations', 0) >= int(max_registrations):
                    return self.CHECK_DENY, dict(warn=
                        f"Limiter '{limiter_name}': maximum number of registrations "
                        f"({max_registrations}) has been reached."
                    )

            # 実行最大回数チェック
            max_total_count = config.get('max_total_count')
            if max_total_count is not None:
                if counter.get('total_count', 0) >= int(max_total_count):
                    return self.CHECK_DENY, dict(warn=
                        f"Limiter '{limiter_name}': maximum execution count "
                        f"({max_total_count}) has been reached."
                    )

            # 実行可能総時間チェック
            max_total_time = config.get('max_total_time')
            if max_total_time is not None:
                if counter.get('total_time', 0) >= int(max_total_time):
                    return self.CHECK_DENY, dict(warn=
                        f"Limiter '{limiter_name}': maximum total execution time "
                        f"({max_total_time}s) has been reached."
                    )

            # 入力総バイト数チェック
            max_total_input = config.get('max_total_input')
            if max_total_input is not None:
                if counter.get('total_input', 0) >= int(max_total_input):
                    return self.CHECK_DENY, dict(warn=
                        f"Limiter '{limiter_name}': maximum total input bytes "
                        f"({max_total_input}) has been reached."
                    )

            # 処理総バイト数チェック
            max_total_process = config.get('max_total_process')
            if max_total_process is not None:
                if counter.get('total_process', 0) >= int(max_total_process):
                    return self.CHECK_DENY, dict(warn=
                        f"Limiter '{limiter_name}': maximum total process bytes "
                        f"({max_total_process}) has been reached."
                    )

            # 出力総バイト数チェック
            max_total_output = config.get('max_total_output')
            if max_total_output is not None:
                if counter.get('total_output', 0) >= int(max_total_output):
                    return self.CHECK_DENY, dict(warn=
                        f"Limiter '{limiter_name}': maximum total output bytes "
                        f"({max_total_output}) has been reached."
                    )
                
            checkfg = self.CHECK_ALLOW

        return checkfg, None

    def update(self, *, feat:LimitedFeature, data_dir: Path, logger: logging.Logger,
               command_options: Dict[str, Any],
               exec_time: float = 0.0,
               input_bytes: int = 0,
               process_bytes: int = 0,
               output_bytes: int = 0,
               registrations: int = 0) -> None:
        """
        コマンド実行後にカウンタを更新します。

        マッチするすべての制限設定のカウンタに対して、
        実行回数・実行時間・入出力バイト数を加算して保存します。

        Args:
            feat (LimitedFeature): 対象の機能
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            command_options (Dict[str, Any]): 実行コマンドのオプション
            exec_time (float): 実行時間（秒）
            input_bytes (int): 入力バイト数
            process_bytes (int): 処理バイト数
            output_bytes (int): 出力バイト数
            registrations (int): 登録数（又は登録サイズ）
        """
        configs = self.load_configs(data_dir)

        for config in configs:
            limiter_name = config.get('limiter_name')
            if not limiter_name:
                continue
            if not self.matches(config, command_options):
                continue

            try:
                counter = self.load_counter(data_dir, limiter_name)
                if self.needs_refresh(config, counter):
                    counter = self.reset_counter(limiter_name)

                counter['total_count'] = counter.get('total_count', 0) + 1
                counter['total_time'] = counter.get('total_time', 0) + round(exec_time)
                counter['total_input'] = counter.get('total_input', 0) + input_bytes
                counter['total_process'] = counter.get('total_process', 0) + process_bytes
                counter['total_output'] = counter.get('total_output', 0) + output_bytes
                counter['total_registrations'] = registrations
                self.save_counter(data_dir, limiter_name, counter)
            except Exception as e:
                logger.warning(f"Limiter.update failed for '{limiter_name}': {e}", exc_info=True)
