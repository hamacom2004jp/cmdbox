from cmdbox.app import common, feature
from cmdbox.app.options import Options
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import re
import string


class WebGenpass(feature.OneshotResultEdgeFeature):
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
        return 'genpass'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="webモードで使用できるパスワード文字列を生成します。",
            discription_en="Generates a password string that can be used in web mode.",
            choice=[
                dict(opt="pass_length", type=Options.T_INT, default=16, required=False, multi=False, hide=False, choice=None,
                     discription_ja="パスワードの長さを指定します。",
                     discription_en="Specifies the length of the password."),
                dict(opt="pass_count", type=Options.T_INT, default=5, required=False, multi=False, hide=False, choice=None,
                     discription_ja="生成するパスワードの件数を指定します。",
                     discription_en="Specify the number of passwords to be generated."),
                dict(opt="use_alphabet", type=Options.T_STR, default='both', required=False, multi=False, hide=False, choice=['notuse','upper','lower','both'],
                     discription_ja="パスワードに使用するアルファベットの種類を指定します。 `notuse` , `upper` , `lower` , `both` が指定できます。",
                     discription_en="Specifies the type of alphabet used for the password. `notuse` , `upper` , `lower` , `both` can be specified."),
                dict(opt="use_number", type=Options.T_STR, default="use", required=False, multi=False, hide=False, choice=['notuse', 'use'],
                     discription_ja="パスワードに使用する数字の種類を指定します。 `notuse` , `use` が指定できます。",
                     discription_en="Specify the type of number to be used for the password. `notuse` , `use` can be specified."),
                dict(opt="use_symbol", type=Options.T_STR, default='use', required=False, multi=False, hide=False, choice=['notuse','use'],
                     discription_ja="パスワードに使用する記号の種類を指定します。 `notuse` , `use` が指定できます。",
                     discription_en="Specifies the type of symbol used in the password. `notuse` , `use` can be specified."),
                dict(opt="similar", type=Options.T_STR, default='exclude', required=False, multi=False, hide=True, choice=['exclude', 'include'],
                     discription_ja="特定の似た文字を使用するかどうかを指定します。 `exclude` , `include` が指定できます。",
                     discription_en="Specifies whether certain similar characters should be used. `exclude` , `include` can be specified."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
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
        if args.pass_length < 1:
            msg = dict(warn="The password length must be 1 or more.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pass_count < 1:
            msg = dict(warn="The number of passwords to generate must be 1 or more.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pass_count >= 40:
            msg = dict(warn="The number of passwords to generate must be less than 40.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        ret = {}
        try:
            chars = ""
            if args.use_alphabet == 'upper' or args.use_alphabet == 'both':
                chars += string.ascii_uppercase
            if args.use_alphabet == 'lower' or args.use_alphabet == 'both':
                chars += string.ascii_lowercase
            if args.use_number == 'use':
                chars += string.digits
            if args.use_symbol == 'use':
                chars += '!#$%&()=-~^|@;+:*{}[]<>/_,.'
            if args.similar == 'exclude':
                chars = re.sub('[\{\}\[\]Il1\|Oo0\.\,:;]', '', chars)

            passwords = []
            for i in range(args.pass_count):
                passwords.append(dict(password=common.random_string(args.pass_length, chars)))
            ret = dict(success=dict(passwords=passwords))
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        except Exception as e:
            msg = dict(error=f"Failed to generate password. {e}")
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
