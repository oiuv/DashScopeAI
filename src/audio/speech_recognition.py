"""
阿里百炼实时语音识别统一接口
提供简单易用的语音识别功能
"""

import os
import pyaudio
from dashscope.audio.asr import RecognitionCallback, Recognition, RecognitionResult
from typing import Optional

class SpeechRecognizer(RecognitionCallback):
    """统一语音识别接口"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "paraformer-realtime-v2"):
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        self.model = model
        self.audio = None
        self.stream = None
        self.recognizer = None
        
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
        
        import dashscope
        dashscope.api_key = self.api_key
    
    def list_devices(self):
        """列出所有音频设备"""
        p = pyaudio.PyAudio()
        
        print("音频输入设备:")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"  {i}: {dev['name']} (输入通道: {dev['maxInputChannels']})")
        
        p.terminate()
    
    def start_microphone_recognition(self, device_index: Optional[int] = None):
        """开始麦克风语音识别"""
        return MicrophoneRecognition(self.model, device_index)
    
    def start_speaker_recognition(self, device_index: Optional[int] = None):
        """开始扬声器语音识别"""
        return SpeakerRecognition(self.model, device_index)

class MicrophoneRecognition:
    """麦克风识别会话"""
    
    def __init__(self, model: str, device_index: Optional[int] = None):
        self.model = model
        self.device_index = device_index
        self.recognizer = None
        
    def start(self):
        """开始识别"""
        from .microphone_recognizer import MicrophoneRecognizer
        mic = MicrophoneRecognizer(model=self.model)
        mic.start_listening(device_index=self.device_index)

class SpeakerRecognition:
    """扬声器识别会话"""
    
    def __init__(self, model: str, device_index: Optional[int] = None):
        self.model = model
        self.device_index = device_index
        self.recognizer = None
        
    def start(self):
        """开始识别"""
        from .speaker_recognizer import SpeakerRecognizer
        speaker = SpeakerRecognizer(model=self.model)
        speaker.start_listening(device_index=self.device_index)

def quick_start(mode: str = "mic", device_index: Optional[int] = None):
    """快速启动语音识别"""
    """
    参数:
        mode: "mic" 或 "speaker"
        device_index: 指定设备索引
    """
    recognizer = SpeechRecognizer()
    
    if mode == "mic":
        session = recognizer.start_microphone_recognition(device_index)
    elif mode == "speaker":
        session = recognizer.start_speaker_recognition(device_index)
    else:
        raise ValueError("mode 必须是 'mic' 或 'speaker'")
    
    session.start()

if __name__ == "__main__":
    # 快速测试
    recognizer = SpeechRecognizer()
    recognizer.list_devices()