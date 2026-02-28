#!/usr/bin/env python3
"""
图像编辑子命令
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.image import ImageEditor
from cli.shared import (
    check_api_key,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_warning,
    get_model_short_name,
    validate_file_exists
)


def add_arguments(parser):
    """添加子命令参数"""
    # 必需参数
    parser.add_argument(
        "image_path",
        help="输入图像路径或 URL"
    )

    parser.add_argument(
        "prompt",
        help="编辑提示词"
    )

    # 模型选择
    parser.add_argument(
        "-m", "--model",
        choices=["qwen-image-edit", "wanx2.1-imageedit"],
        default="qwen-image-edit",
        help="编辑模型：qwen-image-edit(千问 - 同步) 或 wanx2.1-imageedit(万相 - 异步 + 功能选择)"
    )

    # 万相模型专用参数
    wanx_group = parser.add_argument_group('万相模型专用参数')
    wanx_group.add_argument(
        "-f", "--function",
        choices=[
            "stylization_all", "stylization_local", "description_edit",
            "description_edit_with_mask", "remove_watermark", "expand",
            "super_resolution", "colorization", "doodle", "control_cartoon_feature"
        ],
        help="万相 9 大功能类型 (万相模型必选项)"
    )

    wanx_group.add_argument(
        "-n", "--n",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="万相模型：生成图片数量 (1-4 张，默认 1)"
    )

    wanx_group.add_argument(
        "-S", "--seed",
        type=int,
        help="万相模型：随机种子 (控制生成随机性)"
    )

    wanx_group.add_argument(
        "--strength",
        type=float,
        choices=[i / 10 for i in range(0, 11)],  # 0.0-1.0，步长 0.1
        help="万相模型：图像修改幅度，用于全局风格化和指令编辑 (0.0-1.0，默认 0.5)"
    )

    # 扩图功能专用参数
    expand_group = parser.add_argument_group('扩图功能专用参数（仅--function expand 时有效）')
    expand_group.add_argument(
        "--top-scale",
        type=float,
        choices=[i / 10 for i in range(10, 21)],  # 1.0-2.0，步长 0.1
        default=1.0,
        help="向上扩展比例 [1.0-2.0]，默认 1.0"
    )
    expand_group.add_argument(
        "--bottom-scale",
        type=float,
        choices=[i / 10 for i in range(10, 21)],  # 1.0-2.0，步长 0.1
        default=1.0,
        help="向下扩展比例 [1.0-2.0]，默认 1.0"
    )
    expand_group.add_argument(
        "--left-scale",
        type=float,
        choices=[i / 10 for i in range(10, 21)],  # 1.0-2.0，步长 0.1
        default=1.0,
        help="向左扩展比例 [1.0-2.0]，默认 1.0"
    )
    expand_group.add_argument(
        "--right-scale",
        type=float,
        choices=[i / 10 for i in range(10, 21)],  # 1.0-2.0，步长 0.1
        default=1.0,
        help="向右扩展比例 [1.0-2.0]，默认 1.0"
    )

    # 超分辨率专用参数
    super_group = parser.add_argument_group('超分辨率专用参数（仅--function super_resolution 时有效）')
    super_group.add_argument(
        "--upscale-factor",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="放大倍数 (1-4 倍，默认 1。1=仅高清不放大)"
    )

    # 线稿生图专用参数
    doodle_group = parser.add_argument_group('线稿生图专用参数（仅--function doodle 时有效）')
    doodle_group.add_argument(
        "--is-sketch",
        action="store_true",
        help="输入是否为线稿图像 (true=直接基于线稿作画，false=先提取线稿再作画)"
    )

    wanx_group.add_argument(
        "mask_path",
        nargs='?',
        help="万相模型：mask 图像路径（仅 description_edit_with_mask 功能需要）"
    )

    # 千问模型专用参数
    qwen_group = parser.add_argument_group('千问模型专用参数')
    qwen_group.add_argument(
        "-N", "--negative",
        default="",
        help="反向提示词 (仅千问模型支持)"
    )

    parser.add_argument(
        "-k", "--api-key",
        help="阿里云百炼 API 密钥"
    )

    parser.add_argument(
        "-o", "--output",
        default="./output/images/edited",
        help="输出目录 (默认：./output/images/edited)"
    )

    parser.add_argument(
        "-w", "--watermark",
        action="store_true",
        help="添加水印标识"
    )

    parser.add_argument(
        "--filename",
        help="输出文件名（可选，默认自动生成）"
    )


def execute(args):
    """执行子命令"""
    print_banner(
        "阿里百炼图像编辑工具",
        "支持千问 - 图像编辑 & 万相 - 通用图像编辑"
    )

    # 检查 API 密钥
    if not check_api_key(args.api_key):
        return 1

    try:
        editor = ImageEditor(api_key=args.api_key)

        # 验证图像路径
        image_url = validate_image_path(args.image_path, editor)

        # 模型专用参数验证
        mask_image_url = None
        if args.model == "wanx2.1-imageedit":
            if not args.function:
                print_error("万相模型必须指定 --function 参数")
                print("可用功能：stylization_all, stylization_local, description_edit, description_edit_with_mask, remove_watermark, expand, super_resolution, colorization, doodle, control_cartoon_feature")
                return 1

            if args.function == "description_edit_with_mask":
                if not args.mask_path:
                    print_error("万相局部重绘功能需要提供 mask 图像")
                    print("使用示例：python -m cli image-edit base.jpg mask.png '添加物体' --function description_edit_with_mask")
                    return 1
                mask_image_url = validate_image_path(args.mask_path, editor)
                print_info(f"使用万相局部重绘：mask={args.mask_path}")
            else:
                print_info(f"使用万相功能：{args.function}")

        elif args.model == "qwen-image-edit":
            if args.function:
                print_warning("千问模型不需要 --function 参数，已忽略")
            print_info("使用千问 - 图像编辑（同步接口）")

        print_info(f"正在编辑：{args.image_path}")
        print_info(f"编辑指令：{args.prompt}")
        print_info(f"使用模型：{args.model}")

        if args.negative:
            print_info(f"反向提示：{args.negative}")

        # 构建万相模型专用参数
        wanx_params = {}
        if args.model == "wanx2.1-imageedit":
            if args.strength is not None:
                wanx_params['strength'] = args.strength

            if args.function == "expand":
                wanx_params.update({
                    'top_scale': args.top_scale,
                    'bottom_scale': args.bottom_scale,
                    'left_scale': args.left_scale,
                    'right_scale': args.right_scale
                })

            if args.function == "super_resolution":
                wanx_params['upscale_factor'] = args.upscale_factor

            if args.function == "doodle":
                wanx_params['is_sketch'] = args.is_sketch

        # 执行编辑
        result = editor.edit_image(
            model=args.model,
            image_url=image_url,
            prompt=args.prompt,
            function=args.function,
            mask_image_url=mask_image_url,
            negative_prompt=args.negative or None,
            n=args.n,
            seed=args.seed,
            watermark=args.watermark,
            **wanx_params
        )

        # 获取编辑后的图像 URL
        if args.model == "qwen-image-edit":
            # 千问模型直接返回 URL
            edited_url = result.url
            print_success("编辑完成！")
            print_info(f"图像 URL: {edited_url}")
        else:
            # 万相模型从结果中提取 URL
            if result.results and result.results[0]:
                edited_url = result.results[0].url
                print_success("编辑完成！")
                print_info(f"图像 URL: {edited_url}")
            else:
                print_error("编辑失败：未获取到结果")
                return 1

        # 下载图像
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        if args.filename:
            filename = args.filename
        else:
            model_short = get_model_short_name(args.model)
            safe_name = "".join(c for c in args.prompt[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_') or "edited"
            if args.function:
                filename = f"{model_short}_{args.function}_{safe_name}.png"
            else:
                filename = f"{model_short}_{safe_name}.png"

        file_path = editor.download_image(edited_url, str(output_dir), filename)

        print_success(f"保存路径：{file_path}")
        task_id_str = result.task_id if hasattr(result, 'task_id') and result.task_id else "同步任务 (千问模型)"
        print_info(f"任务 ID: {task_id_str}")

        return 0

    except Exception as e:
        print_error(f"错误：{e}")
        return 1


def validate_image_path(image_path: str, editor: ImageEditor) -> str:
    """验证图像路径并返回 URL/Base64"""
    path = Path(image_path)
    if not path.exists():
        # 如果是 URL，直接返回
        if image_path.startswith(('http://', 'https://')):
            return image_path
        else:
            raise FileNotFoundError(f"图像文件不存在：{image_path}")

    # 本地文件转换为 Base64
    return editor.encode_image_to_base64(str(path))
