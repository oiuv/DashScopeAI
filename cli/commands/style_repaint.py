#!/usr/bin/env python3
"""
人像风格重绘子命令
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.image import StyleRepaintGenerator
from src.utils.file_utils import encode_file_to_base64
from cli.shared import (
    check_api_key,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_warning,
    validate_file_exists
)


def add_arguments(parser):
    """添加子命令参数"""
    # 主要参数
    parser.add_argument(
        "image",
        nargs="?",
        help="输入人物图像文件路径"
    )
    parser.add_argument(
        "style",
        nargs="?",
        type=int,
        help="预置风格编号"
    )

    # 可选参数
    parser.add_argument(
        "-r", "--style-ref",
        help="自定义风格参考图路径（与 style 参数互斥）"
    )
    parser.add_argument(
        "-o", "--output",
        default="./repainted_images",
        help="输出目录 (默认：./repainted_images)"
    )
    parser.add_argument(
        "-f", "--file",
        help="批量处理配置文件路径"
    )
    parser.add_argument(
        "-s", "--styles",
        action="store_true",
        help="显示可用风格列表"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=300,
        help="等待超时时间（秒）(默认：300)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="API 密钥"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )


def execute(args):
    """执行子命令"""
    print_banner(
        "阿里云百炼人像风格重绘工具",
        "将人像照片转换为不同艺术风格"
    )

    # 显示风格帮助
    if hasattr(args, 'styles') and args.styles:
        print_style_help()
        return 0

    # 检查 API 密钥
    if not check_api_key(args.api_key):
        return 1

    try:
        generator = StyleRepaintGenerator(api_key=args.api_key)

        # 批量处理模式
        if hasattr(args, 'file') and args.file:
            print_info(f"正在批量处理配置文件：{args.file}")
            return batch_process(generator, args.file, args.output, args.timeout, args.verbose)

        # 单文件处理模式
        if not args.image:
            print_error("必须指定图像文件路径或使用 -f 参数提供配置文件")
            print("使用 'python -m cli style-repaint --help' 查看详细用法")
            return 1

        # 验证参数
        if args.style is not None and args.style_ref:
            print_error("不能同时指定 style 和--style-ref 参数")
            return 1

        if args.style is None and not args.style_ref:
            print_error("必须指定 style 或--style-ref 参数之一")
            return 1

        # 处理图像
        image_path = validate_file_exists(args.image)

        print_info(f"开始处理：{image_path}")

        # 处理本地文件
        image_url = encode_file_to_base64(image_path)

        # 处理风格参数
        if args.style is not None:
            print_info(f"使用预置风格：{args.style}")
            result = generator.repaint_and_wait(
                image_url=image_url,
                style_index=args.style,
                timeout=args.timeout
            )
        else:
            style_ref_path = validate_file_exists(args.style_ref)
            style_ref_url = encode_file_to_base64(style_ref_path)
            print_info(f"使用自定义风格：{args.style_ref}")
            result = generator.repaint_and_wait(
                image_url=image_url,
                style_ref_url=style_ref_url,
                timeout=args.timeout
            )

        # 处理结果
        if result.results and result.results[0].url:
            output_url = result.results[0].url
            print_success("处理成功！")
            print_info(f"结果 URL: {output_url}")
            print_info(f"任务 ID: {result.task_id}")

            # 创建输出目录
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存结果信息
            result_info = {
                "task_id": result.task_id,
                "output_url": output_url,
                "input_image": args.image,
                "style": args.style if args.style is not None else "custom",
                "style_ref": args.style_ref
            }

            result_file = output_dir / f"result_{result.task_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_info, f, ensure_ascii=False, indent=2)

            print_info(f"结果信息已保存到：{result_file}")

            # 自动下载并保存图片
            saved_files = download_and_save_image(output_url, str(output_dir), args)
            print_success(f"图片已保存：{saved_files}")

            return 0
        else:
            print_error("未能获取生成结果")
            return 1

    except Exception as e:
        print_error(f"处理失败：{str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_style_help():
    """打印可用风格帮助信息"""
    styles = {
        0: "复古漫画",
        1: "3D 童话",
        2: "二次元",
        3: "小清新",
        4: "未来科技",
        5: "国画古风",
        6: "将军百战",
        7: "炫彩卡通",
        8: "清雅国风",
        9: "喜迎新年",
        14: "国风工笔",
        15: "恭贺新禧",
        30: "童话世界",
        31: "黏土世界",
        32: "像素世界",
        33: "冒险世界",
        34: "日漫世界",
        35: "3D 世界",
        36: "二次元世界",
        37: "手绘世界",
        38: "蜡笔世界",
        39: "冰箱贴世界",
        40: "吧唧世界"
    }

    print("\n可用的预置风格编号：")
    print("-" * 50)
    for index, name in styles.items():
        print(f"{index:>3}: {name}")
    print("-" * 50)
    print("使用自定义风格：设置 style_index=-1，并提供 style_ref_url")


def download_and_save_image(url: str, output_dir: str, args) -> str:
    """
    下载并保存图片

    Args:
        url: 图片 URL
        output_dir: 输出目录
        args: 命令行参数

    Returns:
        str: 保存的文件路径
    """
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        style_name = "style_" + str(args.style) if args.style is not None else "custom"
        filename = f"repaint_{style_name}_{timestamp}.jpg"
        file_path = output_path / filename

        # 下载图片
        print_info("正在下载图片...")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        # 保存图片
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return str(file_path)

    except Exception as e:
        print_error(f"下载图片失败：{str(e)}")
        return url  # 返回 URL 作为备选


def batch_process(generator: StyleRepaintGenerator, config_file: str, output_dir: str, timeout: int, verbose: bool) -> int:
    """批量处理"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            configs = json.load(f)

        if not isinstance(configs, dict) or 'tasks' not in configs:
            raise ValueError("配置文件格式错误：需要包含'tasks'键")

        base_image = configs.get('base_image')
        base_style_ref = configs.get('base_style_ref')
        config_output_dir = configs.get('output_dir', output_dir)
        tasks = configs['tasks']

        if not isinstance(tasks, list):
            raise ValueError("'tasks'必须是数组")

        print_info(f"发现 {len(tasks)} 个任务")

        # 使用配置中的输出目录，如果没有则使用命令行参数
        final_output_dir = Path(config_output_dir if config_output_dir else output_dir)
        final_output_dir.mkdir(parents=True, exist_ok=True)

        for i, task in enumerate(tasks, 1):
            try:
                print(f"\n[{i}/{len(tasks)}] 处理任务：{task.get('name', f'task_{i}')}")

                # 获取图片路径，支持 base_image 和单独指定
                image_url = None
                if 'image' in task:
                    image_path = task['image']
                    if Path(image_path).exists():
                        image_url = encode_file_to_base64(image_path)
                    else:
                        # 支持直接使用 URL
                        image_url = image_path
                elif base_image:
                    # 使用基础图片
                    if Path(base_image).exists():
                        image_url = encode_file_to_base64(base_image)
                    else:
                        image_url = base_image
                else:
                    print_warning(f"跳过：未指定图片路径")
                    continue

                # 获取风格参数
                style_index = task.get('style_index')
                style_ref = task.get('style_ref')

                # 处理变量引用
                if style_ref == "${base_style_ref}" and base_style_ref:
                    style_ref = base_style_ref

                if style_index is not None:
                    result = generator.repaint_and_wait(
                        image_url=image_url,
                        style_index=style_index,
                        timeout=timeout
                    )
                elif style_ref:
                    # 支持 URL 或文件路径的风格引用
                    if Path(style_ref).exists():
                        style_ref_url = encode_file_to_base64(style_ref)
                    else:
                        style_ref_url = style_ref

                    result = generator.repaint_and_wait(
                        image_url=image_url,
                        style_ref_url=style_ref_url,
                        timeout=timeout
                    )
                else:
                    print_warning(f"跳过：未指定风格参数")
                    continue

                if result.results and result.results[0].url:
                    print_success(f"完成：{result.results[0].url}")

                    # 获取输出文件名
                    output_name = task.get('output_name')
                    if not output_name:
                        output_name = f"repaint_{task.get('name', f'task_{i}')}.jpg"

                    # 自动下载并保存图片
                    saved_files = download_and_save_image(
                        result.results[0].url,
                        str(final_output_dir),
                        type('Args', (), {'style': style_index})()
                    )

                    # 重命名为指定文件名
                    if output_name != Path(saved_files).name:
                        old_path = Path(saved_files)
                        new_path = old_path.parent / output_name
                        old_path.rename(new_path)
                        saved_files = str(new_path)

                    print_success(f"任务 {i} 图片已保存：{saved_files}")

                    # 保存结果信息
                    task_result = {
                        "task_id": result.task_id,
                        "output_url": result.results[0].url,
                        "saved_files": saved_files,
                        "input_image": image_url,
                        "config": task
                    }

                    result_file = final_output_dir / f"task_{i}_{result.task_id}.json"
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(task_result, f, ensure_ascii=False, indent=2)

            except Exception as e:
                print_error(f"任务 {i} 失败：{str(e)}")
                if verbose:
                    import traceback
                    traceback.print_exc()

        print_success(f"批量处理完成！结果保存在：{final_output_dir}")
        return 0

    except Exception as e:
        print_error(f"批量处理失败：{str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
