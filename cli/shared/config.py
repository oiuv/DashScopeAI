"""
CLI 配置和共享参数定义
"""

import os
from typing import Optional, Dict, Any


def get_api_key(cli_arg: Optional[str] = None) -> Optional[str]:
    """
    获取 API 密钥，优先级：CLI 参数 > 环境变量

    Args:
        cli_arg: CLI 传入的 API 密钥

    Returns:
        API 密钥或 None
    """
    return cli_arg or os.getenv("DASHSCOPE_API_KEY")


def check_api_key(api_key: Optional[str] = None) -> bool:
    """
    检查 API 密钥是否有效

    Args:
        api_key: API 密钥

    Returns:
        bool: 是否有效
    """
    key = get_api_key(api_key)
    if not key:
        print("❌ 错误：未找到 API 密钥")
        print("请设置环境变量 DASHSCOPE_API_KEY")
        print("Windows: set DASHSCOPE_API_KEY=你的密钥")
        print("Linux/Mac: export DASHSCOPE_API_KEY=你的密钥")
        print("或者使用 --api-key/-k 参数")
        return False
    return True


# 共享参数定义
COMMON_ARGS = {
    'api_key': {
        'args': ['-k', '--api-key'],
        'kwargs': {
            'help': '阿里云百炼 API 密钥（可选，也可通过环境变量 DASHSCOPE_API_KEY 设置）',
            'dest': 'api_key'
        }
    },
    'output': {
        'args': ['-o', '--output'],
        'kwargs': {
            'default': './output',
            'help': '输出目录 (默认：./output)',
            'dest': 'output'
        }
    },
    'verbose': {
        'args': ['-v', '--verbose'],
        'kwargs': {
            'action': 'store_true',
            'help': '显示详细信息',
            'dest': 'verbose'
        }
    },
    'watermark': {
        'args': ['-w', '--watermark'],
        'kwargs': {
            'action': 'store_true',
            'help': '添加水印标识',
            'dest': 'watermark'
        }
    },
    'filename': {
        'args': ['--filename',],
        'kwargs': {
            'help': '输出文件名（可选，默认自动生成）',
            'dest': 'filename'
        }
    }
}


# 模型简称映射
MODEL_SHORT_NAMES: Dict[str, str] = {
    # 文生图模型
    "qwen-image": "qwen",
    "wan2.2-t2i-flash": "wan22f",
    "wan2.2-t2i-plus": "wan22p",
    "wanx2.1-t2i-turbo": "wan21t",
    "wanx2.1-t2i-plus": "wan21p",
    "wanx2.0-t2i-turbo": "wan20t",
    # 图像编辑模型
    "qwen-image-edit": "qwen_edit",
    "wanx2.1-imageedit": "wanx_edit",
    # 涂鸦作画
    "wanx2.1-t2i-sketch": "sketch",
    # 风格重绘
    "style_repaint": "style_repaint",
}


def get_model_short_name(model_name: str) -> str:
    """获取模型简称"""
    return MODEL_SHORT_NAMES.get(model_name, model_name.replace('.', '_').replace('-', '_'))
