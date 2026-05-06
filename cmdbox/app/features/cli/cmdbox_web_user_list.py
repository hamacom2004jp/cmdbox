from cmdbox.app import common, feature, web
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic


class WebUserList(feature.UnsupportEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'web'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'user_list'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=False,
            description_ja="Webモードのユーザー一覧を取得します。",
            description_en="Get a list of users in Web mode.",
            choice=[
                dict(opt="user_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ユーザー名を指定して取得します。省略した時は全てのユーザーを取得します。",
                     description_en="Retrieved by specifying a user name. If omitted, all users are retrieved."),
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
            ]
        )

    @validator.apprun_check
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
        w = None
        try:
            w = web.Web(logger, self.default_data, appcls=self.appcls, ver=self.ver,
                        redis_host=self.default_host, redis_port=self.default_port, redis_password=self.default_pass, svname=self.default_svname,
                        signin_file=args.signin_file)
            users = w.user_list(args.user_name)
            msg = dict(success=users)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, w
        except Exception as e:
            msg = dict(warn=f"{e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, w

    def output_schema(self) -> type:
        class UserRecord(resdata.Base):
            uid: Union[str, None] = pydantic.Field(default=None, description="ユーザーID")
            name: Union[str, None] = pydantic.Field(default=None, description="名前")
            password: Union[str, None] = pydantic.Field(default=None, description="パスワード")
            hash: Union[str, None] = pydantic.Field(default=None, description="ハッシュ値")
            email: Union[str, None] = pydantic.Field(default=None, description="メールアドレス")
            groups: Union[List[str], None] = pydantic.Field(default=None, description="所属グループリスト")
            home: Union[str, None] = pydantic.Field(default=None, description="ホームディレクトリ")
        class Data(resdata.Data):
            data: Union[List[UserRecord], None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
