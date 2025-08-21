#!/usr/bin/env python3
"""
批量图像编辑工具 - 支持配置文件批量处理
支持千问图像编辑和万相图像编辑模型
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.image import ImageEditor
from src.image.models import ModelType


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        sys.exit(1)


def process_single_creation(editor: ImageEditor, creation: Dict[str, Any], default_image: str, output_dir: str) -> bool:
    """处理单个创作"""
    try:
        print(f"🎨 正在处理: {creation['name']}")
        
        # 构建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取模型
        model = creation.get('model', 'qwen-image-edit')
        
        # 获取图像URL（优先使用creation中的image，其次使用base_image）
        image_url = creation.get('image', default_image)
        if not image_url:
            print(f"❌ {creation['name']} 缺少image字段")
            return False
        
        # 构建参数
        params = {
            'model': model,
            'image_url': image_url,
            'prompt': creation['prompt'],
            'watermark': creation.get('watermark', False)
        }
        
        # 添加千问模型的反向提示词
        if model == 'qwen-image-edit' and creation.get('negative_prompt'):
            params['negative_prompt'] = creation['negative_prompt']
        
        # 添加万相模型的功能参数
        if model == 'wanx2.1-imageedit' and creation.get('function'):
            params['function'] = creation['function']
            if creation.get('strength') is not None:
                params['strength'] = creation['strength']
            if creation.get('upscale_factor') is not None:
                params['upscale_factor'] = creation['upscale_factor']
            if creation.get('is_sketch') is not None:
                params['is_sketch'] = creation['is_sketch']
            if creation.get('top_scale') is not None:
                params['top_scale'] = creation['top_scale']
                params['bottom_scale'] = creation.get('bottom_scale', 1.0)
                params['left_scale'] = creation.get('left_scale', 1.0)
                params['right_scale'] = creation.get('right_scale', 1.0)
        
        # 执行编辑
        result = editor.edit_image(**params)
        
        # 获取结果URL
        if model == 'qwen-image-edit':
            edited_url = result.url
        else:
            if result.results and result.results[0]:
                edited_url = result.results[0].url
            else:
                print(f"❌ {creation['name']} 处理失败：未获取到结果")
                return False
        
        # 下载图像
        filename = creation.get('filename', f"creation_{creation['id']}.png")
        file_path = editor.download_image(edited_url, str(output_path), filename)
        
        print(f"✅ {creation['name']} 完成: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ {creation['name']} 处理失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量图像编辑工具 - 支持配置文件批量处理")
    parser.add_argument(
        "config_file",
        help="配置文件路径 (JSON格式)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="阿里云百炼API密钥（可选，也可通过环境变量设置）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出目录 (可选，配置文件中的设置优先)"
    )
    parser.add_argument(
        "-s", "--start",
        type=int,
        default=1,
        help="起始创作编号 (默认: 1)"
    )
    parser.add_argument(
        "-e", "--end",
        type=int,
        help="结束创作编号 (可选)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，不实际处理图像"
    )
    
    args = parser.parse_args()
    
    # 检查API密钥
    api_key = args.api_key or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未找到API密钥")
        print("请设置环境变量 DASHSCOPE_API_KEY 或使用 -k 参数")
        sys.exit(1)
    
    # 加载配置
    config = load_config(args.config_file)
    
    # 获取基本信息
    base_image = config.get('base_image') or config.get('image')
    
    output_dir = args.output or config.get('output_directory', './batch_output')
    creations = config.get('creations', [])
    
    if not creations:
        print("❌ 错误：配置文件中缺少 creations 字段或为空")
        sys.exit(1)
    
    # 过滤创作范围
    start_idx = max(0, args.start - 1)
    end_idx = args.end if args.end else len(creations)
    creations_to_process = creations[start_idx:end_idx]
    
    if not creations_to_process:
        print("❌ 错误：没有符合条件的创作")
        sys.exit(1)
    
    print("=" * 60)
    project_name = config.get('project_name', '批量图像编辑')
    print(f"🐻 {project_name} - 批量处理开始")
    print("=" * 60)
    print(f"📊 总计创作: {len(creations)}")
    print(f"🎯 本次处理: {len(creations_to_process)} (创作 {args.start}-{end_idx})")
    print(f"🖼️  基础图片: {base_image}")
    print(f"📁 输出目录: {output_dir}")
    
    if args.dry_run:
        print("🔍 试运行模式 - 仅显示计划")
        for creation in creations_to_process:
            filename = creation.get('filename', f"creation_{creation.get('id', 'unknown')}.png")
            print(f"  📋 将处理: {creation['name']} -> {filename}")
        return
    
    # 初始化编辑器
    try:
        editor = ImageEditor(api_key=api_key)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    
    # 处理创作
    success_count = 0
    total_count = len(creations_to_process)
    
    # 显示图片统计
    unique_images = set(creation.get('image', base_image) for creation in creations_to_process)
    print(f"🖼️  涉及图片: {len(unique_images)}张")
    
    for creation in creations_to_process:
        if process_single_creation(editor, creation, base_image, output_dir):
            success_count += 1
    
    print("=" * 60)
    print(f"✅ 完成！成功: {success_count}/{total_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()