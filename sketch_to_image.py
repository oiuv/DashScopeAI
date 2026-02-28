#!/usr/bin/env python3
"""
雪风AI涂鸦绘画命令行工具
使用通义万相-涂鸦作画模型的命令行工具
"""

import argparse
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.image.sketch_to_image import SketchToImageGenerator


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="雪风AI涂鸦绘画工具")
    parser.add_argument("sketch", help="草图文件路径")
    parser.add_argument("prompt", help="描述文字，≤75字符")
    parser.add_argument("--style", choices=[
        "auto", "3d_cartoon", "anime", "oil_painting", 
        "watercolor", "sketch", "chinese_painting", "flat_illustration"
    ], default="auto", help="绘画风格，默认为自动随机选择")
    parser.add_argument("--size", choices=["768*768"], default="768*768", 
                       help="输出尺寸，目前仅支持768×768")
    parser.add_argument("--n", type=int, choices=[1, 2, 3, 4], default=1, help="生成数量")
    parser.add_argument("--weight", type=int, choices=range(0, 11), default=5, 
                       help="草图权重，0-10")
    parser.add_argument("--output", default="./output/images/sketched", help="输出目录 (默认：./output/images/sketched)")
    parser.add_argument("--api-key", help="API密钥")
    parser.add_argument("--wait", action="store_true", help="等待完成")
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("错误: 请设置API密钥或DASHSCOPE_API_KEY环境变量")
        return 1
    
    # 检查文件
    if not os.path.exists(args.sketch):
        print(f"错误: 草图文件不存在: {args.sketch}")
        return 1
    
    # 初始化生成器
    generator = SketchToImageGenerator(api_key)
    
    # 映射风格
    style_map = {
        "auto": "<auto>",
        "3d_cartoon": "<3d cartoon>",
        "anime": "<anime>",
        "oil_painting": "<oil painting>",
        "watercolor": "<watercolor>",
        "sketch": "<sketch>",
        "chinese_painting": "<chinese painting>",
        "flat_illustration": "<flat illustration>"
    }
    
    print("🎨 雪风AI涂鸦绘画工具")
    print(f"草图: {args.sketch}")
    print(f"描述: {args.prompt}")
    print(f"风格: {args.style}")
    print(f"尺寸: {args.size}")
    
    try:
        if args.wait:
            # 等待完成模式
            result = generator.generate_and_wait(
                sketch_path=args.sketch,
                prompt=args.prompt,
                style=style_map[args.style],
                size=args.size,
                n=args.n,
                sketch_weight=args.weight,
                max_wait_time=300
            )
            
            if result.task_status == "SUCCEEDED":
                print(f"✅ 生成成功! 共{len(result.image_urls)}张图片")
                for i, url in enumerate(result.image_urls):
                    print(f"图片{i+1}: {url}")
                return 0
            else:
                print(f"❌ 生成失败: {result.error_message}")
                return 1
        else:
            # 异步模式
            result = generator.generate_from_file(
                sketch_path=args.sketch,
                prompt=args.prompt,
                style=style_map[args.style],
                size=args.size,
                n=args.n,
                sketch_weight=args.weight
            )
            
            if result.task_status == "FAILED":
                print(f"❌ 创建任务失败: {result.error_message}")
                return 1
            
            print(f"✅ 任务已创建: {result.task_id}")
            print(f"使用以下命令查询结果:")
            print(f"python sketch_to_image.py --task-id {result.task_id}")
            return 0
            
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())