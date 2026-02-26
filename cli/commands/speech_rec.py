#!/usr/bin/env python3
"""
语音识别子命令
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 延迟导入，避免在 add_arguments 时加载依赖
_microphone_recognizer = None
_speaker_recognizer = None

def _get_microphone_recognizer():
    """延迟加载麦克风识别器"""
    global _microphone_recognizer
    if _microphone_recognizer is None:
        from src.audio.microphone_recognizer import MicrophoneRecognizer
        _microphone_recognizer = MicrophoneRecognizer
    return _microphone_recognizer

def _get_speaker_recognizer():
    """延迟加载扬声器识别器"""
    global _speaker_recognizer
    if _speaker_recognizer is None:
        from src.audio.speaker_recognizer import SpeakerRecognizer
        _speaker_recognizer = SpeakerRecognizer
    return _speaker_recognizer

from cli.shared import check_api_key, print_banner, print_info, print_success, print_error


def add_arguments(parser):
    """添加子命令参数"""
    parser.add_argument(
        "--mode",
        choices=["mic", "speaker"],
        help="识别模式：mic=麦克风，speaker=扬声器"
    )
    parser.add_argument(
        "--model",
        default="paraformer-realtime-v2",
        choices=["paraformer-realtime-v2", "gummy-realtime-v1"],
        help="识别模型"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有音频设备"
    )
    parser.add_argument(
        "--device",
        type=int,
        help="指定音频设备索引"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="测试音频设置"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )


def execute(args):
    """执行子命令"""
    # 打印欢迎信息
    print_banner(
        "阿里百炼实时语音识别工具",
        "模式说明：麦克风模式 - 识别你对着麦克风说的话 | 扬声器模式 - 识别电脑播放的任何声音"
    )

    # 检查 API 密钥
    if not check_api_key(args.api_key if hasattr(args, 'api_key') else None):
        return 1

    try:
        if args.list:
            # 列出所有设备
            print_info("麦克风设备:")
            mic = _get_microphone_recognizer()()
            mic.list_microphones()

            print("\n📋 扬声器回环设备:")
            speaker = _get_speaker_recognizer()()
            speaker.list_all_devices()
            return 0

        if args.test:
            # 测试音频设置
            print_info("测试音频设置...")
            if args.mode == "speaker":
                speaker = _get_speaker_recognizer()(model=args.model)
                speaker.test_audio_setup()
            else:
                mic = _get_microphone_recognizer()(model=args.model)
                mic.list_microphones()
            return 0

        # 根据模式启动识别器
        if args.mode == "mic":
            print_success("启动麦克风识别模式...")
            recognizer = _get_microphone_recognizer()(model=args.model)
            print_info("请对着麦克风说话，按 Ctrl+C 停止")
            recognizer.start_listening(device_index=args.device)

        elif args.mode == "speaker":
            print_success("启动扬声器识别模式...")
            recognizer = _get_speaker_recognizer()(model=args.model)
            print_info("请确保有音频正在播放，按 Ctrl+C 停止")
            recognizer.start_listening(device_index=args.device)

        else:
            print_error("请指定模式：--mode mic 或 --mode speaker")
            print("使用 'python -m cli speech-rec --help' 查看详细用法")
            return 1

    except KeyboardInterrupt:
        print("\n👋 程序已退出")
        return 0
    except Exception as e:
        print_error(f"程序错误：{e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
