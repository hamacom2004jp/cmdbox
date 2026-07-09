from cmdbox.app import common, feature
from cmdbox.app.commons import cache, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from datetime import datetime
import argparse
import logging
import json
import pydantic


class UrlLoad(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'load'
    
    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="短縮URLを読み込みます。指定されたurl_idの情報を取得します。",
            description_en="Load a short URL. Retrieves information for the specified url_id.",
            choice=[
                dict(opt="url_id", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込む短縮URLのurl_idを指定します。",
                     description_en="Specify the url_id of the short URL to load."),
            ]
        )

    @cache.apprun_cache(args_key='url_id')
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
            # JSONファイルのパスを指定
            urls_dir = Path(self.default_data) / '.urls'
            json_file = urls_dir / f"{args.url_id}.json"
            
            # ファイルが存在するか確認
            if not json_file.exists():
                msg = dict(warn=f"Short URL '{args.url_id}' not found at '{json_file}'.")
                logger.warning(msg['warn'])
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            
            # ファイルを読み込み
            with json_file.open('r', encoding='utf-8') as f:
                url_data = json.load(f)
            
            # 期限切れをチェック
            if 'period_dt' in url_data:
                period_dt = datetime.fromisoformat(url_data['period_dt'])
                if datetime.now() > period_dt:
                    # 期限切れの場合、ファイルを削除
                    json_file.unlink()
                    msg = dict(warn=f"Short URL '{args.url_id}' not found at '{json_file}'.")
                    logger.warning(msg['warn'])
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            
            # 結果を返す
            msg = dict(success=dict(data=url_data))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception as e:
            msg = dict(warn=f"{e}")
            logger.error(f"Error in url_load: {e}", exc_info=True)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class UrlData(resdata.Base):
            url_id: Union[str, None] = pydantic.Field(default=None, description="URL ID")
            short_url: Union[str, None] = pydantic.Field(default=None, description="生成された短縮URL")
            target_url: Union[str, None] = pydantic.Field(default=None, description="リダイレクト先URL")
            base_url: Union[str, None] = pydantic.Field(default=None, description="短縮URLのベースURL")
            period: Union[int, None] = pydantic.Field(default=None, description="有効期限の秒数")
            saved_at: Union[str, None] = pydantic.Field(default=None, description="保存日時")
            period_dt: Union[str, None] = pydantic.Field(default=None, description="期限切れ日時")
        class Data(resdata.Data):
            data: Union[UrlData, None] = pydantic.Field(default=None, description="URL情報")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
