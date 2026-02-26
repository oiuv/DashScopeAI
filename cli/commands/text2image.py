#!/usr/bin/env python3
"""
文生图子命令
"""

import sys
from pathlib import Path
from typing import Optional

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.image import Text2ImageGenerator
from src.utils.file_utils import PromptFileReader
from cli.shared import (
    check_api_key,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_warning,
    get_model_short_name,
    validate_size_format
)


def add_arguments(parser):
    """添加子命令参数"""
    # 输入方式组
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "prompt",
        nargs='?',
        help="生成图像的文本描述"
    )
    input_group.add_argument(
        "-f", "--file",
        help="从文件读取提示词（支持.txt 和.json 格式）"
    )

    parser.add_argument(
        "-m", "--model",
        choices=["qwen-image", "wan2.2-t2i-flash", "wan2.2-t2i-plus", "wanx2.1-t2i-turbo", "wanx2.1-t2i-plus", "wanx2.0-t2i-turbo"],
        default="wan2.2-t2i-flash",
        help="模型选择 (默认：wan2.2-t2i-flash)"
    )

    parser.add_argument(
        "-s", "--size",
        default="1024*1024",
        help="图像尺寸 (万相：512-1440 像素任意组合，千问：1328*1328/1664*928/1472*1140/1140*1472/928*1664)"
    )

    parser.add_argument(
        "-n", "--n",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="生成图片数量 (仅万相模型支持 1-4 张，千问模型仅支持 1 张)"
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
        help="阿里云百炼 API 密钥"
    )

    parser.add_argument(
        "-o", "--output",
        default="./generated_images",
        help="输出目录 (默认：./generated_images)"
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


def execute(args):
    """执行子命令"""
    print_banner("阿里百炼文生图工具", "阿里云百炼大模型 - 文本生成图像")

    # 检查 API 密钥
    if not check_api_key(args.api_key):
        return 1

    try:
        generator = Text2ImageGenerator(api_key=args.api_key)

        if args.file:
            return process_file_input(generator, args)
        else:
            return process_single_prompt(generator, args)

    except Exception as e:
        print_error(f"错误：{e}")
        return 1


def process_file_input(generator: Text2ImageGenerator, args) -> int:
    """处理文件输入"""
    filepath = Path(args.file)
    if not filepath.exists():
        print_error(f"文件不存在：{filepath}")
        return 1

    print_info(f"从文件读取：{filepath}")

    try:
        prompts = PromptFileReader.read_prompt_file(str(filepath))

        if not prompts:
            print_error("文件中没有找到有效提示词")
            return 1

        # 构建配置列表
        configs = []

        if isinstance(prompts[0], dict):
            # JSON 格式 - 使用完整配置
            configs = prompts
            print_info(f"找到 {len(configs)} 个 JSON 配置")
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
            print_info(f"找到 {len(configs)} 个文本提示词")

        # 统一处理所有配置
        from pathlib import Path as PPath
        output_dir = PPath(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for i, config in enumerate(configs, 1):
            prompt_text = config.get('prompt', '')
            print(f"\n[{i}/{len(configs)}] 处理：{prompt_text[:60]}...")

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

                    print_success(f"成功：{filename}")
                    print_info(f"保存路径：{file_path}")
                    print_info(f"使用模型：{validated_config.get('model', '未知')}")
                    print_info(f"图片尺寸：{validated_config.get('size', '未知')}")
                    if image.actual_prompt:
                        print_info(f"实际提示词：{image.actual_prompt}")
                    print_info(f"原始提示词：{image.orig_prompt}")
                    success_count += 1
                else:
                    print_error(f"失败：{prompt_text}")

            except Exception as e:
                print_error(f"任务 {i} 失败：{e}")
                continue

        print(f"\n📊 文件处理完成：{success_count}/{len(configs)} 成功")
        return 0 if success_count > 0 else 1

    except Exception as e:
        print_error(f"文件读取错误：{e}")
        return 1


def process_single_prompt(generator: Text2ImageGenerator, args) -> int:
    """处理单个提示词"""
    print_info(f"正在生成：{args.prompt}")
    if args.negative:
        print_info(f"反向提示：{args.negative}")

    # 验证千问模型的特殊限制
    if args.model == "qwen-image" and args.n != 1:
        print_warning("千问模型仅支持生成 1 张图片，已自动调整为 1")
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
        from pathlib import Path as PPath
        output_dir = PPath(args.output)
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

        print_success("生成成功！")
        print_info(f"保存路径：{file_path}")
        print_info(f"使用模型：{args.model}")
        print_info(f"图片尺寸：{args.size}")
        print_info(f"原始 URL: {image.url}")
        print_info(f"任务 ID: {result.task_id}")
        if image.actual_prompt:
            print_info(f"实际提示词：{image.actual_prompt}")
        print_info(f"原始提示词：{image.orig_prompt}")

        return 0
    else:
        print_error(f"生成失败：{result.task_status}")
        return 1
