"""
CLI 参数验证工具
"""

import os
from pathlib import Path
from typing import Optional


def validate_image_path(image_path: str, allow_url: bool = True) -> str:
    """
    验证图像路径并返回 URL/Base64 格式

    Args:
        image_path: 图像路径或 URL
        allow_url: 是否允许 URL 格式

    Returns:
        str: 验证后的路径/URL

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的格式
    """
    # 检查是否为 URL
    if image_path.startswith(('http://', 'https://')):
        if allow_url:
            return image_path
        else:
            raise ValueError("不支持 URL 格式，请提供本地文件路径")

    # 检查本地文件
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图像文件不存在：{image_path}")

    # 验证文件格式
    ext = path.suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
        raise ValueError(f"不支持的图像格式：{ext}")

    return str(path)


def validate_file_exists(file_path: str, extensions: Optional[list] = None) -> str:
    """
    验证文件是否存在

    Args:
        file_path: 文件路径
        extensions: 允许的扩展名列表

    Returns:
        str: 验证后的文件路径

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的格式
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    if extensions:
        ext = path.suffix.lower()
        if ext not in extensions:
            raise ValueError(f"不支持的文件格式：{ext}，允许的格式：{extensions}")

    return str(path)


def validate_positive_int(value: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """
    验证正整数

    Args:
        value: 待验证的值
        min_val: 最小值
        max_val: 最大值

    Returns:
        int: 验证后的值

    Raises:
        ValueError: 验证失败
    """
    if value < 0:
        raise ValueError(f"值不能为负数：{value}")

    if min_val is not None and value < min_val:
        raise ValueError(f"值不能小于 {min_val}: {value}")

    if max_val is not None and value > max_val:
        raise ValueError(f"值不能大于 {max_val}: {value}")

    return value


def validate_size_format(size: str, model: str = None) -> str:
    """
    验证图像尺寸格式

    Args:
        size: 尺寸字符串，如 "1024*1024"
        model: 模型名称（用于特定模型验证）

    Returns:
        str: 验证后的尺寸

    Raises:
        ValueError: 格式错误
    """
    if '*' not in size:
        raise ValueError(f"尺寸格式错误，应为 '宽*高' 格式：{size}")

    parts = size.split('*')
    if len(parts) != 2:
        raise ValueError(f"尺寸格式错误，应为 '宽*高' 格式：{size}")

    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError:
        raise ValueError(f"尺寸必须为整数：{size}")

    # 千问模型的特殊尺寸验证
    if model == "qwen-image":
        valid_sizes = ["1328*1328", "1664*928", "1472*1140", "1140*1472", "928*1664"]
        if size not in valid_sizes:
            raise ValueError(f"千问模型仅支持以下尺寸：{', '.join(valid_sizes)}")
    else:
        # 万相模型：512-1440 像素
        if not (512 <= width <= 1440 and 512 <= height <= 1440):
            raise ValueError(f"万相模型尺寸范围：512-1440 像素")

        # 最大 200 万像素
        if width * height > 2000000:
            raise ValueError("万相模型最大支持 200 万像素")

    return size
