from cmdbox.app import common, feature
from cmdbox.app.commons import cache, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class UrlList(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'list'
    
    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="登録済みの短縮URLを一覧表示します。",
            description_en="Lists registered short URLs.",
            choice=[
                dict(opt="kwd", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="検索したいurl_idを指定します。中間マッチで検索します。",
                     description_en="Specify the url_id to search for. Searches for partial matches."),
            ]
        )

    @cache.apprun_cache(exclude_fn=lambda args: hasattr(args,'kwd') and args.kwd)
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
            results: List[Dict[str, Any]] = []
            
            # .urlsフォルダを確認
            urls_dir = Path(self.default_data) / '.urls'
            if not urls_dir.exists():
                msg = dict(success=dict(data=results, msg="No URLs found."))
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_SUCCESS, msg, None
            
            # キーワード検索の設定
            kwd = args.kwd if hasattr(args, 'kwd') and args.kwd else '*'
            
            # JSONファイルを読み込み
            for json_file in sorted(urls_dir.glob(f"{kwd}.json")):
                try:
                    with json_file.open('r', encoding='utf-8') as f:
                        url_data = json.load(f)
                    results.append(dict(
                        url_id=url_data.get('url_id', json_file.stem),
                        short_url=url_data.get('short_url', None),
                        target_url=url_data.get('target_url', None),
                        base_url=url_data.get('base_url', None),
                        period=url_data.get('period', None),
                        saved_at=url_data.get('saved_at', None),
                        period_dt=url_data.get('period_dt', None),
                    ))
                except Exception as e:
                    logger.warning(f"Error reading {json_file}: {e}")
            
            # 結果を返す
            msg = dict(success=dict(data=results, msg=f"Found {len(results)} URL(s)."))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception as e:
            msg = dict(warn=f"{e}")
            logger.error(f"Error in url_list: {e}", exc_info=True)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class UrlInfo(resdata.Base):
            url_id: Union[str, None] = pydantic.Field(default=None, description="URL ID")
            short_url: Union[str, None] = pydantic.Field(default=None, description="生成された短縮URL")
            target_url: Union[str, None] = pydantic.Field(default=None, description="リダイレクト先URL")
            base_url: Union[str, None] = pydantic.Field(default=None, description="短縮URLのベースURL")
            period: Union[int, None] = pydantic.Field(default=None, description="有効期限の秒数")
            saved_at: Union[str, None] = pydantic.Field(default=None, description="保存日時")
            period_dt: Union[str, None] = pydantic.Field(default=None, description="期限切れ日時")
        class Data(resdata.Data):
            data: Union[List[UrlInfo], None] = pydantic.Field(default=None, description="URL情報のリスト")
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果のメッセージ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
