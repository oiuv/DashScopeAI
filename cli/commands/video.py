#!/usr/bin/env python3
"""
视频生成子命令
支持文生视频、图生视频、首尾帧生视频等功能
"""

import sys
from pathlib import Path
from typing import Optional

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.video import VideoGenerator
from cli.shared import (
    check_api_key,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_warning,
)


def add_arguments(parser):
    """添加子命令参数"""
    # 视频模式作为必需参数
    parser.add_argument(
        'mode',
        choices=['text2video', 'image2video', 'first-last-frame'],
        help='视频生成模式'
    )

    # 文生视频：prompt
    # 图生视频：image prompt
    # 首尾帧：first_frame prompt（尾帧不需要，文档说只需首帧）
    parser.add_argument("param1", help="文生视频=prompt; 图生视频=image; 首尾帧=first_frame")
    parser.add_argument("param2", nargs='?', default=None, help="图生视频=prompt; 首尾帧=prompt（可选）")

    # 共享参数
    parser.add_argument(
        "-m", "--model",
        choices=[
            # 文生视频
            "wan2.6-t2v", "wan2.6-t2v-us", "wan2.5-t2v-preview",
            "wan2.2-t2v-plus", "wanx2.1-t2v-turbo", "wanx2.1-t2v-plus",
            # 图生视频
            "wan2.6-i2v-flash", "wan2.6-i2v", "wan2.6-i2v-us", "wan2.5-i2v-preview",
            "wan2.2-i2v-plus", "wan2.2-i2v-flash", "wanx2.1-i2v-turbo", "wanx2.1-i2v-plus",
            # 首尾帧
            "wanx2.1-kf2v-plus"
        ],
        default="wan2.6-t2v",
        help="模型选择"
    )

    parser.add_argument(
        "--size",
        choices=[
            # 480P
            "480*480", "832*480", "480*832",
            # 720P
            "720*720", "720*1280", "1280*720", "1088*832", "832*1088",
            # 1080P
            "1440*1440", "1080*1920", "1920*1080", "1632*1248", "1248*1632"
        ],
        default=None,
        help="视频分辨率（文生视频使用）"
    )

    parser.add_argument(
        "--resolution",
        choices=["480P", "720P", "1080P"],
        default="1080P",
        help="视频分辨率档位（图生视频使用，默认：1080P）"
    )

    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=5,
        help="视频时长（秒）"
    )

    parser.add_argument(
        "--prompt-extend",
        action="store_true",
        default=True,
        help="开启 prompt 智能改写（默认开启）"
    )

    parser.add_argument(
        "--no-prompt-extend",
        action="store_true",
        help="关闭 prompt 智能改写"
    )

    parser.add_argument(
        "-w", "--watermark",
        action="store_true",
        help="添加水印标识"
    )

    parser.add_argument(
        "-S", "--seed",
        type=int,
        help="随机种子，用于控制生成内容的随机性"
    )

    parser.add_argument(
        "-N", "--negative",
        help="反向提示词（不希望在视频中出现的内容）"
    )

    parser.add_argument(
        "--audio-url",
        help="音频 URL（wan2.5/2.6 系列支持，3-30 秒 mp3/wav）"
    )

    parser.add_argument(
        "--shot-type",
        choices=["single", "multi"],
        help="镜头类型：single=单镜头，multi=多镜头（仅 wan2.6 系列支持）"
    )

    parser.add_argument(
        "--audio",
        action="store_true",
        default=None,
        help="生成有声视频（仅 wan2.6-i2v-flash 支持）"
    )

    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="生成无声视频（仅 wan2.6-i2v-flash 支持）"
    )

    parser.add_argument(
        "--template",
        choices=[
            # 通用特效
            "squish", "rotation", "poke", "inflate", "dissolve", "melt", "icecream",
            # 单人/动物特效
            "flying", "rose", "crystalrose",
            # 单人特效
            "carousel", "singleheart", "dance1", "dance2", "dance3", "dance4", "dance5",
            "mermaid", "graduation", "dragon", "money", "jellyfish", "pupil",
            # 双人特效
            "hug", "frenchkiss", "coupleheart",
            # 首尾帧特效
            "hanfu-1", "solaron", "magazine", "mech1", "mech2"
        ],
        help="视频特效模板名称（使用特效时 prompt 留空）"
    )

    parser.add_argument(
        "-k", "--api-key",
        help="阿里云百炼 API 密钥"
    )

    parser.add_argument(
        "-o", "--output",
        default="./output/videos/generated",
        help="输出目录 (默认：./output/videos/generated)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="等待超时时间（秒）(默认：600)"
    )


def execute(args):
    """执行子命令"""
    print_banner("阿里百炼视频生成工具", "阿里云百炼大模型 - 文本/图像生成视频")

    # 检查 API 密钥
    if not check_api_key(args.api_key):
        return 1

    # 获取视频模式
    video_mode = args.mode

    # 根据模式解析参数
    if video_mode == 'text2video':
        args.prompt = args.param1
    elif video_mode == 'image2video':
        args.image = args.param1
        args.prompt = args.param2
    elif video_mode == 'first-last-frame':
        args.first_frame = args.param1
        args.prompt = args.param2

    # 处理 prompt_extend 参数
    if args.no_prompt_extend:
        args.prompt_extend = False

    # 处理 audio 参数
    if args.no_audio:
        args.audio = False
    elif args.audio:
        args.audio = True
    else:
        args.audio = None

    try:
        generator = VideoGenerator(api_key=args.api_key)

        if video_mode == 'text2video':
            return process_text2video(generator, args)
        elif video_mode == 'image2video':
            return process_image2video(generator, args)
        elif video_mode == 'first-last-frame':
            return process_first_last_frame(generator, args)
        else:
            print_error(f"未知的视频模式：{video_mode}")
            return 1

    except Exception as e:
        print_error(f"错误：{e}")
        return 1


def process_text2video(generator: VideoGenerator, args) -> int:
    """处理文生视频"""
    if not args.prompt:
        print_error("text2video 模式需要提供 prompt 参数")
        return 1

    print_info(f"正在生成视频：{args.prompt}")
    print_info(f"使用模型：{args.model}")
    print_info(f"分辨率：{args.size}")
    print_info(f"时长：{args.duration}秒")

    if args.negative:
        print_info(f"反向提示：{args.negative}")
    if args.audio_url:
        print_info(f"音频 URL: {args.audio_url}")
    if args.shot_type:
        print_info(f"镜头类型：{args.shot_type}")

    try:
        result = generator.generate_video(
            prompt=args.prompt,
            size=args.size,
            duration=args.duration,
            prompt_extend=args.prompt_extend,
            watermark=args.watermark,
            seed=args.seed,
            negative_prompt=args.negative,
            audio_url=args.audio_url,
            shot_type=args.shot_type,
            model=args.model,
        )

        return handle_result(generator, result, args)

    except TimeoutError as e:
        print_error(f"超时：{e}")
        print_info(f"任务 ID 仍有效，可使用任务 ID 继续查询")
        return 1
    except Exception as e:
        print_error(f"生成失败：{e}")
        return 1


def process_image2video(generator: VideoGenerator, args) -> int:
    """处理图生视频"""
    if not args.image:
        print_error("image2video 模式需要提供 image 参数（首帧 URL）")
        return 1

    # 特效模板模式：不需要 prompt
    if args.template:
        return process_image2video_effect(generator, args)

    # 普通图生视频模式：需要 prompt
    if not args.prompt:
        print_error("普通图生视频模式需要提供 prompt 参数（或使用 --template 指定特效）")
        return 1

    print_info(f"正在从图片生成视频")
    print_info(f"输入图片：{args.image}")
    print_info(f"提示词：{args.prompt}")
    print_info(f"使用模型：{args.model}")
    print_info(f"分辨率档位：{args.resolution}")
    print_info(f"时长：{args.duration}秒")

    if args.negative:
        print_info(f"反向提示：{args.negative}")
    if args.audio_url:
        print_info(f"音频 URL: {args.audio_url}")
    if args.shot_type:
        print_info(f"镜头类型：{args.shot_type}")
    if args.audio is not None:
        print_info(f"有声视频：{'是' if args.audio else '否'}")

    try:
        result = generator.generate_image2video(
            image_url=args.image,
            prompt=args.prompt,
            resolution=args.resolution,
            duration=args.duration,
            prompt_extend=args.prompt_extend,
            watermark=args.watermark,
            seed=args.seed,
            negative_prompt=args.negative,
            audio_url=args.audio_url,
            shot_type=args.shot_type,
            audio=args.audio,
            model=args.model,
        )

        return handle_result(generator, result, args)

    except TimeoutError as e:
        print_error(f"超时：{e}")
        print_info(f"任务 ID 仍有效，可使用任务 ID 继续查询")
        return 1
    except Exception as e:
        print_error(f"生成失败：{e}")
        return 1


def process_image2video_effect(generator: VideoGenerator, args) -> int:
    """处理图生视频 - 特效模板模式"""
    print_info(f"正在生成视频特效")
    print_info(f"输入图片：{args.image}")
    print_info(f"特效模板：{args.template}")
    print_info(f"使用模型：{args.model}")
    print_info(f"分辨率档位：{args.resolution}")

    try:
        # 特效模式：prompt 留空
        result = generator.generate_image2video(
            image_url=args.image,
            prompt=None,  # 特效模式不需要 prompt
            resolution=args.resolution,
            duration=args.duration,
            prompt_extend=False,  # 特效模式关闭 prompt_extend
            watermark=args.watermark,
            seed=args.seed,
            model=args.model,
            template=args.template,
        )

        return handle_result(generator, result, args)

    except TimeoutError as e:
        print_error(f"超时：{e}")
        print_info(f"任务 ID 仍有效，可使用任务 ID 继续查询")
        return 1
    except Exception as e:
        print_error(f"生成失败：{e}")
        return 1


def process_first_last_frame(generator: VideoGenerator, args) -> int:
    """处理首尾帧生视频 - 只需首帧图像"""
    if not args.first_frame:
        print_error("first-last-frame 模式需要提供 first_frame 参数（首帧 URL）")
        return 1

    # 根据是否有 template 参数，决定是特效模式还是普通模式
    if args.template:
        # 特效模式：只需要首帧图像 + template
        return process_first_last_frame_effect(generator, args)
    else:
        # 普通模式：需要首帧图像 + prompt
        if not args.prompt:
            print_error("普通模式需要提供 prompt 参数（或使用 --template 指定特效）")
            return 1
        return process_first_last_frame_normal(generator, args)


def process_first_last_frame_effect(generator: VideoGenerator, args) -> int:
    """处理首尾帧生视频 - 特效模板模式"""
    print_info(f"正在生成视频特效")
    print_info(f"输入图片：{args.first_frame}")
    print_info(f"特效模板：{args.template}")
    print_info(f"使用模型：{args.model}")
    print_info(f"分辨率档位：{args.resolution}")

    try:
        # 特效模式：prompt 留空
        result = generator.generate_first_last_frame(
            first_frame_url=args.first_frame,
            prompt=None,  # 特效模式不需要 prompt
            resolution=args.resolution,
            duration=args.duration,
            prompt_extend=False,  # 特效模式关闭 prompt_extend
            watermark=args.watermark,
            seed=args.seed,
            model=args.model,
            template=args.template,
        )

        return handle_result(generator, result, args)

    except TimeoutError as e:
        print_error(f"超时：{e}")
        print_info(f"任务 ID 仍有效，可使用任务 ID 继续查询")
        return 1
    except Exception as e:
        print_error(f"生成失败：{e}")
        return 1


def process_first_last_frame_normal(generator: VideoGenerator, args) -> int:
    """处理首尾帧生视频 - 普通模式（带 prompt）"""
    print_info(f"正在从首帧生成视频")
    print_info(f"首帧：{args.first_frame}")
    print_info(f"提示词：{args.prompt}")
    print_info(f"使用模型：{args.model}")
    print_info(f"分辨率档位：{args.resolution}")

    try:
        result = generator.generate_first_last_frame(
            first_frame_url=args.first_frame,
            prompt=args.prompt,
            resolution=args.resolution,
            duration=args.duration,
            prompt_extend=args.prompt_extend,
            watermark=args.watermark,
            seed=args.seed,
            model=args.model,
        )

        return handle_result(generator, result, args)

    except TimeoutError as e:
        print_error(f"超时：{e}")
        print_info(f"任务 ID 仍有效，可使用任务 ID 继续查询")
        return 1
    except Exception as e:
        print_error(f"生成失败：{e}")
        return 1


def handle_result(generator: VideoGenerator, result, args) -> int:
    """处理生成结果"""
    if result.task_status.value == "SUCCEEDED" and result.video_url:
        # 确保输出目录存在
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        filename = f"video_{result.task_id}.mp4"

        file_path = generator.download_video(
            result.video_url,
            str(output_dir),
            filename
        )

        print_success("视频生成成功！")
        print_info(f"保存路径：{file_path}")
        print_info(f"视频 URL: {result.video_url}")
        print_info(f"任务 ID: {result.task_id}")

        if result.orig_prompt:
            print_info(f"原始提示词：{result.orig_prompt}")
        if result.actual_prompt:
            print_info(f"优化后提示词：{result.actual_prompt}")
        if result.usage:
            usage = result.usage
            if 'duration' in usage:
                print_info(f"视频时长：{usage['duration']}秒")
            if 'size' in usage:
                print_info(f"视频分辨率：{usage['size']}")
            if 'SR' in usage:
                print_info(f"分辨率档位：{usage['SR']}")

        # 提醒用户及时保存
        print_warning("注意：视频 URL 仅 24 小时有效，请及时转存！")

        return 0
    else:
        if result.error_message:
            print_error(f"生成失败：{result.error_message}")
        else:
            print_error(f"生成失败：{result.task_status}")
        return 1
