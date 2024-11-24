from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFile
from PIL.Image import Resampling
from typing import Tuple
import base64
import numpy as np


def npyfile2npy(fp) -> np.ndarray:
    """
    npyファイルからndarrayを読み込みます。

    Args:
        fp ([type]): npyファイルのパス

    Returns:
        np.ndarray: 読み込んだndarray
    """
    return np.load(fp)

def npybytes2npy(npy:bytes) -> np.ndarray:
    """
    バイト列からndarrayを読み込みます。

    Args:
        npy (bytes): ndarrayのバイト列

    Returns:
        np.ndarray: 読み込んだndarray
    """
    return np.load(BytesIO(npy))

def npy2b64str(npy:np.ndarray) -> str:
    """
    ndarrayをBase64エンコードした文字列を返します。

    Args:
        npy (np.ndarray): ndarray

    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(npy.tobytes()).decode('utf-8')

def npy2img(npy:np.ndarray) -> Image.Image:
    """
    ndarrayをPILのImageオブジェクトに変換します。

    Args:
        npy (np.ndarray): ndarray

    Returns:
        Image.Image: PILのImageオブジェクト
    """
    return Image.fromarray(npy)

def b64str2bytes(b64str:str) -> bytes:
    """
    Base64文字列をバイト列に変換します。

    Parameters:
        b64str (str): Base64形式の文字列

    Returns:
        bytes: バイト列
    """
    return base64.b64decode(b64str)

def b64str2npy(b64str:str, shape:Tuple=None, dtype:str='uint8') -> np.ndarray:
    """
    Base64エンコードされた文字列からndarrayを復元します。

    Args:
        b64str (str): Base64エンコードされた文字列
        shape (tuple): ndarrayの形状
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: 復元したndarray
    """
    if shape is None:
        return np.frombuffer(base64.b64decode(b64str), dtype=dtype)
    return np.frombuffer(base64.b64decode(b64str), dtype=dtype).reshape(shape)

def npy2imgfile(npy, output_image_file:Path=None, image_type:str='jpeg') -> bytes:
    """
    ndarrayを画像bytesに変換しoutput_image_fileに保存します。
    output_image_fileが省略された場合は保存されません

    Args:
        npy ([type]): ndarray
        output_image_file (Path): 保存先の画像ファイルパス

    Returns:
        bytes: 画像のバイト列
    """
    image = Image.fromarray(npy)
    image_type = 'jpeg' if image_type == 'jpg' else image_type
    img_byte = img2byte(image, format=image_type)
    if output_image_file is not None:
        with open(output_image_file, 'wb') as f:
            f.write(img_byte)
    return img_byte

def bytes2b64str(img:bytes) -> str:
    """
    画像のバイト列をBase64エンコードします。

    Args:
        img (bytes): 画像のバイト列

    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(img).decode('utf-8')

def bgr2rgb(npy:np.ndarray) -> np.ndarray:
    """
    BGRのndarrayをRGBに変換します。

    Args:
        npy (np.ndarray): BGRのndarray

    Returns:
        np.ndarray: RGBのndarray
    """
    return npy[..., ::-1].copy()

def imgbytes2thumbnail(img:bytes, size:Tuple[float, float]) -> Image.Image:
    """
    画像のバイト列をサムネイルに変換します。

    Args:
        img (bytes): 画像のバイト列
        size (Tuple[float, float]): サムネイルのサイズ(width, height)

    Returns:
        Image.Image: サムネイル
    """
    i = Image.open(BytesIO(img))
    i.thumbnail(size, Resampling.LANCZOS)

    return i

def imgbytes2npy(img:bytes, dtype:str='uint8') -> np.ndarray:
    """
    画像のバイト列をndarrayに変換します。

    Args:
        img (bytes): 画像のバイト列
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    img = Image.open(BytesIO(img))
    return np.array(img, dtype=dtype)

def imgbytes2img(img:bytes) -> ImageFile:
    """
    画像のバイト列をPILのImageオブジェクトに変換します。

    Args:
        img (bytes): 画像のバイト列

    Returns:
        ImageFile: PILのImageオブジェクト
    """
    return Image.open(BytesIO(img))

def img2npy(img:Image.Image, dtype:str='uint8') -> np.ndarray:
    """
    PILのImageオブジェクトをndarrayに変換します。

    Args:
        img (Image.Image): PILのImageオブジェクト
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    return np.array(img, dtype=dtype)

def imgfile2npy(fp, dtype:str='uint8') -> np.ndarray:
    """
    画像ファイルをndarrayに変換します。

    Args:
        fp ([type]): 画像ファイルのパス
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    img = Image.open(fp)
    return np.array(img, dtype=dtype)

def img2npy(image:Image.Image, dtype:str='uint8') -> np.ndarray:
    """
    PILのImageオブジェクトをndarrayに変換します。

    Args:
        image (Image.Image): PILのImageオブジェクト
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    return np.array(image, dtype=dtype)

def img2byte(image:Image.Image, format:str='jpeg') -> bytes:
    """
    画像をバイト列に変換します。

    Args:
        image (Image.Image): PILのImageオブジェクト
        format (str, optional): 画像のフォーマット. Defaults to 'jpeg'.

    Returns:
        bytes: 画像のバイト列
    """
    with BytesIO() as buffer:
        image.save(buffer, format=format)
        return buffer.getvalue()

def str2b64str(s:str) -> str:
    """
    文字列をBase64エンコードします。

    Args:
        s (str): 文字列

    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(s.encode()).decode('utf-8')

def b64str2str(b64str:str) -> str:
    """
    Base64エンコードされた文字列をデコードします。

    Args:
        b64str (str): Base64エンコードされた文字列

    Returns:
        str: デコードされた文字列
    """
    return base64.b64decode(b64str).decode('utf-8')
