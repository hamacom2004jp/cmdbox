from cmdbox.app import feature, options
from cmdbox.app.commons import resdata
from typing import Any, Callable, Dict, List, Tuple, Union
from unittest.mock import patch
import argparse
import logging


class TestCase(resdata.Base):
    """
    テストケースを表すクラス
    """
    model_config = resdata.ConfigDict(arbitrary_types_allowed=True) 
    name: str = resdata.Field(description="テストケースの名前(必須)")
    description: Union[str, None] = resdata.Field(default=None, description="テストケースの説明(省略可能)")
    args: argparse.Namespace = resdata.Field(description="テストケースのオプションパラメータ(必須)")
    exec_cmd: Union[Callable[
        [logging.Logger, argparse.Namespace, float, List[Dict[str, float]], Any],
        Any], None] = resdata.Field(default=None, description="コマンドの実行関数(省略可能)")
    output: Tuple[int, Dict[str, Any], Any] = resdata.Field(description="期待される出力(必須：リターンコード、メッセージ、オブジェクト)")
    assertion: Union[Callable[
        [logging.Logger, argparse.Namespace, float, List[Dict[str, float]], Any,
         Tuple[int, Dict[str, Any], Any], Tuple[int, Dict[str, Any], Any]],
        Any], None] = resdata.Field(default=None, description="テスト結果の検証関数(省略可能)")

class UnitTestable(feature.Feature):
    def create_base_args(self, logger:logging.Logger, args: argparse.Namespace) -> argparse.Namespace:
        """
        テストケースの基本的な引数を作成するためのメソッド
        Args:
            logger (logging.Logger): ロガーオブジェクト
            args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
        Returns:
            argparse.Namespace: テストケースの基本的な引数を含むNamespaceオブジェクト
        """
        common_opt = options.Options(self.appcls, self.ver)
        common_opt.init_options()
        opt = {name: info.get('default', None) for name, info in common_opt._options.items()}
        opt_ref = self.get_option()
        opt.update({o['opt']: o.get('default', None) for o in opt_ref.get('choice', [])})
        base_args = argparse.Namespace(**opt)
        base_args.mode = self.get_mode()
        base_args.cmd = self.get_cmd()
        return base_args

    def create_tests(self, logger:logging.Logger, base_args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]) -> List[TestCase]:
        """
        テストケースを作成するためのメソッド
        Returns:
            List[TestCase]: テストケースのリスト
        """
        tests = []
        _0_args = argparse.Namespace(**vars(base_args))
        tests.append(TestCase(
            name="Test Case 1",
            description="This is a sample test case.",
            args=_0_args,
            output=(0, dict(success=dict(data="")), None),
        ))
        return tests

    def run_tests(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        """
        テストケースを実行するためのメソッド
        Args:
            logger (logging.Logger): ロガーオブジェクト
            args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
            tm (float): コマンドの実行時間を測定するためのタイムスタンプ
            pf (List[Dict[str, float]]): コマンドの実行時間を測定するためのパフォーマンスデータのリスト
        Returns:
            Tuple[int, Dict[str, Any], Any]: テストの実行結果(リターンコード、メッセージ、オブジェクト)
        """
        base_args = self.create_base_args(logger, args)
        tests = self.create_tests(logger, base_args, tm, pf)
        _bef = self.exec_before(logger, args, tm, pf)
        for test in tests:
            if test.exec_cmd:
                _res = test.exec_cmd(logger, test.args, tm, pf, _bef)
            else:
                _res = self.exec_cmd(logger, test.args, tm, pf, _bef)
            if test.assertion:
                test.assertion(logger, test.args, tm, pf, _bef, _res, test.output)
            else:
                self.assertion(logger, test.args, tm, pf, _bef, _res, test.output)
        self.exec_after(logger, args, tm, pf, _bef) if test.after else None

    def exec_before(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]) -> Any:
        """
        前処理を実行するためのメソッド
        Args:
            logger (logging.Logger): ロガーオブジェクト
            args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
            tm (float): コマンドの実行時間を測定するためのタイムスタンプ
            pf (List[Dict[str, float]]): コマンドの実行時間を測定するためのパフォーマンスデータのリスト
        Returns:
            Any: 前処理の結果
        """
        logger.info("Running before test case...")
        return None

    def exec_cmd(self, logger:logging.Logger, test_args:argparse.Namespace, tm:float, pf:List[Dict[str, float]], _bef:Any) -> Tuple[int, Dict[str, Any], Any]:
        """
        コマンドを実行するためのメソッド
        Args:
            logger (logging.Logger): ロガーオブジェクト
            test_args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
            tm (float): コマンドの実行時間を測定するためのタイムスタンプ
            pf (List[Dict[str, float]]): コマンドの実行時間を測定するためのパフォーマンスデータのリスト
            _bef (Any): 前処理の結果
        Returns:
            Tuple[int, Dict[str, Any], Any]: コマンドの実行結果(リターンコード、メッセージ、オブジェクト)
        """
        app_instance = self.appcls.getInstance(appcls=self.appcls, ver=self.ver)
        args_list = options.Options.getInstance(appcls=self.appcls, ver=self.ver).mk_opt_list(vars(**test_args), webmode=False)
        with patch("cmdbox.app.common.print_format"):
            ret_code, ret_msg, _obj = app_instance.main(args_list=args_list, webcall=True)
            return ret_code, ret_msg, _obj

    def assertion(self, logger:logging.Logger, test_args:argparse.Namespace, tm:float, pf:List[Dict[str, float]], _bef:Any, _res:Tuple[int, Dict[str, Any], Any], output:Tuple[int, Dict[str, Any], Any]) -> None:
        """
        テスト結果を検証するためのメソッド
        Args:
            logger (logging.Logger): ロガーオブジェクト
            test_args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
            tm (float): コマンドの実行時間を測定するためのタイムスタンプ
            pf (List[Dict[str, float]]): コマンドの実行時間を測定するためのパフォーマンスデータのリスト
            _bef (Any): 前処理の結果
            _res (Tuple[int, Dict[str, Any], Any]): コマンドの実行結果(リターンコード、メッセージ、オブジェクト)
            output (Tuple[int, Dict[str, Any], Any]): 期待される出力(リターンコード、メッセージ、オブジェクト)
        Returns:
            None
        """
        logger.info("Running assertion...")
        assert output.get('success') is not None, "Output must contain 'success' key"
        assert output.get('success',{}).get('data',None) is not None, "Output 'success' must contain 'data' key"

    def exec_after(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]], _bef:Any) -> Any:
        """
        テストケースの後処理を実行するためのメソッド
        Args:
            logger (logging.Logger): ロガーオブジェクト
            args (argparse.Namespace): コマンドの引数を含むNamespaceオブジェクト
            tm (float): コマンドの実行時間を測定するためのタイムスタンプ
            pf (List[Dict[str, float]]): コマンドの実行時間を測定するためのパフォーマンスデータのリスト
            _bef (Any): 前処理の結果
        Returns:
            Any: 後処理の結果
        """
        logger.info("Running after test case...")
        return None
