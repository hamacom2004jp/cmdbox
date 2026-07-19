from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic


class CmdboxInfo(feature.UnsupportEdgeFeature, validator.Validator):
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
        return 'info'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="Cmdbox の情報を表示します。",
            description_en="Display Cmdbox information.",
            choice=[
                dict(opt="enable_value", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"バージョン値のみを表示するかどうかを指定します。この指定を行うと他のフラグは無視します。",
                     description_en=f"Specify whether to display only the version value. If this option is specified, other flags are ignored."),
                dict(opt="enable_logo", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"ロゴを含めるかどうかを指定します。",
                     description_en=f"Specify whether to include the logo."),
                dict(opt="enable_version", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"バージョン情報を含めるかどうかを指定します。",
                     description_en=f"Specify whether to include the version information."),
                dict(opt="enable_appid", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"AppID を含めるかどうかを指定します。",
                     description_en=f"Specify whether to include the AppID."),
                dict(opt="enable_title", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"タイトルを含めるかどうかを指定します。",
                     description_en=f"Specify whether to include the title."),
                dict(opt="enable_copyright", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"著作権情報を含めるかどうかを指定します。",
                     description_en=f"Specify whether to include the copyright information."),
                dict(opt="enable_description", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"説明を含めるかどうかを指定します。",
                     description_en=f"Specify whether to include the description."),
                dict(opt="enable_other", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja=f"その他の情報を含めるかどうかを指定します。",
                     description_en=f"Specify whether to include other information."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        if args.enable_value:
            v = getattr(self.ver, '__version__', None)
            common.print_format(v, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, v, None
        data = dict()
        success = dict(data=data)
        msg = dict(success=success)
        if args.enable_logo:
            data['logo'] = getattr(self.ver, '__logo__', None)
        if args.enable_version:
            data['version'] = getattr(self.ver, '__version__', None)
        if args.enable_appid:
            data['appid'] = getattr(self.ver, '__appid__', None)
        if args.enable_title:
            data['title'] = getattr(self.ver, '__title__', None)
        if args.enable_copyright:
            data['copyright'] = getattr(self.ver, '__copyright__', None)
        if args.enable_description:
            data['description'] = getattr(self.ver, '__description__', None)
        if args.enable_other:
            data['pypiurl'] = getattr(self.ver, '__pypiurl__', None)
            data['srcurl'] = getattr(self.ver, '__srcurl__', None)
            data['docurl'] = getattr(self.ver, '__docurl__', None)
        if not data:
            data['logo'] = getattr(self.ver, '__logo__', None)
            data['version'] = getattr(self.ver, '__version__', None)
            data['appid'] = getattr(self.ver, '__appid__', None)
            data['title'] = getattr(self.ver, '__title__', None)
            data['copyright'] = getattr(self.ver, '__copyright__', None)
            data['pypiurl'] = getattr(self.ver, '__pypiurl__', None)
            data['srcurl'] = getattr(self.ver, '__srcurl__', None)
            data['docurl'] = getattr(self.ver, '__docurl__', None)
            data['description'] = getattr(self.ver, '__description__', None)
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS, msg, None

    def output_schema(self) -> type:
        class Version(resdata.Base):
            logo: Union[str, None] = pydantic.Field(default=None, description="ロゴ")
            version: Union[str, None] = pydantic.Field(default=None, description="バージョン")
            appid: Union[str, None] = pydantic.Field(default=None, description="AppID")
            title: Union[str, None] = pydantic.Field(default=None, description="タイトル")
            copyright: Union[str, None] = pydantic.Field(default=None, description="著作権情報")
            description: Union[str, None] = pydantic.Field(default=None, description="説明")
            pypiurl: Union[str, None] = pydantic.Field(default=None, description="PyPi URL")
            srcurl: Union[str, None] = pydantic.Field(default=None, description="Source Code URL")
            docurl: Union[str, None] = pydantic.Field(default=None, description="Document URL")
        class Data(resdata.Data):
            data: Union[str, Version, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return None
