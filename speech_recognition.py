#!/usr/bin/env python3
"""
阿里百炼实时语音识别工具
统一入口脚本，支持麦克风和扬声器识别

使用方法:
    python speech_recognition.py --mode mic        # 识别麦克风输入
    python speech_recognition.py --mode speaker    # 识别扬声器输出
    python speech_recognition.py --list            # 列出音频设备
    python speech_recognition.py --test            # 测试音频设置

环境要求:
    pip install dashscope pyaudio
    # Windows用户: pip install pipwin && pipwin install pyaudio
"""

import argparse
import os
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.audio.microphone_recognizer import MicrophoneRecognizer
from src.audio.speaker_recognizer import SpeakerRecognizer

def print_banner():
    """打印程序欢迎信息"""
    print("=" * 60)
    print("阿里百炼实时语音识别工具")
    print("=" * 60)
    print("模式说明:")
    print("  麦克风模式: 识别你对着麦克风说的话")
    print("  扬声器模式: 识别电脑播放的任何声音")
    print("=" * 60)

def check_api_key():
    """检查API密钥"""
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 错误: 未设置DASHSCOPE_API_KEY环境变量")
        print("💡 请先设置环境变量:")
        print("   Windows: set DASHSCOPE_API_KEY=your-api-key")
        print("   Linux/Mac: export DASHSCOPE_API_KEY=your-api-key")
        return False
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="阿里百炼实时语音识别工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python speech_recognition.py --mode mic
  python speech_recognition.py --mode speaker --device 34
  python speech_recognition.py --list
  python speech_recognition.py --test --mode speaker
        """
    )
    
    parser.add_argument("--mode", choices=["mic", "speaker"], 
                       help="识别模式: mic=麦克风, speaker=扬声器")
    parser.add_argument("--model", default="paraformer-realtime-v2",
                       choices=["paraformer-realtime-v2", "gummy-realtime-v1"],
                       help="识别模型")
    parser.add_argument("--list", action="store_true",
                       help="列出所有音频设备")
    parser.add_argument("--device", type=int,
                       help="指定音频设备索引")
    parser.add_argument("--test", action="store_true",
                       help="测试音频设置")
    parser.add_argument("--verbose", action="store_true",
                       help="显示详细信息")
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print_banner()
    
    # 检查API密钥
    if not check_api_key():
        sys.exit(1)
    
    try:
        if args.list:
            # 列出所有设备
            print("📋 麦克风设备:")
            mic = MicrophoneRecognizer()
            mic.list_microphones()
            
            print("\n📋 扬声器回环设备:")
            speaker = SpeakerRecognizer()
            speaker.list_all_devices()
            return
        
        if args.test:
            # 测试音频设置
            print("🔍 测试音频设置...")
            if args.mode == "speaker":
                speaker = SpeakerRecognizer(model=args.model)
                speaker.test_audio_setup()
            else:
                mic = MicrophoneRecognizer(model=args.model)
                mic.list_microphones()
            return
        
        # 根据模式启动识别器
        if args.mode == "mic":
            print("🎤 启动麦克风识别模式...")
            recognizer = MicrophoneRecognizer(model=args.model)
            print("💡 请对着麦克风说话，按Ctrl+C停止")
            recognizer.start_listening(device_index=args.device)
            
        elif args.mode == "speaker":
            print("🔊 启动扬声器识别模式...")
            recognizer = SpeakerRecognizer(model=args.model)
            print("💡 请确保有音频正在播放，按Ctrl+C停止")
            recognizer.start_listening(device_index=args.device)
            
        else:
            print("❌ 请指定模式: --mode mic 或 --mode speaker")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()