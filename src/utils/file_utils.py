"""
文件处理工具
支持从文件读取提示词、批量处理等功能
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union


class PromptFileReader:
    """提示词文件读取器"""
    
    @staticmethod
    def read_text_file(filepath: str) -> List[str]:
        """
        从文本文件读取提示词
        
        支持格式：
        - 每行一个提示词
        - 空行会被忽略
        - 以#开头的行作为注释
        
        Args:
            filepath: 文本文件路径
            
        Returns:
            List[str]: 提示词列表
            
        Raises:
            FileNotFoundError: 文件不存在
            IOError: 读取文件失败
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        prompts = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释行
                    if line and not line.startswith('#'):
                        prompts.append(line)
        except Exception as e:
            raise IOError(f"读取文件失败: {e}")
        
        return prompts
    
    @staticmethod
    def read_json_file(filepath: str) -> List[Dict[str, Any]]:
        """
        从JSON文件读取结构化提示词
        
        支持格式：
        {
            "prompts": [
                {
                    "prompt": "文本提示词",
                    "negative": "反向提示词",
                    "size": "1328*1328",
                    "watermark": false,
                    "filename": "output.png"
                }
            ]
        }
        
        Args:
            filepath: JSON文件路径
            
        Returns:
            List[Dict]: 结构化提示词配置列表
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or 'prompts' not in data:
                raise ValueError("JSON格式错误：需要包含'prompts'键")
            
            prompts = data['prompts']
            if not isinstance(prompts, list):
                raise ValueError("'prompts'必须是数组")
            
            return prompts
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON格式错误: {e}", e.doc, e.pos)
    
    @staticmethod
    def read_prompt_file(filepath: str) -> Union[List[str], List[Dict[str, Any]]]:
        """
        智能读取提示词文件
        
        根据文件扩展名自动选择读取方式
        
        Args:
            filepath: 文件路径
            
        Returns:
            Union[List[str], List[Dict]]: 提示词列表或结构化配置列表
        """
        filepath = Path(filepath)
        
        if filepath.suffix.lower() == '.json':
            return PromptFileReader.read_json_file(str(filepath))
        elif filepath.suffix.lower() in ['.txt', '.text']:
            return PromptFileReader.read_text_file(str(filepath))
        else:
            # 默认尝试按文本读取
            return PromptFileReader.read_text_file(str(filepath))
    
    @staticmethod
    def validate_prompt_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证提示词配置
        
        Args:
            config: 配置字典
            
        Returns:
            Dict[str, Any]: 验证后的配置
        """
        validated = {
            'prompt': str(config.get('prompt', '')),
            'negative_prompt': str(config.get('negative', config.get('negative_prompt', ''))),
            'size': str(config.get('size', '1328*1328')),
            'watermark': bool(config.get('watermark', False)),
            'prompt_extend': bool(config.get('prompt_extend', config.get('extend', True))),
            'model': str(config.get('model', 'wan2.2-t2i-flash')),
            'n': int(config.get('n', 1)),
            'seed': int(config.get('seed', 0)) if config.get('seed') else None,
            'filename': str(config.get('filename', '')) if config.get('filename') else None
        }
        
        # 验证模型特定参数
        model = validated['model']
        if model == 'qwen-image':
            # 千问模型限制
            validated['n'] = 1  # 只支持1张
            validated['seed'] = None  # 不支持seed参数
        else:
            # 万相模型限制
            if validated['n'] > 4:
                validated['n'] = 4
            elif validated['n'] < 1:
                validated['n'] = 1
        
        # 验证size - 根据模型选择有效尺寸范围
        model = validated.get('model', 'wan2.2-t2i-flash')
        if model == 'qwen-image':
            valid_sizes = ['1328*1328', '1664*928', '1472*1140', '1140*1472', '928*1664']
            if validated['size'] not in valid_sizes:
                validated['size'] = '1328*1328'
        else:
            # 万相模型支持512-1440范围内的任意尺寸
            size_str = validated['size']
            try:
                width, height = map(int, size_str.split('*'))
                if not (512 <= width <= 1440 and 512 <= height <= 1440 and width * height <= 2000000):
                    validated['size'] = '1024*1024'  # 万相默认尺寸
            except (ValueError, IndexError):
                validated['size'] = '1024*1024'
        
        return validated


class BatchProcessor:
    """批量处理器"""
    
    @staticmethod
    def create_batch_config(
        prompts: List[str],
        output_dir: str = "./batch_output",
        **common_params
    ) -> List[Dict[str, Any]]:
        """
        创建批量配置
        
        Args:
            prompts: 提示词列表
            output_dir: 输出目录
            **common_params: 公共参数
            
        Returns:
            List[Dict]: 批量配置列表
        """
        configs = []
        for i, prompt in enumerate(prompts):
            config = {
                'prompt': prompt,
                **common_params
            }
            
            # 自动生成文件名
            if not config.get('filename'):
                safe_name = "".join(c for c in prompt[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                config['filename'] = f"batch_{i+1}_{safe_name}.png"
            
            configs.append(config)
        
        return configs
    
    @staticmethod
    def save_batch_config(configs: List[Dict[str, Any]], filepath: str):
        """
        保存批量配置到JSON文件
        
        Args:
            configs: 配置列表
            filepath: 保存路径
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'prompts': configs}, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_batch_config(filepath: str) -> List[Dict[str, Any]]:
        """
        从文件加载批量配置
        
        Args:
            filepath: 配置文件路径
            
        Returns:
            List[Dict]: 配置列表
        """
        return PromptFileReader.read_json_file(filepath)