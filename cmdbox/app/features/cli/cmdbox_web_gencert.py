from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from datetime import datetime, timedelta, timezone
from cmdbox.app import common
from cmdbox.app.feature import Feature
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class WebGencert(Feature):
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
        return 'gencert'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="webモードでSSLを簡易的に実装するために自己署名証明書を生成します。",
            discription_en="Generate a self-signed certificate for simple implementation of SSL in web mode.",
            test_assert="assert result != ''",
            choice=[
                dict(opt="webhost", type="str", default="localhost", required=True, multi=False, hide=False, choice=None,
                        discription_ja="自己署名証明書のCN(Common Name)に指定するホスト名を指定します。",
                        discription_en="Specify the host name to be specified as the CN (Common Name) of the self-signed certificate."),
                dict(opt="output_cert", type="file", default=None, required=False, multi=False, hide=False, choice=None,
                        discription_ja="出力する自己署名証明書のファイルを指定します。省略した場合は `webhostオプションに指定したホスト名` .crt に出力されます。",
                        discription_en="Specify the self-signed certificate file to be output.If omitted, the hostname specified in the `webhost option` .crt will be output."),
                dict(opt="output_cert_format", type="str", default="PEM", required=False, multi=False, hide=False, choice=["DER", "PEM"],
                        discription_ja="出力する自己署名証明書のファイルフォーマットを指定します。",
                        discription_en="Specifies the file format of the self-signed certificate to be output."),
                dict(opt="output_key", type="file", default=None, required=False, multi=False, hide=False, choice=None,
                        discription_ja="出力する自己署名証明書の秘密鍵ファイルを指定します。省略した場合は `webhostオプションに指定したホスト名` .key に出力されます。",
                        discription_en="Specifies the private key file of the self-signed certificate to be output.If omitted, the hostname specified in the `webhost option` .key will be output."),
                dict(opt="output_key_format", type="str", default="PEM", required=False, multi=False, hide=False, choice=["DER", "PEM"],
                        discription_ja="出力する自己署名証明書の秘密鍵ファイルフォーマットを指定します。",
                        discription_en="Specifies the private key file format of the output self-signed certificate."),
                dict(opt="overwrite", type="bool", default=False, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="出力する自己署名証明書のファイルが存在する場合に上書きします。",
                        discription_en="Overwrites the self-signed certificate file to be output if it exists."),
                dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                        discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                        discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                        discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
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
        if args.webhost is None:
            msg = {"warn":f"Please specify the --webhost option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.output_cert is None:
            args.output_cert = f"{args.webhost}.crt"
        if args.output_key is None:
            args.output_key = f"{args.webhost}.key"
        output_cert = Path(args.output_cert)
        output_key = Path(args.output_key)
        if not args.overwrite and output_cert.exists():
            msg = {"warn":f"File already exists. {output_cert}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if not args.overwrite and output_key.exists():
            msg = {"warn":f"File already exists. {output_key}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None

        try:
            self.gen_cert(logger, args.webhost, output_cert, output_key)
            ret = {"success":f"Generate certificate. {output_cert}, {output_key}"}
        except Exception as e:
            msg = {"error":f"Failed to generate certificate. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        return 0, ret, None

    def gen_cert(self, logger:logging.Logger, webhost:str,
                 output_cert:Path, output_cert_format:str,
                 output_key:Path, output_key_format:str) -> None:
        # 秘密鍵の作成
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        # 秘密鍵の保存
        with open(output_key, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.DER if output_key_format == "DER" else serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption() #BestAvailableEncryption(b"passphrase"),
            ))
            logger.info(f"Save private key. {output_key}")

        # 自己署名証明書の作成
        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, webhost)
        ])
        self_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(timezone.utc)
        ).not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=365*10)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(webhost)]),
            critical=False,
        ).sign(private_key, hashes.SHA256())

        # 自己署名証明書の保存
        with open(output_cert, "wb") as f:
            f.write(self_cert.public_bytes(serialization.Encoding.DER if output_cert_format == "DER" else serialization.Encoding.PEM))
            logger.info(f"Save self-signed certificate. {output_cert}")
