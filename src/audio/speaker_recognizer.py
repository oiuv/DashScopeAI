import pyaudio
import dashscope
from dashscope.audio.asr import RecognitionCallback, Recognition, RecognitionResult
import os
import sys

class SpeakerRecognizer(RecognitionCallback):
    """扬声器输出实时语音识别器"""
    
    def __init__(self, api_key=None, model="paraformer-realtime-v2"):
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        self.model = model
        self.audio = None
        self.stream = None
        self.recognizer = None
        
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量或传入api_key参数")
        
        dashscope.api_key = self.api_key
    
    def find_speaker_device(self):
        """查找扬声器回环设备"""
        p = pyaudio.PyAudio()
        
        # 常见的扬声器回环设备关键词
        speaker_keywords = [
            "立体声混音", "stereo mix", "what u hear", "wave out mix",
            "loopback", "系统声音", "system sound", "mix"
        ]
        
        # 排除麦克风的关键词
        exclude_keywords = ["microphone", "mic", "麦克风"]
        
        candidates = []
        
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                name = dev['name'].lower()
                
                # 检查是否是回环设备
                is_loopback = any(keyword in name for keyword in speaker_keywords)
                is_not_mic = not any(keyword in name for keyword in exclude_keywords)
                
                if is_loopback:
                    print(f"✅ 找到扬声器回环设备: {i} - {dev['name']}")
                    p.terminate()
                    return i
                elif is_not_mic and ("stereo" in name or "mix" in name):
                    candidates.append((i, dev['name']))
        
        # 如果没有找到回环设备，返回None让用户手动指定
        if candidates:
            print("📋 可能的扬声器回环设备:")
            for i, name in candidates:
                print(f"  {i}: {name}")
            
            print("💡 请使用 --device 参数指定正确的设备")
        
        p.terminate()
        return None
    
    def on_open(self) -> None:
        """开始识别时的回调"""
        print("🔊 开始监听扬声器输出...")
        print("💡 确保有音频从扬声器播放")
        print("💡 按 Ctrl+C 停止识别")
    
    def on_close(self) -> None:
        """停止识别时的回调"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("\n🔇 扬声器监听已关闭")
    
    def on_event(self, result: RecognitionResult) -> None:
        """识别结果回调"""
        if result and hasattr(result, 'text') and result.text:
            print(f"🗣️  识别到: {result.text}")
    
    def list_all_devices(self):
        """列出所有音频设备"""
        p = pyaudio.PyAudio()
        print("📋 所有音频设备:")
        print("输入设备:")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"  {i}: {dev['name']} (输入通道: {dev['maxInputChannels']})")
        
        print("\n输出设备:")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxOutputChannels'] > 0:
                print(f"  {i}: {dev['name']} (输出通道: {dev['maxOutputChannels']})")
        
        p.terminate()
    
    def setup_virtual_audio(self):
        """设置虚拟音频设备（Windows/Mac/Linux通用提示）"""
        print("""
🎯 如果找不到扬声器设备，请按以下步骤设置：

Windows:
1. 右键点击音量图标 → 声音设置
2. 录制 → 右键空白处 → 显示禁用的设备
3. 启用"立体声混音" (Stereo Mix)
4. 右键"立体声混音" → 启用 → 设为默认设备

Mac:
1. 安装 BlackHole 或 Loopback 虚拟音频驱动
2. 在"音频MIDI设置"中创建多输出设备
3. 将系统输出重定向到虚拟设备

Linux:
1. 安装 PulseAudio Volume Control: sudo apt install pavucontrol
2. 运行 pavucontrol → 录制 → 选择"Monitor of [你的输出设备]"
""")
    
    def start_listening(self, device_index=None):
        """开始实时监听扬声器输出"""
        try:
            # 查找设备
            if device_index is None:
                device_index = self.find_speaker_device()
                if device_index is None:
                    print("❌ 未找到合适的扬声器回环设备")
                    print("💡 请检查以下设置:")
                    self.setup_virtual_audio()
                    return
            
            print(f"🎯 使用设备索引: {device_index}")
            
            # 初始化识别器
            self.recognizer = Recognition(
                model=self.model,
                format="pcm",
                sample_rate=16000,
                callback=self
            )
            
            self.recognizer.start()
            
            # 打开音频流
            self.audio = pyaudio.PyAudio()
            
            # 验证设备
            try:
                dev_info = self.audio.get_device_info_by_index(device_index)
                print(f"✅ 使用设备 {device_index}: {dev_info['name']}")
            except:
                print(f"❌ 设备 {device_index} 无效")
                self.list_all_devices()
                return
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=3200,
                stream_callback=None
            )
            
            print("🔊 开始实时识别扬声器输出的声音...")
            print("💡 请确保有音频正在播放")
            
            try:
                while True:
                    if self.stream and self.recognizer:
                        data = self.stream.read(3200, exception_on_overflow=False)
                        self.recognizer.send_audio_frame(data)
            except KeyboardInterrupt:
                print("\n⏹️  用户中断识别")
            except Exception as e:
                print(f"❌ 识别过程中出错: {e}")
            finally:
                self.stop()
                
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            self.stop()
    
    def stop(self):
        """停止识别"""
        if self.recognizer:
            try:
                self.recognizer.close()
            except:
                pass
        self.on_close()
    
    def test_audio_setup(self):
        """测试音频设置"""
        print("🔍 测试音频设置...")
        
        # 查找设备
        device_index = self.find_speaker_device()
        if device_index is not None:
            print(f"✅ 找到扬声器设备: {device_index}")
            
            # 测试音频流
            try:
                self.audio = pyaudio.PyAudio()
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=3200
                )
                
                print("🔊 正在测试音频流...")
                for i in range(50):  # 录制5秒测试
                    data = self.stream.read(3200, exception_on_overflow=False)
                    if i % 10 == 0:
                        print(f"📊 收到音频数据: {len(data)} 字节")
                
                self.stream.stop_stream()
                self.stream.close()
                self.audio.terminate()
                print("✅ 音频流测试成功")
                
            except Exception as e:
                print(f"❌ 音频流测试失败: {e}")
        else:
            print("❌ 未找到扬声器设备")
            self.setup_virtual_audio()

def main():
    """主函数 - 命令行使用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="实时扬声器语音识别")
    parser.add_argument("--model", default="paraformer-realtime-v2", 
                       choices=["paraformer-realtime-v2", "gummy-realtime-v1"],
                       help="识别模型")
    parser.add_argument("--list-devices", action="store_true", 
                       help="列出所有音频设备")
    parser.add_argument("--device", type=int, help="指定扬声器设备索引")
    parser.add_argument("--test", action="store_true", 
                       help="测试音频设置")
    
    args = parser.parse_args()
    
    try:
        recognizer = SpeakerRecognizer(model=args.model)
        
        if args.list_devices:
            recognizer.list_all_devices()
            return
        
        if args.test:
            recognizer.test_audio_setup()
            return
        
        if args.device is not None:
            print(f"使用设备 {args.device}")
        
        recognizer.start_listening(device_index=args.device)
        
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()