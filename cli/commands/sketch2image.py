#!/usr/bin/env python3
"""
涂鸦作画子命令
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.image.sketch_to_image import SketchToImageGenerator
from cli.shared import (
    check_api_key,
    print_banner,
    print_success,
    print_error,
    print_info,
    validate_file_exists
)


def add_arguments(parser):
    """添加子命令参数"""
    parser.add_argument(
        "sketch",
        help="草图文件路径"
    )
    parser.add_argument(
        "prompt",
        help="描述文字，≤75 字符"
    )
    parser.add_argument(
        "--style",
        choices=[
            "auto", "3d_cartoon", "anime", "oil_painting",
            "watercolor", "sketch", "chinese_painting", "flat_illustration"
        ],
        default="auto",
        help="绘画风格，默认为自动随机选择"
    )
    parser.add_argument(
        "--size",
        choices=["768*768"],
        default="768*768",
        help="输出尺寸，目前仅支持 768×768"
    )
    parser.add_argument(
        "--n",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="生成数量"
    )
    parser.add_argument(
        "--weight",
        type=int,
        choices=range(0, 11),
        default=5,
        help="草图权重，0-10"
    )
    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="输出目录"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="API 密钥"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="等待完成"
    )


def execute(args):
    """执行子命令"""
    print_banner("雪风 AI 涂鸦绘画工具", "根据草图和文本描述生成精美图像")

    # 获取 API 密钥
    if not check_api_key(args.api_key):
        return 1

    # 检查文件
    try:
        validate_file_exists(args.sketch, ['.jpg', '.jpeg', '.png', '.bmp', '.webp'])
    except (FileNotFoundError, ValueError) as e:
        print_error(str(e))
        return 1

    # 初始化生成器
    generator = SketchToImageGenerator(args.api_key)

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

    print_info(f"草图：{args.sketch}")
    print_info(f"描述：{args.prompt}")
    print_info(f"风格：{args.style}")
    print_info(f"尺寸：{args.size}")

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
                print_success(f"生成成功！共 {len(result.image_urls)} 张图片")
                for i, url in enumerate(result.image_urls):
                    print_info(f"图片{i + 1}: {url}")

                # 下载图片
                output_dir = Path(args.output)
                output_dir.mkdir(parents=True, exist_ok=True)

                for i, url in enumerate(result.image_urls, 1):
                    filename = f"sketch_{args.style}_{i}.png"
                    file_path = generator.download_image(url, str(output_dir), filename)
                    print_success(f"已保存：{file_path}")

                return 0
            else:
                print_error(f"生成失败：{result.error_message}")
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
                print_error(f"创建任务失败：{result.error_message}")
                return 1

            print_success(f"任务已创建：{result.task_id}")
            print_info("使用以下命令查询结果:")
            print_info(f"python -m cli sketch2image {args.sketch} \"{args.prompt}\" --task-id {result.task_id} --wait")
            return 0

    except Exception as e:
        print_error(f"执行失败：{str(e)}")
        return 1
