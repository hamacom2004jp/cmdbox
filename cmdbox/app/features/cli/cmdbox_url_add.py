from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from datetime import datetime, timedelta
import argparse
import logging
import json
import pydantic
import random
import string


class UrlAdd(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language=None):
        super().__init__(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'url'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'add'
    
    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="短縮URLを追加します。target_urlとperiodを指定すると、url_idが生成され、.urlsフォルダにurl_id.jsonファイルが作成されます。",
            description_en="Add a short URL. When target_url and period are specified, a url_id is generated and a url_id.json file is created in the .urls folder.",
            choice=[
                dict(opt="target_url", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="短縮URLのリダイレクト先となるURLを指定します。",
                     description_en="Specify the URL that the short URL will redirect to."),
                dict(opt="period", type=Options.T_INT, default=3600*24*30, required=False, multi=False, hide=False, choice=None,
                     description_ja="短縮URLの有効期限の秒数を指定します。デフォルトは1か月（2592000秒）です。",
                     description_en="Specify the validity period in seconds. Default is 1 month (2592000 seconds)."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
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
        try:
            # url_idを生成（8文字の英数字）
            url_id = common.random_string(size=8)
            
            # .urlsフォルダを作成
            urls_dir = Path(self.default_data) / '.urls'
            urls_dir.mkdir(parents=True, exist_ok=True)
            
            # JSONファイルのパスを指定
            json_file = urls_dir / f"{url_id}.json"
            
            # 保存するデータを作成
            saved_at = datetime.now()
            period = args.period if hasattr(args, 'period') and args.period else 3600*24*30
            period_dt = (saved_at + timedelta(seconds=period)).isoformat()
            url_data = {
                "url_id": url_id,
                "target_url": args.target_url,
                "period": period,
                "saved_at": saved_at.isoformat(),
                "period_dt": period_dt
            }
            # JSONファイルを保存
            common.save_file(json_file, lambda f: json.dump(url_data, f, default=common.default_json_enc), nolock=False)
            # 結果を返す
            msg = dict(success=dict(data=dict(
                url_id=url_id,
                target_url=args.target_url,
                period=url_data["period"],
                saved_at=url_data["saved_at"],
                period_dt=url_data["period_dt"],
                file_path=str(json_file),
                msg=f"Short URL added. url_id={url_id}"
            )))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception as e:
            msg = dict(warn=f"{e}")
            logger.error(f"Error in url_add: {e}", exc_info=True)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:

        class UrlData(resdata.Base):
            url_id: Union[str, None] = pydantic.Field(default=None, description="生成されたURL ID")
            target_url: Union[str, None] = pydantic.Field(default=None, description="リダイレクト先URL")
            period: Union[int, None] = pydantic.Field(default=None, description="有効期限の秒数")
            saved_at: Union[str, None] = pydantic.Field(default=None, description="保存日時")
            period_dt: Union[str, None] = pydantic.Field(default=None, description="期限切れ日時")
            file_path: Union[str, None] = pydantic.Field(default=None, description="作成されたJSONファイルのパス")
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果のメッセージ")
        class Data(resdata.Data):
            data: Union[UrlData, None] = pydantic.Field(default=None, description="URL情報")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
