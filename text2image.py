#!/usr/bin/env python3
"""
阿里百炼文生图 - 直接运行生成图片
用户友好的命令行工具
支持文件输入和批量处理
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.image import Text2ImageGenerator
from src.utils.file_utils import PromptFileReader


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
  python text2image.py "一只可爱的猫咪"
  python text2image.py -f prompts.txt
  python text2image.py -f prompts.json --output ./images
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
    
    parser.add_argument(
        "-m", "--model",
        choices=["qwen-image", "wan2.2-t2i-flash", "wan2.2-t2i-plus", "wanx2.1-t2i-turbo", "wanx2.1-t2i-plus", "wanx2.0-t2i-turbo"],
        default="wan2.2-t2i-flash",
        help="模型选择 (默认: wan2.2-t2i-flash)"
    )
    
    parser.add_argument(
        "-s", "--size",
        default="1024*1024",
        help="图像尺寸 (万相: 512-1440像素任意组合, 千问: 1328*1328/1664*928/1472*1140/1140*1472/928*1664)"
    )
    
    parser.add_argument(
        "-n", "--n",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="生成图片数量 (仅万相模型支持1-4张, 千问模型仅支持1张)"
    )
    
    parser.add_argument(
        "-S", "--seed",
        type=int,
        help="随机种子，用于控制生成内容的随机性"
    )
    
    parser.add_argument(
        "-N", "--negative",
        default="",
        help="反向提示词（不希望在图像中出现的内容）"
    )
    
    parser.add_argument(
        "-k", "--api-key",
        help="阿里云百炼API密钥（可选，也可通过环境变量设置）"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./output/images/generated",
        help="输出目录 (默认: ./generated_images)"
    )
    
    parser.add_argument(
        "-w", "--watermark",
        action="store_true",
        help="添加水印标识"
    )
    
    parser.add_argument(
        "-x", "--no-extend",
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
        
        if args.file:
            return process_file_input(generator, args)
        else:
            return process_single_prompt(generator, args)
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


def get_model_short_name(model_name: str) -> str:
    """获取模型简称"""
    model_short_names = {
        "qwen-image": "qwen",
        "wan2.2-t2i-flash": "wan22f",
        "wan2.2-t2i-plus": "wan22p",
        "wanx2.1-t2i-turbo": "wan21t",
        "wanx2.1-t2i-plus": "wan21p",
        "wanx2.0-t2i-turbo": "wan20t"
    }
    return model_short_names.get(model_name, model_name)


def process_file_input(generator: Text2ImageGenerator, args) -> int:
    """统一处理文件输入"""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        return 1
    
    print(f"📄 从文件读取: {filepath}")
    
    try:
        prompts = PromptFileReader.read_prompt_file(str(filepath))
        
        if not prompts:
            print("❌ 文件中没有找到有效提示词")
            return 1
        
        # 构建配置列表
        configs = []
        
        if isinstance(prompts[0], dict):
            # JSON格式 - 使用完整配置
            configs = prompts
            print(f"🎯 找到 {len(configs)} 个JSON配置")
        else:
            # 文本格式 - 转换为统一配置
            for prompt in prompts:
                config = {
                    'prompt': prompt,
                    'negative_prompt': args.negative or None,
                    'size': args.size,
                    'prompt_extend': not args.no_extend,
                    'watermark': args.watermark,
                    'model': args.model,
                    'n': args.n,
                    'seed': args.seed
                }
                configs.append(config)
            print(f"🎯 找到 {len(configs)} 个文本提示词")
        
        # 统一处理所有配置
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        for i, config in enumerate(configs, 1):
            prompt_text = config.get('prompt', '')
            print(f"\n[{i}/{len(configs)}] 处理: {prompt_text[:60]}...")
            
            try:
                validated_config = PromptFileReader.validate_prompt_config(config)
                result = generator.generate_image(**validated_config)
                
                if result.task_status.value == "SUCCEEDED" and result.results:
                    image = result.results[0]
                    
                    # 获取模型简称
                    model_short = get_model_short_name(validated_config.get('model', 'wan2.2-t2i-flash'))
                    
                    # 确定文件名
                    if config.get('filename'):
                        filename = config['filename']
                        # 为用户指定的文件名添加模型前缀
                        name_without_ext = Path(filename).stem
                        ext = Path(filename).suffix or '.png'
                        filename = f"{i}_{model_short}_{name_without_ext}{ext}"
                    else:
                        safe_name = "".join(c for c in prompt_text[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_name = safe_name.replace(' ', '_') or f"prompt_{i}"
                        filename = f"{i}_{model_short}_{safe_name}.png"
                    
                    file_path = generator.download_image_sync(
                        image.url,
                        str(output_dir),
                        filename
                    )
                    
                    print(f"✅ 成功: {filename}")
                    print(f"📁 保存路径: {file_path}")
                    print(f"🤖 使用模型: {validated_config.get('model', '未知')}")
                    print(f"📐 图片尺寸: {validated_config.get('size', '未知')}")
                    if image.actual_prompt:
                        print(f"📝 实际提示词: {image.actual_prompt}")
                    print(f"📋 原始提示词: {image.orig_prompt}")
                    success_count += 1
                else:
                    print(f"❌ 失败: {prompt_text}")
                    
            except Exception as e:
                print(f"❌ 任务 {i} 失败: {e}")
                continue
        
        print(f"\n📊 文件处理完成: {success_count}/{len(configs)} 成功")
        return 0 if success_count > 0 else 1
        
    except Exception as e:
        print(f"❌ 文件读取错误: {e}")
        return 1


def process_single_prompt(generator: Text2ImageGenerator, args) -> int:
    """处理单个提示词"""
    print(f"🚀 正在生成: {args.prompt}")
    if args.negative:
        print(f"🚫 反向提示: {args.negative}")
    
    # 验证千问模型的特殊限制
    if args.model == "qwen-image" and args.n != 1:
        print("⚠️ 千问模型仅支持生成1张图片，已自动调整为1")
        args.n = 1
    
    result = generator.generate_image(
        prompt=args.prompt,
        negative_prompt=args.negative or None,
        size=args.size,
        model=args.model,
        prompt_extend=not args.no_extend,
        watermark=args.watermark,
        n=args.n,
        seed=args.seed
    )
    
    if result.task_status.value == "SUCCEEDED" and result.results:
        image = result.results[0]
        
        # 确保输出目录存在
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取模型简称
        model_short = get_model_short_name(args.model)
        
        # 确定文件名
        filename = args.filename
        if not filename:
            safe_name = "".join(c for c in args.prompt[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_') or "generated"
            filename = f"{model_short}_{safe_name}.png"
        else:
            # 如果用户指定了文件名，添加模型前缀
            name_without_ext = Path(filename).stem
            ext = Path(filename).suffix or '.png'
            filename = f"{model_short}_{name_without_ext}{ext}"
        
        file_path = generator.download_image_sync(
            image.url,
            str(output_dir),
            filename
        )
        
        print("\n✅ 生成成功！")
        print(f"📁 保存路径: {file_path}")
        print(f"🤖 使用模型: {args.model}")
        print(f"📐 图片尺寸: {args.size}")
        print(f"🌐 原始URL: {image.url}")
        print(f"⏱️  任务ID: {result.task_id}")
        if image.actual_prompt:
            print(f"📝 实际提示词: {image.actual_prompt}")
        print(f"📋 原始提示词: {image.orig_prompt}")
        
        return 0
    else:
        print(f"❌ 生成失败: {result.task_status}")
        return 1


if __name__ == "__main__":
    sys.exit(main())