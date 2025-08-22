import pyaudio
import dashscope
from dashscope.audio.asr import RecognitionCallback, Recognition, RecognitionResult
import os
import sys

class MicrophoneRecognizer(RecognitionCallback):
    """麦克风实时语音识别器"""
    
    def __init__(self, api_key=None, model="paraformer-realtime-v2"):
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        self.model = model
        self.mic = None
        self.stream = None
        self.recognizer = None
        
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量或传入api_key参数")
        
        dashscope.api_key = self.api_key
    
    def on_open(self) -> None:
        """开始识别时的回调"""
        try:
            self.mic = pyaudio.PyAudio()
            self.stream = self.mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=3200,
                input_device_index=None  # 使用默认麦克风
            )
            print("🎤 麦克风已打开，开始监听...")
            print("💡 按 Ctrl+C 停止识别")
        except Exception as e:
            print(f"❌ 打开麦克风失败: {e}")
            raise
    
    def on_close(self) -> None:
        """停止识别时的回调"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()
        print("\n🔇 麦克风已关闭")
    
    def on_event(self, result: RecognitionResult) -> None:
        """识别结果回调"""
        if result and hasattr(result, 'text') and result.text:
            print(f"🎯 你说: {result.text}")
    
    def list_microphones(self):
        """列出可用的麦克风设备"""
        p = pyaudio.PyAudio()
        print("📋 可用的麦克风设备:")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"  {i}: {dev['name']}")
        p.terminate()
    
    def start_listening(self, device_index=None):
        """开始实时监听麦克风"""
        try:
            self.recognizer = Recognition(
                model=self.model,
                format="pcm",
                sample_rate=16000,
                callback=self
            )
            
            self.recognizer.start()
            
            # 打开指定设备或默认设备
            self.mic = pyaudio.PyAudio()
            self.stream = self.mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=3200
            )
            
            print("🎤 开始实时语音识别...")
            
            try:
                while True:
                    if self.stream and self.recognizer:
                        data = self.stream.read(3200, exception_on_overflow=False)
                        self.recognizer.send_audio_frame(data)
            except KeyboardInterrupt:
                print("\n⏹️  用户中断识别")
            finally:
                self.stop()
                
        except Exception as e:
            print(f"❌ 识别过程中出错: {e}")
            self.stop()
    
    def stop(self):
        """停止识别"""
        if self.recognizer:
            try:
                self.recognizer.close()
            except:
                pass
        self.on_close()

def main():
    """主函数 - 命令行使用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="实时麦克风语音识别")
    parser.add_argument("--model", default="paraformer-realtime-v2", 
                       choices=["paraformer-realtime-v2", "gummy-realtime-v1"],
                       help="识别模型")
    parser.add_argument("--list-devices", action="store_true", 
                       help="列出麦克风设备")
    parser.add_argument("--device", type=int, help="指定麦克风设备索引")
    
    args = parser.parse_args()
    
    try:
        recognizer = MicrophoneRecognizer(model=args.model)
        
        if args.list_devices:
            recognizer.list_microphones()
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