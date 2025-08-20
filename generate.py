#!/usr/bin/env python3
"""
阿里百炼文生图 - 直接运行生成图片
用户友好的命令行工具
支持文件输入和批量处理
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.image import Text2ImageGenerator
from src.utils.file_utils import PromptFileReader, BatchProcessor


def check_api_key():
    """检查API密钥"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未找到API密钥")
        print("请设置环境变量 DASHSCOPE_API_KEY")
        print("Windows: set DASHSCOPE_API_KEY=你的密钥")
        print("Linux/Mac: export DASHSCOPE_API_KEY=你的密钥")
        print("或者使用 --api-key 参数")
        return False
    return True


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🎨 阿里百炼文生图工具")
    print("阿里云百炼大模型 - 文本生成图像")
    print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="阿里云百炼文生图工具 - 直接生成图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python generate.py "一只可爱的猫咪"
  python generate.py "山水画" --size 1472*1140 --negative "模糊"
  python generate.py "科幻城市" --api-key sk-xxx --output ./images
        """
    )
    
    # 输入方式组
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "prompt",
        nargs='?',
        help="生成图像的文本描述"
    )
    input_group.add_argument(
        "-f", "--file",
        help="从文件读取提示词（支持.txt和.json格式）"
    )
    input_group.add_argument(
        "-b", "--batch",
        help="批量处理模式，从JSON文件读取多个提示词配置"
    )
    
    parser.add_argument(
        "--size",
        choices=["1328*1328", "1664*928", "1472*1140", "1140*1472", "928*1664"],
        default="1328*1328",
        help="图像尺寸 (默认: 1328*1328)"
    )
    
    parser.add_argument(
        "--negative",
        default="",
        help="反向提示词（不希望在图像中出现的内容）"
    )
    
    parser.add_argument(
        "--api-key",
        help="阿里云百炼API密钥（可选，也可通过环境变量设置）"
    )
    
    parser.add_argument(
        "--output",
        default="./generated_images",
        help="输出目录 (默认: ./generated_images)"
    )
    
    parser.add_argument(
        "--no-watermark",
        action="store_true",
        help="不添加水印"
    )
    
    parser.add_argument(
        "--no-extend",
        action="store_true",
        help="不开启智能提示词改写"
    )
    
    parser.add_argument(
        "--filename",
        help="输出文件名（可选，默认自动生成）"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # 检查API密钥
    api_key = args.api_key or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        check_api_key()
        return 1
    
    try:
        generator = Text2ImageGenerator(api_key=api_key)
        
        # 根据输入方式处理
        if args.file:
            return process_single_file(generator, args)
        elif args.batch:
            return process_batch_file(generator, args)
        else:
            return process_single_prompt(generator, args)
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


def process_single_prompt(generator: Text2ImageGenerator, args) -> int:
    """处理单个提示词"""
    print(f"🚀 正在生成: {args.prompt}")
    print(f"📏 尺寸: {args.size}")
    if args.negative:
        print(f"🚫 反向提示: {args.negative}")
    
    result = generator.generate_image(
        prompt=args.prompt,
        negative_prompt=args.negative or None,
        size=args.size,
        prompt_extend=not args.no_extend,
        watermark=not args.no_watermark
    )
    
    return handle_single_result(result, args, generator=generator)


def process_single_file(generator: Text2ImageGenerator, args) -> int:
    """处理单个文件"""
    filepath = args.file
    print(f"📄 从文件读取: {filepath}")
    
    try:
        prompts = PromptFileReader.read_prompt_file(filepath)
        
        if isinstance(prompts, list) and len(prompts) > 0:
            if isinstance(prompts[0], dict):
                # JSON格式，结构化配置
                config = PromptFileReader.validate_prompt_config(prompts[0])
                print(f"🎯 使用JSON配置: {config['prompt'][:50]}...")
                
                result = generator.generate_image(**config)
                return handle_single_result(result, args, config.get('filename'), generator)
            else:
                # 文本格式，使用第一个提示词
                prompt = prompts[0]
                print(f"🎯 使用文本提示: {prompt}")
                
                result = generator.generate_image(
                    prompt=prompt,
                    negative_prompt=args.negative or None,
                    size=args.size,
                    prompt_extend=not args.no_extend,
                    watermark=not args.no_watermark
                )
                return handle_single_result(result, args, generator=generator)
        else:
            print("❌ 文件中没有找到有效提示词")
            return 1
            
    except Exception as e:
        print(f"❌ 文件读取错误: {e}")
        return 1


def process_batch_file(generator: Text2ImageGenerator, args) -> int:
    """处理批量文件"""
    filepath = args.batch
    print(f"📁 批量处理模式: {filepath}")
    
    try:
        configs = PromptFileReader.read_json_file(filepath)
        print(f"🎯 找到 {len(configs)} 个生成任务")
        
        # 确保输出目录存在
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        for i, config in enumerate(configs, 1):
            print(f"\n[{i}/{len(configs)}] 正在生成...")
            
            try:
                validated_config = PromptFileReader.validate_prompt_config(config)
                
                result = generator.generate_image(**validated_config)
                
                if result.task_status.value == "SUCCEEDED" and result.results:
                    image = result.results[0]
                    filename = validated_config.get('filename') or f"batch_{i}.png"
                    
                    file_path = generator.download_image_sync(
                        image.url,
                        str(output_dir),
                        filename
                    )
                    
                    print(f"✅ 成功: {filename}")
                    success_count += 1
                else:
                    print(f"❌ 失败: {validated_config.get('prompt', '')[:50]}...")
                    
            except Exception as e:
                print(f"❌ 任务 {i} 失败: {e}")
                continue
        
        print(f"\n📊 批量完成: {success_count}/{len(configs)} 成功")
        return 0 if success_count > 0 else 1
        
    except Exception as e:
        print(f"❌ 批量处理错误: {e}")
        return 1


def handle_single_result(result, args, custom_filename: Optional[str] = None, generator=None) -> int:
    """处理单个生成结果"""
    if result.task_status.value == "SUCCEEDED" and result.results:
        image = result.results[0]
        
        # 确保输出目录存在
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载图像
        filename = custom_filename or args.filename
        file_path = generator.download_image_sync(
            image.url,
            str(output_dir),
            filename
        )
        
        print("\n✅ 生成成功！")
        print(f"📁 保存路径: {file_path}")
        print(f"🌐 原始URL: {image.url}")
        print(f"⏱️  任务ID: {result.task_id}")
        
        return 0
    else:
        print(f"❌ 生成失败: {result.task_status}")
        return 1


if __name__ == "__main__":
    sys.exit(main())