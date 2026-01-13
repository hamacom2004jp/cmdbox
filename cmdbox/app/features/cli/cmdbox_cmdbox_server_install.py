from cmdbox import version
from cmdbox.app import common, feature, install
from cmdbox.app.auth import signin
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import glob
import logging


class CmdboxServerInstall(feature.OneshotEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'cmdbox'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'server_install'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            description_ja="cmdboxのコンテナをインストールします。",
            description_en="Install the cmdbox container.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None,
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="install_cmdbox", type=Options.T_STR, default='cmdbox', required=False, multi=False, hide=True, choice=None,
                     description_ja=f"省略した時は `cmdbox` を使用します。 `cmdbox=={version.__version__}` といった指定も可能です。",
                     description_en=f"When omitted, `cmdbox` is used. You can also specify `cmdbox=={version.__version__}`."),
                dict(opt="install_from", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="作成するdockerイメージの元となるFROMイメージを指定します。",
                     description_en="Specify the FROM image that will be the source of the docker image to be created."),
                dict(opt="install_no_python", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="pythonのインストールを行わないようにします。",
                     description_en="Do not install python."),
                dict(opt="install_compile_python", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="python3をコンパイルしてインストールします。install_no_pythonが指定されるとそちらを優先します。",
                     description_en="Compile and install python3; if install_no_python is specified, it is preferred."),
                dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                     description_en="If specified, you can add to the tag name of the docker image to create."),
                dict(opt="install_use_gpu", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="GPUを使用するモジュール構成でインストールします。",
                     description_en="Install with a module configuration that uses the GPU."),
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["", "voicevox"],
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_os", "voicevox_arc", "voicevox_device", "voicevox_whl"]),
                     description_ja="使用するTTSエンジンを指定します。",
                     description_en="Specify the TTS engine to use."),
                dict(opt="voicevox_ver", type=Options.T_STR, default='0.16.3', required=False, multi=False, hide=False,
                     choice=['', '0.16.3'],
                     choice_edit=True,
                     description_ja="使用するVOICEVOXのバージョンを指定します。",
                     description_en="Specify the version of VOICEVOX to use."),
                dict(opt="voicevox_whl", type=Options.T_STR, default='voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl', required=False, multi=False, hide=False,
                     choice=['',
                             'voicevox_core-0.16.3-cp310-abi3-win32.whl',
                             'voicevox_core-0.16.3-cp310-abi3-win_amd64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-macosx_10_12_x86_64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-macosx_11_0_arm64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_aarch64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl',
                             ],
                     choice_edit=True,
                     description_ja="使用するVOICEVOXのホイールファイルを指定します。",
                     description_en="Specify the VOICEVOX wheel file to use."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.data is None:
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        inst = install.Install(logger, self.appcls, self.ver)
        ret = inst.server_install(Path(args.data),
                                  install_cmdbox_tgt=args.install_cmdbox,
                                  install_from=args.install_from,
                                  install_no_python=args.install_no_python,
                                  install_compile_python=args.install_compile_python,
                                  install_tag=args.install_tag,
                                  install_use_gpu=args.install_use_gpu,
                                  tts_engine=args.tts_engine,
                                  voicevox_ver=args.voicevox_ver,
                                  voicevox_whl=args.voicevox_whl)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None
