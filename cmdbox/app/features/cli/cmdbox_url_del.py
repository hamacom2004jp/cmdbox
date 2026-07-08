from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic


class UrlDel(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'del'
    
    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="短縮URLを削除します。指定されたurl_idのJSONファイルを削除します。",
            description_en="Delete a short URL. Removes the JSON file for the specified url_id.",
            choice=[
                dict(opt="url_id", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="削除する短縮URLのurl_idを指定します。",
                     description_en="Specify the url_id of the short URL to delete."),
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
            # JSONファイルのパスを指定
            urls_dir = Path(self.default_data) / '.urls'
            json_file = urls_dir / f"{args.url_id}.json"
            
            # ファイルが存在するか確認
            if not json_file.exists():
                msg = dict(warn=f"Short URL '{args.url_id}' not found at '{json_file}'.")
                logger.warning(msg['warn'])
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            
            # ファイルを削除
            json_file.unlink()
            
            # 結果を返す
            msg = dict(success=dict(
                url_id=args.url_id,
                msg=f"Short URL '{args.url_id}' deleted."
            ))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception as e:
            msg = dict(warn=f"{e}")
            logger.error(f"Error in url_del: {e}", exc_info=True)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            url_id: Union[str, None] = pydantic.Field(default=None, description="削除されたURL ID")
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果のメッセージ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
