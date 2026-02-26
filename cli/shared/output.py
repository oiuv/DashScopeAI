"""
CLI 输出格式化工具
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


def print_banner(title: str, subtitle: str = "", width: int = 60):
    """
    打印欢迎横幅

    Args:
        title: 主标题
        subtitle: 副标题
        width: 横幅宽度
    """
    print("=" * width)
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * width)


def print_success(message: str):
    """打印成功消息"""
    print(f"✅ {message}")


def print_error(message: str):
    """打印错误消息"""
    print(f"❌ {message}")


def print_warning(message: str):
    """打印警告消息"""
    print(f"⚠️  {message}")


def print_info(message: str):
    """打印信息消息"""
    print(f"📋 {message}")


def print_progress(current: int, total: int, prefix: str = ""):
    """
    打印进度信息

    Args:
        current: 当前进度
        total: 总进度
        prefix: 前缀文本
    """
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\r{prefix}[{bar}] {current}/{total} ({percentage:.1f}%)", end='', flush=True)
    if current == total:
        print()  # 完成后换行


class OutputManager:
    """输出管理器"""

    def __init__(self, output_dir: str, create: bool = True):
        """
        初始化输出管理器

        Args:
            output_dir: 输出目录
            create: 是否自动创建目录
        """
        self.output_dir = Path(output_dir)
        if create:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_filename(
        self,
        model_short: str,
        prefix: str = "",
        ext: str = ".png",
        timestamp: bool = True
    ) -> str:
        """
        生成文件名

        Args:
            model_short: 模型简称
            prefix: 文件名前缀
            ext: 文件扩展名
            timestamp: 是否添加时间戳

        Returns:
            str: 生成的文件名
        """
        parts = []
        if prefix:
            parts.append(prefix)
        parts.append(model_short)
        if timestamp:
            parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

        return "_".join(parts) + ext

    def save_result(
        self,
        result: Dict[str, Any],
        filename: Optional[str] = None,
        subdir: Optional[str] = None
    ) -> str:
        """
        保存结果信息为 JSON

        Args:
            result: 结果字典
            filename: 文件名（不含扩展名）
            subdir: 子目录

        Returns:
            str: 保存的文件路径
        """
        if subdir:
            save_dir = self.output_dir / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.output_dir

        if not filename:
            filename = f"result_{int(time.time())}"

        file_path = save_dir / f"{filename}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return str(file_path)

    def file_exists(self, filename: str) -> bool:
        """检查文件是否已存在"""
        return (self.output_dir / filename).exists()
