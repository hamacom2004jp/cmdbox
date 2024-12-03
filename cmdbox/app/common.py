from cmdbox import version
from cmdbox.app import feature
from pathlib import Path
from PIL import Image, ImageDraw
from pkg_resources import resource_string
from tabulate import tabulate
from typing import List, Tuple, Dict, Any
import datetime
import logging
import logging.config
import json
import numpy as np
import os
import random
import shutil
import string
import re
import requests
import subprocess
import tempfile
import time
import yaml


HOME_DIR = Path(os.path.expanduser("~"))
def copy_sample(data:Path, ver=version):
    """
    サンプルデータをコピーします。

    Args:
        data (Path): データディレクトリ
        ver (version, optional): バージョン. Defaults to version
    """
    dst = Path(data) / '.samples' if data is not None else HOME_DIR / '.samples'
    if dst.exists():
        return
    src = Path(ver.__file__).parent / 'extensions'
    shutil.copytree(src, dst, dirs_exist_ok=True)

def mklogdir(data:Path) -> Path:
    """
    ログディレクトリを作成します。

    Args:
        logdir (Path, optional): ログディレクトリのパス. Defaults to Path.cwd()/'log'.

    Returns:
        作成したログディレ作成したログディレクトリのパス
    """
    logdir = Path(data) / '.logs' if data is not None else HOME_DIR / '.logs'
    if not logdir.exists():
        return mkdirs(logdir)
    return logdir

def load_yml(yml_path:Path) -> dict:
    """
    YAMLファイルを読み込みます。

    Args:
        yml_path (Path): YAMLファイルのパス

    Returns:
        dict: 読み込んだYAMLファイルの内容
    """
    with open(yml_path) as f:
        return yaml.safe_load(f)

def load_config(mode:str, debug:bool=False, data=HOME_DIR, webcall:bool=False, appid:str=version.__appid__) -> Tuple[logging.Logger, dict]:
    """
    指定されたモードのロガーと設定を読み込みます。

    Args:
        mode (str): モード名
        debug (bool, optional): デバッグモード. Defaults to False
        data (Path, optional): データディレクトリ. Defaults to HOME_DIR.
        webcall (bool, optional): WebAPIからの呼出しの場合はTrue. setHandlerを削除します。. Defaults to False.
        appid (str, optional): アプリケーションID. Defaults to version.__appid__.

    Returns:
        logger (logging.Logger): ロガー
        config (dict): 設定
    """
    data = Path(data) if data is not None else HOME_DIR
    log_config = yaml.safe_load(resource_string(appid, f"logconf_{mode}.yml"))
    std_key = None
    for k, h in log_config['handlers'].items():
        if 'filename' in h:
            h['filename'] = data / h['filename']
            mkdirs(h['filename'].parent)
        if 'class' in h and h['class'] == 'logging.StreamHandler':
            std_key = k
    if webcall and std_key is not None:
        for k, l in log_config['loggers'].items():
            if 'handlers' in l and std_key in l['handlers']:
                l['handlers'].remove(std_key)
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(mode)
    set_debug(logger, debug)
    config = yaml.safe_load(resource_string(version.__appid__, "config.yml"))
    return logger, config

def set_debug(logger:logging.Logger, debug:bool=False) -> None:
    """
    ロガーのデバッグモードを設定します。

    Args:
        logger (logging.Logger): ロガー
        debug (bool, optional): デバッグモード. Defaults to False.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.info("Use debug mode logging.")
    else:
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            handler.setLevel(logging.INFO)

def default_json_enc(o) -> Any:
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.float32):
        return float(o)
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, np.int32):
        return int(o)
    if isinstance(o, np.intc):
        return int(o)
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, tempfile._TemporaryFileWrapper):
        return str(o)
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%dT%H:%M:%S')
    if isinstance(o, feature.Feature):
        return 'object'
    raise TypeError(f"Type {type(o)} not serializable")

def saveopt(opt:dict, opt_path:Path) -> None:
    """
    コマンドラインオプションをJSON形式でファイルに保存します。

    Args:
        opt (dict): コマンドラインオプション
        opt_path (Path): 保存先のファイルパス
    """
    if opt_path is None:
        return
    with open(opt_path, 'w') as f:
        json.dump(opt, f, indent=4, default=default_json_enc)

def loadopt(opt_path:str) -> dict:
    """
    JSON形式のファイルからコマンドラインオプションを読み込みます。

    Args:
        opt_path (str): 読み込むファイルパス

    Returns:
        dict: 読み込んだコマンドラインオプション
    """
    if opt_path is None or not Path(opt_path).exists():
        return dict()
    with open(opt_path) as f:
        opt = json.load(f)
        return opt

def getopt(opt:dict, key:str, preval=None, defval=None, withset=False) -> any:
    """
    コマンドラインオプションから指定されたキーの値を取得します。

    Args:
        opt (dict): 読み込んだコマンドラインオプション
        key (str): キー
        preval (Any, optional): 引数で指定されたコマンドラインオプション. Defaults to None.
        defval (Any, optional): デフォルト値. Defaults to None.
        withset (bool, optional): optに引数のコマンドラインオプションを設定するかどうか. Defaults to False.

    Returns:
        Any: 取得した値
    """
    if preval is not None:
        v = preval
        if isinstance(preval, dict):
            v = preval.get(key, None)
        if (v is None or not v) and key in opt:
            v = opt[key]
        elif (v is None or not v) and v != 0:
            v = defval
        if withset:
            opt[key] = v
        return v
    if key in opt:
        return opt[key]
    else:
        if withset:
            opt[key] = defval
        return defval

def safe_fname(fname:str) -> str:
    """
    ファイル名に使えない文字を置換します。

    Args:
        fname (str): ファイル名

    Returns:
        str: 置換後のファイル名
    """
    return re.sub('[\s:;\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]', '_',str(fname))

def check_fname(fname:str) -> bool:
    """
    ファイル名に使えない文字が含まれているかどうかをチェックします。

    Args:
        fname (str): ファイル名

    Returns:
        bool: Trueの場合は使えない文字が含まれている
    """
    return re.search('[\s:\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]',str(fname)) is not None

def mkdirs(dir_path:Path):
    """
    ディレクトリを中間パスも含めて作成します。

    Args:
        dir_path (Path): 作成するディレクトリのパス

    Returns:
        Path: 作成したディレクトリのパス
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def rmdirs(dir_path:Path, ignore_errors:bool=True):
    """
    ディレクトリをサブディレクトリ含めて削除します。

    Args:
        dir_path (Path): 削除するディレクトリのパス
    """
    shutil.rmtree(dir_path, ignore_errors=ignore_errors)

def random_string(size:int=16):
    """
    ランダムな文字列を生成します。

    Args:
        size (int, optional): 文字列の長さ. Defaults to 16.

    Returns:
        str: 生成された文字列
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

def print_format(data:dict, format:bool, tm:float, output_json:str=None, output_json_append:bool=False, stdout:bool=True, tablefmt:str='github'):
    """
    データを指定されたフォーマットで出力します。

    Args:
        data (dict): 出力するデータ
        format (bool): フォーマットするかどうか
        tm (float): 処理時間
        output_json (str, optional): JSON形式で出力するファイルパス. Defaults to None.
        output_json_append (bool, optional): JSON形式で出力するファイルパス. Defaults to False.
        stdout (bool, optional): 標準出力に出力するかどうか. Defaults to True.
        tablefmt (str, optional): テーブルのフォーマット. Defaults to 'github'.
    Returns:
        str: 生成された文字列
    """
    txt = ''
    if format:
        if 'success' in data:
            data = data['success']['data'] if 'data' in data['success'] else data['success']
            if type(data) == list:
                txt = tabulate(data, headers='keys', tablefmt=tablefmt)
            elif type(data) == dict:
                txt = tabulate([data], headers='keys', tablefmt=tablefmt)
            else:
                txt = str(data)
        elif type(data) == list:
            txt = tabulate(data, headers='keys', tablefmt=tablefmt)
        else:
            txt = tabulate([data], headers='keys', tablefmt=tablefmt)
        if stdout:
            try:
                print(txt)
                print(f"{time.perf_counter() - tm:.03f}s.")
            except BrokenPipeError:
                pass
    else:
        if 'success' in data and type(data['success']) == dict:
            if "performance" not in data["success"]:
                data["success"]["performance"] = []
            performance = data["success"]["performance"]
            performance.append(dict(key="app_proc", val=f"{time.perf_counter() - tm:.03f}s"))
        try:
            if type(data) == dict:
                txt = json.dumps(data, default=default_json_enc, ensure_ascii=False)
            else:
                txt = data
        except:
            txt = data
        if stdout:
            try:
                print(txt)
            except BrokenPipeError:
                pass
    if output_json is not None:
        try:
            with open(output_json, 'a' if output_json_append else 'w', encoding='utf-8') as f:
                json.dump(data, f, default=default_json_enc, ensure_ascii=False)
                print('', file=f)
        except Exception as e:
            pass
    return txt

def to_str(o, slise=-1):
    ret = ""
    if type(o) == dict:
        ret = json.dumps(o, default=default_json_enc)
    elif type(o) == list and len(o) > 0 and type(o[0]) == dict:
        ret = json.dumps(o, default=default_json_enc)
    else:
        ret = str(o)
    if slise < 0:
        return ret
    ret = ret[0:slise]
    return len(ret) > 100 and ret + '...' or ret

def download_file(url:str, save_path:Path) -> Path:
    """
    ファイルをダウンロードします。

    Args:
        url (str): ダウンロードするファイルのURL
        save_path (Path): 保存先のファイルパス

    Returns:
        Path: 保存したファイルのパス
    """
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(r.content)
    return save_path

def cmd(cmd:str, logger:logging.Logger, slise:int=100, newenv:Dict=None):
    """
    コマンドを実行します。

    Args:
        cmd (str): 実行するコマンド
        logger (logging.Logger): ロガー
        slise (int, optional): 出力文字列の最大長. Defaults to 100
        newenv (dict): 上書きしたい環境変数

    Returns:
        Tuple[int, str]: コマンドの戻り値と出力
    """
    if logger.level == logging.DEBUG:
        logger.debug(f"common.cmd:{cmd}")
    env = os.environ.copy()
    if newenv is not None:
        for k, v in newenv.items():
            env[k] = v
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    output = None
    while proc.returncode is None:
        out = proc.stdout.readline()
        if out == b'' and proc.poll() is not None:
            break
        for enc in ['utf-8', 'cp932', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                output = out.decode(enc).rstrip()
                #if platform.system() == 'Windows' or strip:
                #    output = output.rstrip()
                if logger.level == logging.DEBUG:
                    output_str = to_str(output, slise=slise)
                    logger.debug(f"common.cmd:output={output_str}")
                break
            except UnicodeDecodeError:
                pass

    return proc.returncode, output, cmd

def draw_boxes(image:Image.Image, boxes:List[List[float]], scores:List[float], classes:List[int], ids:List[str]=None,
               labels:List[str]=None, colors:List[Tuple[int]]=None, tracks:List[int]=None,
               nodraw:bool=False, nolookup:bool=False) -> Tuple[Image.Image, List[str]]:
    """
    画像にバウンディングボックスを描画します。

    Args:
        image (Image.Image): 描画する画像
        boxes (List[List[float]]): バウンディングボックスの座標リスト
        scores (List[float]): 各バウンディングボックスのスコアリスト
        classes (List[int]): 各バウンディングボックスのクラスリスト
        ids (List[str]): 各バウンディングボックスのIDリスト
        labels (List[str], optional): クラスのラベルリスト. Defaults to None.
        colors (List[Tuple[int]], optional): クラスごとの色のリスト. Defaults to None.
        tracks (List[int], optional): トラックIDリスト. Defaults to None.
        nodraw (bool, optional): 描画しない場合はTrue. Defaults to False.
        nolookup (bool, optional): ラベル及び色をクラスIDから取得しない場合はTrue. Defaults to False.

    Returns:
        Image: バウンディングボックスが描画された画像
        List[str]: 各バウンディングボックスのラベルリスト
    """
    draw = ImageDraw.Draw(image)
    ids = ids if ids is not None else [None] * len(boxes)
    tracks = tracks if tracks is not None else [None] * len(boxes)
    output_labels = []
    for i, (box, score, cl, id, trc) in enumerate(zip(boxes, scores, classes, ids, tracks)):
        y1, x1, y2, x2 = box
        x1 = max(0, np.floor(x1 + 0.5).astype(int))
        y1 = max(0, np.floor(y1 + 0.5).astype(int))
        x2 = min(image.width, np.floor(x2 + 0.5).astype(int))
        y2 = min(image.height, np.floor(y2 + 0.5).astype(int))
        if not nolookup:
            color = colors[int(cl)] if colors is not None and len(colors) > cl else make_color(str(int(cl)))
            label = str(labels[int(cl)]) if labels is not None else str(id) if id is not None else None
        else:
            color = colors[i] if colors is not None and len(colors) > i else make_color(str(int(cl)))
            label = str(labels[i]) if labels is not None and len(labels) > i else None
        if not nodraw:
            if x2 - x1 > 0 and y2 - y1 > 0:
                draw.rectangle(((x1, y1), (x2, y2)), outline=color)
                if label is not None:
                    draw.rectangle(((x1, y1), (x2, y1+10)), outline=color, fill=color)
                    draw.text((x1, y1), f"{label}:{score}", tuple([int(255-c) for c in color]))
        output_labels.append(label)

    return image, output_labels

def make_color(idstr:str) -> Tuple[int]:
    if len(idstr) < 3:
        idstr = idstr.zfill(3)
    return tuple([ord(c) * ord(c) % 256 for c in idstr[:3]])
