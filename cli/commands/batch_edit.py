#!/usr/bin/env python3
"""
批量图像编辑子命令
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.image import ImageEditor
from cli.shared import (
    check_api_key,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_warning
)


def add_arguments(parser):
    """添加子命令参数"""
    parser.add_argument(
        "config_file",
        help="配置文件路径 (JSON 格式)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="阿里云百炼 API 密钥"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出目录 (可选，配置文件中的设置优先)"
    )
    parser.add_argument(
        "-s", "--start",
        type=int,
        default=1,
        help="起始创作编号 (默认：1)"
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


def execute(args):
    """执行子命令"""
    # 检查 API 密钥
    if not check_api_key(args.api_key):
        return 1

    # 加载配置
    config = load_config(args.config_file)

    # 获取基本信息
    base_image = config.get('base_image') or config.get('image')

    output_dir = args.output or config.get('output_directory', './batch_output')
    creations = config.get('creations', [])

    if not creations:
        print_error("配置文件中缺少 creations 字段或为空")
        return 1

    # 过滤创作范围
    start_idx = max(0, args.start - 1)
    end_idx = args.end if args.end else len(creations)
    creations_to_process = creations[start_idx:end_idx]

    if not creations_to_process:
        print_error("没有符合条件的创作")
        return 1

    print_banner(
        f"{config.get('project_name', '批量图像编辑')} - 批量处理开始",
        f"总计：{len(creations)} | 本次：{len(creations_to_process)} | 输出：{output_dir}"
    )

    if args.dry_run:
        print_info("试运行模式 - 仅显示计划")
        for creation in creations_to_process:
            filename = creation.get('filename', f"creation_{creation.get('id', 'unknown')}.png")
            print(f"  📋 将处理：{creation['name']} -> {filename}")
        return 0

    # 初始化编辑器
    try:
        editor = ImageEditor(api_key=args.api_key)
    except Exception as e:
        print_error(f"初始化失败：{e}")
        return 1

    # 处理创作
    success_count = 0
    total_count = len(creations_to_process)

    # 显示图片统计
    unique_images = set(creation.get('image', base_image) for creation in creations_to_process)
    print_info(f"涉及图片：{len(unique_images)}张")

    for creation in creations_to_process:
        if process_single_creation(editor, creation, base_image, output_dir):
            success_count += 1

    print("=" * 60)
    print(f"✅ 完成！成功：{success_count}/{total_count}")
    print("=" * 60)
    return 0


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"配置文件不存在：{config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print_error(f"配置文件格式错误：{e}")
        sys.exit(1)


def process_single_creation(editor: ImageEditor, creation: Dict[str, Any], default_image: str, output_dir: str) -> bool:
    """处理单个创作"""
    try:
        print_info(f"正在处理：{creation['name']}")

        # 构建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 获取模型
        model = creation.get('model', 'qwen-image-edit')

        # 获取图像 URL（优先使用 creation 中的 image，其次使用 base_image）
        image_url = creation.get('image', default_image)
        if not image_url:
            print_error(f"{creation['name']} 缺少 image 字段")
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
            if creation.get('mask_image'):
                params['mask_image_url'] = creation['mask_image']

        # 执行编辑
        result = editor.edit_image(**params)

        # 获取结果 URL
        if model == 'qwen-image-edit':
            edited_url = result.url
        else:
            if result.results and result.results[0]:
                edited_url = result.results[0].url
            else:
                print_error(f"{creation['name']} 处理失败：未获取到结果")
                return False

        # 下载图像
        filename = creation.get('filename', f"creation_{creation['id']}.png")
        file_path = editor.download_image(edited_url, str(output_path), filename)

        print_success(f"{creation['name']} 完成：{file_path}")
        return True

    except Exception as e:
        print_error(f"{creation['name']} 处理失败：{e}")
        return False
