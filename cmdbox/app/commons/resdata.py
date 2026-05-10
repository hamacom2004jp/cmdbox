from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import PydanticUndefined
from typing import Dict, Any, Tuple, List, Union


class Base(BaseModel):
    """
    コマンドの実行結果を表すクラス
    """
    @classmethod
    def get_model_info(cls) -> Dict[str, Any]:
        """
        モデルの情報を取得するメソッド
        Returns:
            dict: モデルの情報を表す辞書
        """
        info = {}
        for name, field in cls.model_fields.items():
            info[name] = {
                'type': str(field.annotation),
                'default': field.default if field.default is not PydanticUndefined else None,
                'required': field.is_required(),
                'description': field.description,
            }
        return info

    @classmethod
    def forbid_on(cls):
        """
        定義されていないフィールドを禁止するためのConfigDictを返すクラスメソッド
        Returns:
            ConfigDict: 定義されていないフィールドを禁止するConfigDict
        """
        return ConfigDict(extra="forbid")

    @classmethod
    def forbid_off(cls):
        """
        定義されていないフィールドを許可するためのConfigDictを返すクラスメソッド
        Returns:
            ConfigDict: 定義されていないフィールドを許可するConfigDict
        """
        return ConfigDict(extra="allow")

class KeyVal(Base):
    """
    キーと値のペアを表すクラス
    """
    model_config = Base.forbid_on()  # 定義されていないフィールドを禁止
    key: str = Field(description="キー")
    value: Union[Any, None] = Field(default=None, alias="val", description="値")

class NamePath(Base):
    """
    名前とパスのペアを表すクラス
    """
    model_config = Base.forbid_on()  # 定義されていないフィールドを禁止
    name: str = Field(description="名前")
    path: Union[Path, str, None] = Field(default=None, description="パス")

class Data(Base):
    """
    コマンドの実行結果のデータを表すクラス
    """
    model_config = Base.forbid_on()  # 定義されていないフィールドを禁止
    #data: Union[Dict[str, Any], List[Any], str, int, float, bool, None] = None
    performance: Union[List[KeyVal], None] = Field(default=None, description="パフォーマンス情報のリスト")

class Result(Base):
    """
    コマンドの実行結果を表すクラス
    """
    model_config = Base.forbid_on()  # 定義されていないフィールドを禁止
    success: Union[Data, str, bool, None] = Field(default=None, description="成功した場合の結果")
    warn: Union[Dict[str, Any], Data, str, bool, None] = Field(default=None, description="警告がある場合の結果")
    error: Union[Dict[str, Any], Data, str, bool, None] = Field(default=None, description="エラーがある場合の結果")
    schema: Union[Dict[str, Any], None] = Field(default=None, description="スキーマ情報")
    end: Union[bool, None] = Field(default=None, description="終了フラグ")
