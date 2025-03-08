from cmdbox.app import common, feature
from cmdbox.app.commons import module
from fastapi.routing import APIRoute
from pathlib import Path
from starlette.routing import Route
from typing import List, Dict, Any 
import locale
import logging
import re


class Options:
    T_INT = 'int'
    T_FLOAT = 'float'
    T_BOOL = 'bool'
    T_STR = 'str'
    T_DICT = 'dict'
    T_TEXT = 'text'
    T_FILE = 'file'
    T_DIR = 'dir'
    
    def __setattr__(self, name:str, value):
        if name.startswith("T_") and name in self.__dict__:
            raise ValueError(f'Cannot set attribute. ({name})')
        self.__dict__[name] = value

    _instance = None

    @staticmethod
    def getInstance(appcls=None, ver=None):
        if Options._instance is None:
            Options._instance = Options(appcls=appcls, ver=ver)
        return Options._instance

    def __init__(self, appcls=None, ver=None):
        self.appcls = appcls
        self.ver = ver
        self.features_yml_data = None
        self.features_loaded = dict()
        self.aliases_loaded_cli = False
        self.aliases_loaded_web = False
        self.init_options()

    def get_mode_keys(self) -> List[str]:
        return [key for key,val in self._options["mode"].items() if type(val) == dict]

    def get_modes(self) -> List[Dict[str, str]]:
        """
        起動モードの選択肢を取得します。
        Returns:
            List[Dict[str, str]]: 起動モードの選択肢
        """
        return [''] + [{key:val} for key,val in self._options["mode"].items() if type(val) == dict]

    def get_cmd_keys(self, mode:str) -> List[str]:
        if mode not in self._options["cmd"]:
            return []
        return [key for key,val in self._options["cmd"][mode].items() if type(val) == dict]

    def get_cmds(self, mode:str) -> List[Dict[str, str]]:
        """
        コマンドの選択肢を取得します。
        Args:
            mode: 起動モード
        Returns:
            List[Dict[str, str]]: コマンドの選択肢
        """
        if mode not in self._options["cmd"]:
            return ['Please select mode.']
        ret = [{key:val} for key,val in self._options["cmd"][mode].items() if type(val) == dict]
        if len(ret) > 0:
            return [''] + ret
        return ['Please select mode.']

    def get_cmd_attr(self, mode:str, cmd:str, attr:str) -> Any:
        """
        コマンドの属性を取得します。
        Args:
            mode: 起動モード
            cmd: コマンド
            attr: 属性
        Returns:
            Any: 属性の値
        """
        if mode not in self._options["cmd"]:
            return [f'Unknown mode. ({mode})']
        if cmd is None or cmd == "" or cmd not in self._options["cmd"][mode]:
            return []
        if attr not in self._options["cmd"][mode][cmd]:
            return None
        return self._options["cmd"][mode][cmd][attr]
    
    def get_svcmd_feature(self, svcmd:str) -> Any:
        """
        サーバー側のコマンドのフューチャーを取得します。

        Args:
            svcmd: サーバー側のコマンド
        Returns:
            feature.Feature: フューチャー
        """
        if svcmd is None or svcmd == "":
            return None
        if svcmd not in self._options["svcmd"]:
            return None
        return self._options["svcmd"][svcmd]

    def get_cmd_choices(self, mode:str, cmd:str, webmode:bool=False) -> List[Dict[str, Any]]:
        """
        コマンドのオプション一覧を取得します。
        Args:
            mode: 起動モード
            cmd: コマンド
            webmode (bool, optional): Webモードからの呼び出し. Defaults to False
        Returns:
            List[Dict[str, Any]]: オプションの選択肢
        """
        opts = self.get_cmd_attr(mode, cmd, "choice")
        ret = []
        for o in opts:
            if not webmode or type(o) is not dict:
                ret.append(o)
                continue
            o = o.copy()
            if 'web' in o and o['web'] == 'mask':
                o['default'] = '********'
            ret.append(o)
        return ret

    def get_cmd_opt(self, mode:str, cmd:str, opt:str, webmode:bool=False) -> Dict[str, Any]:
        """
        コマンドのオプションを取得します。
        Args:
            mode: 起動モード
            cmd: コマンド
            opt: オプション
            webmode (bool, optional): Webモードからの呼び出し. Defaults to False
        Returns:
            Dict[str, Any]: オプションの値
        """
        opts = self.get_cmd_choices(mode, cmd, webmode)
        for o in opts:
            if 'opt' in o and o['opt'] == opt:
                return o
        return None

    def list_options(self):
        def _list(ret, key, val):
            if type(val) != dict or 'type' not in val:
                return
            opt = dict()
            if val['type'] == Options.T_INT:
                opt['type'] = int
                opt['action'] = 'append' if val['multi'] else None
            elif val['type'] == Options.T_FLOAT:
                opt['type'] = float
                opt['action'] = 'append' if val['multi'] else None
            elif val['type'] == Options.T_BOOL:
                opt['type'] = bool
                opt['action'] = 'store_true'
            elif val['type'] == Options.T_DICT:
                opt['type'] = dict
                if not val['multi']:
                    raise ValueError(f'list_options: The multi must be True if type is dict. key={key}, val={val}')
                opt['action'] = 'append'
            else:
                opt['type'] = str
                opt['action'] = 'append' if val['multi'] else None
            o = [f'-{val["short"]}'] if "short" in val else []
            o += [f'--{key}']
            language, _ = locale.getlocale()
            opt['help'] = val['discription_en'] if language.find('Japan') < 0 and language.find('ja_JP') < 0 else val['discription_ja']
            opt['default'] = val['default']
            if val['multi'] and val['default'] is not None:
                raise ValueError(f'list_options: The default value must be None if multi is True. key={key}, val={val}')
            opt['opts'] = o
            if val['choice'] is not None:
                opt['choices'] = []
                for c in val['choice']:
                    if type(c) == dict:
                        opt['choices'] += [c['opt']]
                    elif c is not None and c != "":
                        opt['choices'] += [c]
            else:
                opt['choices'] = None
            ret[key] = opt
        ret = dict()
        for k, v in self._options.items():
            _list(ret, k, v)
        #for mode in self._options["mode"]['choice']:
        for _, cmd in self._options["cmd"].items():
            if type(cmd) is not dict:
                continue
            for _, opt in cmd.items():
                if type(opt) is not dict:
                    continue
                for o in opt["choice"]:
                    if type(o) is not dict:
                        continue
                    _list(ret, o['opt'], o)
        return ret

    def mk_opt_list(self, opt:dict, webmode:bool=False) -> List[str]:
        opt_schema = self.get_cmd_choices(opt['mode'], opt['cmd'], webmode)
        opt_list = ['-m', opt['mode'], '-c', opt['cmd']]
        file_dict = dict()
        for key, val in opt.items():
            if key in ['stdout_log', 'capture_stdout']:
                continue
            schema = [schema for schema in opt_schema if type(schema) is dict and schema['opt'] == key]
            if len(schema) == 0 or val == '':
                continue
            if schema[0]['type'] == Options.T_BOOL:
                if val:
                    opt_list.append(f"--{key}")
                continue
            if type(val) == list:
                for v in val:
                    if v is None or v == '':
                        continue
                    opt_list.append(f"--{key}")
                    if str(v).find(' ') >= 0:
                        opt_list.append(f'"{v}"')
                    else:
                        opt_list.append(str(v))
            elif type(val) == dict:
                for k,v in val.items():
                    if k is None or k == '' or v is None or v == '':
                        continue
                    opt_list.append(f"--{key}")
                    k = f'"{k}"' if str(k).find(' ') >= 0 else str(k)
                    v = f'"{v}"' if str(v).find(' ') >= 0 else str(v)
                    opt_list.append(f'{k}={v}')
            elif val is not None and val != '':
                opt_list.append(f"--{key}")
                if str(val).find(' ') >= 0:
                    opt_list.append(f'"{val}"')
                else:
                    opt_list.append(str(val))
            if 'fileio' in schema[0] and schema[0]['fileio'] == 'in' and type(val) != str:
                file_dict[key] = val
        return opt_list, file_dict

    def init_options(self):
        self._options = dict()
        self._options["version"] = dict(
            short="v", type=Options.T_BOOL, default=None, required=False, multi=False, hide=True, choice=None,
            discription_ja="バージョン表示",
            discription_en="Display version")
        self._options["useopt"] = dict(
            short="u", type=Options.T_STR, default=None, required=False, multi=False, hide=True, choice=None,
            discription_ja="オプションを保存しているファイルを使用します。",
            discription_en="Use the file that saves the options.")
        self._options["saveopt"] = dict(
            short="s", type=Options.T_BOOL, default=None, required=False, multi=False, hide=True, choice=[True, False],
            discription_ja="指定しているオプションを `-u` で指定したファイルに保存します。",
            discription_en="Save the specified options to the file specified by `-u`.")
        self._options["debug"] = dict(
            short="d", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
            discription_ja="デバックモードで起動します。",
            discription_en="Starts in debug mode.")
        self._options["format"] = dict(
            short="f", type=Options.T_BOOL, default=None, required=False, multi=False, hide=True,
            discription_ja="処理結果を見やすい形式で出力します。指定しない場合json形式で出力します。",
            discription_en="Output the processing result in an easy-to-read format. If not specified, output in json format.",
            choice=None)
        self._options["mode"] = dict(
            short="m", type=Options.T_STR, default=None, required=True, multi=False, hide=True,
            discription_ja="起動モードを指定します。",
            discription_en="Specify the startup mode.",
            choice=[])
        self._options["cmd"] = dict(
            short="c", type=Options.T_STR, default=None, required=True, multi=False, hide=True,
            discription_ja="コマンドを指定します。",
            discription_en="Specify the command.",
            choice=[])
        self._options["output_json"] = dict(
            short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
            discription_ja="処理結果jsonの保存先ファイルを指定。",
            discription_en="Specify the destination file for saving the processing result json.")
        self._options["output_json_append"] = dict(
            short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
            discription_ja="処理結果jsonファイルを追記保存します。",
            discription_en="Save the processing result json file by appending.")

    def init_debugoption(self):
        # デバックオプションを追加
        self._options["debug"]["opt"] = "debug"
        for key, mode in self._options["cmd"].items():
            if type(mode) is not dict:
                continue
            mode['opt'] = key
            for k, c in mode.items():
                if type(c) is not dict:
                    continue
                c["opt"] = k
                if "debug" not in [_o['opt'] for _o in c["choice"]]:
                    c["choice"].append(self._options["debug"])
                if c["opt"] not in [_o['opt'] for _o in self._options["cmd"]["choice"]]:
                    self._options["cmd"]["choice"] += [c]
            self._options["mode"][key] = mode
            self._options["mode"]["choice"] += [mode]

    def load_svcmd(self, package_name:str, prefix:str="cmdbox_", excludes:list=[], appcls=None, ver=None, logger:logging.Logger=None, isloaded:bool=True):
        """
        指定されたパッケージの指定された接頭語を持つモジュールを読み込みます。

        Args:
            package_name (str): パッケージ名
            prefix (str): 接頭語
            excludes (list): 除外するモジュール名のリスト
            appcls (Any): アプリケーションクラス
            ver (Any): バージョンモジュール
            logger (logging.Logger): ロガー
            isloaded (bool): 読み込み済みかどうか
        """
        if "svcmd" not in self._options:
            self._options["svcmd"] = dict()
        for mode, f in module.load_features(package_name, prefix, excludes, appcls=appcls, ver=ver).items():
            if mode not in self._options["cmd"]:
                self._options["cmd"][mode] = dict()
            for cmd, opt in f.items():
                self._options["cmd"][mode][cmd] = opt
                fobj:feature.Feature = opt['feature']
                if not isloaded and logger is not None and logger.level == logging.DEBUG:
                    logger.debug(f"loaded features: mode={mode}, cmd={cmd}, {fobj}")
                svcmd = fobj.get_svcmd()
                if svcmd is not None:
                    self._options["svcmd"][svcmd] = fobj
        self.init_debugoption()
    
    def is_features_loaded(self, ftype:str) -> bool:
        """
        指定されたフィーチャータイプが読み込まれているかどうかを返します。

        Args:
            ftype (str): フィーチャータイプ
        Returns:
            bool: 読み込まれているかどうか
        """
        return ftype in self.features_loaded and self.features_loaded[ftype]

    def load_features_file(self, ftype:str, func, appcls, ver, logger:logging.Logger=None):
        """
        フィーチャーファイル（features.yml）を読み込みます。

        Args:
            ftype (str): フィーチャータイプ。cli又はweb
            func (Any): フィーチャーの処理関数
            appcls (Any): アプリケーションクラス
            ver (Any): バージョンモジュール
            logger (logging.Logger): ロガー
        """
        # 読込み済みかどうかの判定
        if self.is_features_loaded(ftype):
            return
        # cmdboxを拡張したアプリをカスタマイズするときのfeatures.ymlを読み込む
        features_yml = Path('features.yml')
        if not features_yml.exists() or not features_yml.is_file():
            # cmdboxを拡張したアプリの組み込みfeatures.ymlを読み込む
            features_yml = Path(ver.__file__).parent / 'extensions' / 'features.yml'
        #if not features_yml.exists() or not features_yml.is_file():
        #    features_yml = Path('.samples/features.yml')
        if logger is not None and logger.level == logging.DEBUG:
            logger.debug(f"load features.yml: {features_yml}, is_file={features_yml.is_file()}")
        if features_yml.exists() and features_yml.is_file():
            if self.features_yml_data is None:
                self.features_yml_data = yml = common.load_yml(features_yml)
            else:
                yml = self.features_yml_data
            if yml is None: return
            if 'features' not in yml:
                raise Exception('features.yml is invalid. (The root element must be "features".)')
            if ftype not in yml['features']:
                raise Exception(f'features.yml is invalid. (There is no “{ftype}” in the “features” element.)')
            if yml['features'][ftype] is None:
                return
            if type(yml['features'][ftype]) is not list:
                raise Exception(f'features.yml is invalid. (The “features.{ftype} element must be a list. {ftype}={yml["features"][ftype]})')
            for data in yml['features'][ftype]:
                if type(data) is not dict:
                    raise Exception(f'features.yml is invalid. (The “features.{ftype}” element must be a list element must be a dictionary. data={data})')
                if 'package' not in data:
                    raise Exception(f'features.yml is invalid. (The “package” element must be in the dictionary of the list element of the “features.{ftype}” element. data={data})')
                if 'prefix' not in data:
                    raise Exception(f'features.yml is invalid. (The prefix element must be in the dictionary of the list element of the “features.{ftype}” element. data={data})')
                if data['package'] is None or data['package'] == "":
                    continue
                if data['prefix'] is None or data['prefix'] == "":
                    continue
                exclude_modules = []
                if 'exclude_modules' in data:
                    if type(data['exclude_modules']) is not list:
                        raise Exception(f'features.yml is invalid. (The “exclude_modules” element must be a list element. data={data})')
                    exclude_modules = data['exclude_modules']
                func(data['package'], data['prefix'], exclude_modules, appcls, ver, logger, self.is_features_loaded(ftype))
                self.features_loaded[ftype] = True

    def load_features_args(self, args_dict:Dict[str, Any]):
        yml = self.features_yml_data
        if yml is None:
            return
        if 'args' not in yml or 'cli' not in yml['args']:
            return

        opts = self.list_options()
        def _cast(self, key, val):
            for opt in opts.values():
                if f"--{key}" in opt['opts']:
                    if opt['type'] == int:
                        return int(val)
                    elif opt['type'] == float:
                        return float(val)
                    elif opt['type'] == bool:
                        return True
                    else:
                        return eval(val)
            return None

        for rule in yml['args']['cli']:
            if type(rule) is not dict:
                raise Exception(f'features.yml is invalid. (The “args.cli” element must be a list element must be a dictionary. rule={rule})')
            if 'rule' not in rule:
                raise Exception(f'features.yml is invalid. (The “rule” element must be in the dictionary of the list element of the “args.cli” element. rule={rule})')
            if rule['rule'] is None:
                continue
            if 'default' not in rule and 'coercion' not in rule:
                raise Exception(f'features.yml is invalid. (The “default” or “coercion” element must be in the dictionary of the list element of the “args.cli” element. rule={rule})')
            if len([rk for rk in rule['rule'] if rk not in args_dict or rule['rule'][rk] != args_dict[rk]]) > 0:
                continue
            if 'default' in rule and rule['default'] is not None:
                for dk, dv in rule['default'].items():
                    if dk not in args_dict or args_dict[dk] is None:
                        if type(dv) == list:
                            args_dict[dk] = [_cast(self, dk, v) for v in dv]
                        else:
                            args_dict[dk] = _cast(self, dk, dv)
            if 'coercion' in rule and rule['coercion'] is not None:
                for ck, cv in rule['coercion'].items():
                    if type(cv) == list:
                        args_dict[ck] = [_cast(self, ck, v) for v in cv]
                    else:
                        args_dict[ck] = _cast(self, ck, cv)

    def load_features_aliases_cli(self, logger:logging.Logger):
        yml = self.features_yml_data
        if yml is None: return
        if self.aliases_loaded_cli: return
        if 'aliases' not in yml or 'cli' not in yml['aliases']:
            return

        opt_cmd = self._options["cmd"].copy()
        for rule in yml['aliases']['cli']:
            if type(rule) is not dict:
                raise Exception(f'features.yml is invalid. (The aliases.cli” element must be a list element must be a dictionary. rule={rule})')
            if 'source' not in rule:
                raise Exception(f'features.yml is invalid. (The source element must be in the dictionary of the list element of the aliases.cli” element. rule={rule})')
            if 'target' not in rule:
                raise Exception(f'features.yml is invalid. (The target element must be in the dictionary of the list element of the aliases.cli” element. rule={rule})')
            if rule['source'] is None or rule['target'] is None:
                if logger.level == logging.DEBUG:
                    logger.debug(f'Skip cli rule in features.yml. (The source or target element is None. rule={rule})')
                continue
            if type(rule['source']) is not dict:
                raise Exception(f'features.yml is invalid. (The aliases.cli.source” element must be a dictionary element must. rule={rule})')
            if type(rule['target']) is not dict:
                raise Exception(f'features.yml is invalid. (The aliases.cli.target element must be a dictionary element must. rule={rule})')
            if 'mode' not in rule['source'] or 'cmd' not in rule['source']:
                raise Exception(f'features.yml is invalid. (The aliases.cli.source element must have "mode" and "cmd" specified. rule={rule})')
            if 'mode' not in rule['target'] or 'cmd' not in rule['target']:
                raise Exception(f'features.yml is invalid. (The aliases.cli.target element must have "mode" and "cmd" specified. rule={rule})')
            if rule['source']['mode'] is None or rule['source']['cmd'] is None:
                if logger.level == logging.DEBUG:
                    logger.debug(f'Skip cli rule in features.yml. (The source mode or cmd element is None. rule={rule})')
                continue
            if rule['target']['mode'] is None or rule['target']['cmd'] is None:
                if logger.level == logging.DEBUG:
                    logger.debug(f'Skip cli rule in features.yml. (The target mode or cmd element is None. rule={rule})')
                continue
            tgt_move = True if 'move' in rule['target'] and rule['target']['move'] else False
            reg_src_cmd = re.compile(rule['source']['cmd'])
            for mk, mv in opt_cmd.items():
                if type(mv) is not dict: continue
                if mk != rule['source']['mode']: continue
                src_mode = mk
                tgt_mode = rule['target']['mode']
                self._options["cmd"][tgt_mode] = dict() if tgt_mode not in self._options["cmd"] else self._options["cmd"][tgt_mode]
                self._options["mode"][tgt_mode] = dict() if tgt_mode not in self._options["mode"] else self._options["mode"][tgt_mode]
                find = False
                for ck, cv in mv.copy().items():
                    if type(cv) is not dict: continue
                    ck_match:re.Match = reg_src_cmd.search(ck)
                    if ck_match is None: continue
                    find = True
                    src_cmd = ck
                    tgt_cmd = rule['target']['cmd'].format(*([ck_match.string]+list(ck_match.groups())))
                    cv = cv.copy()
                    cv['opt'] = tgt_cmd
                    # cmd/[target mode]/[target cmd]に追加
                    self._options["cmd"][tgt_mode][tgt_cmd] = cv
                    # mode/[target mode]/[target cmd]に追加
                    self._options["mode"][tgt_mode][tgt_cmd] = cv
                    # mode/choiceにtarget modeがない場合は追加
                    found_mode_choice = False
                    for i, me in enumerate(self._options["mode"]["choice"]):
                        if me['opt'] == tgt_mode:
                            me[tgt_cmd] = cv.copy()
                            found_mode_choice = True
                        # 移動の場合は元を削除
                        if tgt_move and me['opt'] == src_mode and src_cmd in me:
                            del me[src_cmd]
                    if not found_mode_choice:
                        self._options["mode"]["choice"].append({'opt':tgt_mode, tgt_cmd:cv})
                    # cmd/choiceにtarget cmdがない場合は追加
                    found_cmd_choice = False
                    for i, ce in enumerate(self._options["cmd"]["choice"]):
                        if ce['opt'] == tgt_cmd:
                            self._options["cmd"]["choice"][i] = cv
                            found_cmd_choice = True
                        # 移動の場合は元を削除(この処理をするとモード違いの同名コマンドが使えなくなるのでコメントアウト)
                        #if tgt_move and ce['opt'] == src_cmd:
                        #    self._options["cmd"]["choice"].remove(ce)
                    if not found_cmd_choice:
                        self._options["cmd"]["choice"].append(cv)
                    # 移動の場合は元を削除
                    if tgt_move:
                        if logger.level == logging.DEBUG:
                            logger.debug(f'move command: src=({src_mode},{src_cmd}) -> tgt=({tgt_mode},{tgt_cmd})')
                        if src_cmd in self._options["cmd"][src_mode]:
                            del self._options["cmd"][src_mode][src_cmd]
                    else:
                        if logger.level == logging.DEBUG:
                            logger.debug(f'copy command: src=({src_mode},{src_cmd}) -> tgt=({tgt_mode},{tgt_cmd})')
                if not find:
                    logger.warning(f'Skip cli rule in features.yml. (Command matching the rule not found. rule={rule})')
                if len(self._options["cmd"][src_mode]) == 1:
                    del self._options["cmd"][src_mode]
                if len(self._options["mode"][src_mode]) == 1:
                    del self._options["mode"][src_mode]
        self.aliases_loaded_cli = True

    def load_features_aliases_web(self, routes:List[Route], logger:logging.Logger):
        yml = self.features_yml_data
        if yml is None: return
        if self.aliases_loaded_web: return
        if routes is None or type(routes) is not list or len(routes) == 0:
            raise Exception(f'routes is invalid. (The routes must be a list element.) routes={routes}')
        if 'aliases' not in yml or 'web' not in yml['aliases']:
            return

        for rule in yml['aliases']['web']:
            if type(rule) is not dict:
                raise Exception(f'features.yml is invalid. (The aliases.web element must be a list element must be a dictionary. rule={rule})')
            if 'source' not in rule:
                raise Exception(f'features.yml is invalid. (The source element must be in the dictionary of the list element of the aliases.web element. rule={rule})')
            if 'target' not in rule:
                raise Exception(f'features.yml is invalid. (The target element must be in the dictionary of the list element of the aliases.web element. rule={rule})')
            if rule['source'] is None or rule['target'] is None:
                if logger.level == logging.DEBUG:
                    logger.debug(f'Skip web rule in features.yml. (The source or target element is None. rule={rule})')
                continue
            if type(rule['source']) is not dict:
                raise Exception(f'features.yml is invalid. (The aliases.web.source” element must be a dictionary element must. rule={rule})')
            if type(rule['target']) is not dict:
                raise Exception(f'features.yml is invalid. (The aliases.web.target element must be a dictionary element must. rule={rule})')
            if 'path' not in rule['source']:
                raise Exception(f'features.yml is invalid. (The aliases.web.source element must have "path" specified. rule={rule})')
            if 'path' not in rule['target']:
                raise Exception(f'features.yml is invalid. (The aliases.web.target element must have "path" specified. rule={rule})')
            if rule['source']['path'] is None:
                if logger.level == logging.DEBUG:
                    logger.debug(f'Skip web rule in features.yml. (The source path element is None. rule={rule})')
                continue
            if rule['target']['path'] is None:
                if logger.level == logging.DEBUG:
                    logger.debug(f'Skip web rule in features.yml. (The target path element is None. rule={rule})')
                continue
            tgt_move = True if 'move' in rule['target'] and rule['target']['move'] else False
            reg_src_path = re.compile(rule['source']['path'])
            find = False
            for route in routes.copy():
                if not isinstance(route, APIRoute):
                    continue
                route_path = route.path
                path_match:re.Match = reg_src_path.search(route_path)
                if path_match is None: continue
                find = True
                tgt_Path = rule['target']['path'].format(*([path_match.string]+list(path_match.groups())))
                tgt_route = APIRoute(tgt_Path, route.endpoint, methods=route.methods, name=route.name,
                                  include_in_schema=route.include_in_schema)
                routes.append(tgt_route)
                if tgt_move:
                    if logger.level == logging.DEBUG:
                        logger.debug(f'move route: src=({route_path}) -> tgt=({tgt_Path})')
                    routes.remove(route)
                else:
                    if logger.level == logging.DEBUG:
                        logger.debug(f'copy route: src=({route_path}) -> tgt=({tgt_Path})')
            if not find:
                logger.warning(f'Skip web rule in features.yml. (Command matching the rule not found. rule={rule})')
        self.aliases_loaded_web = True
