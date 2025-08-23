"""
统一GUI工具配置管理模块
为所有GUI工具提供共享的配置管理功能
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ToolsConfig:
    """统一配置管理类"""
    
    CONFIG_FILE = "tools_config.json"
    
    def __init__(self):
        self.config_path = Path(__file__).parent / self.CONFIG_FILE
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "api_key": "",
            "output_dir": "./output",
            "default_model": "qwen-image",
            "tools": {
                "poster_generator": {
                    "default_size": "1328×1328 (正方形)",
                    "default_negative": "低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良",
                    "polling": {
                        "max_attempts": 120,
                        "initial_delay": 2,
                        "max_delay": 10,
                        "timeout": 15
                    }
                },
                "watermark_remover": {
                    "model": "qwen-image-edit"
                },
                "sketch_to_image": {
                    "model": "wanx-sketch-to-image-lite",
                    "default_style": "自动",
                    "default_size": "768×768 (正方形)",
                    "default_n": 1,
                    "default_weight": 5
                }
            }
        }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @property
    def api_key(self) -> str:
        """获取API密钥"""
        return self.get("api_key", "")
    
    @api_key.setter
    def api_key(self, value: str):
        """设置API密钥"""
        self.set("api_key", value)
    
    @property
    def output_dir(self) -> str:
        """获取输出目录"""
        return self.get("output_dir", "./output")
    
    @output_dir.setter
    def output_dir(self, value: str):
        """设置输出目录"""
        self.set("output_dir", value)
    
    def get_tool_config(self, tool_name: str, key: str = None, default: Any = None) -> Any:
        """获取特定工具的配置"""
        if key:
            return self.get(f"tools.{tool_name}.{key}", default)
        return self.get(f"tools.{tool_name}", {})
    
    def set_tool_config(self, tool_name: str, key: str, value: Any):
        """设置特定工具的配置"""
        self.set(f"tools.{tool_name}.{key}", value)

# 创建全局配置实例
config = ToolsConfig()