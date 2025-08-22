# 实时语音识别API文档

## 产品概述
实时语音识别可以将音频流实时转换为文本，实现"边说边出文字"的效果。适用于麦克风语音实时识别和本地音频文件实时转录。

## 支持的模型

### Paraformer系列
| 模型名称 | 支持语言 | 采样率 | 适用场景 | 单价 | 免费额度 |
|---------|----------|--------|----------|------|----------|
| **paraformer-realtime-v2** | 中文普通话+方言、英语、日语、韩语、德语、法语、俄语 | 任意采样率 | 视频直播、会议 | 0.00024元/秒 | 36,000秒/月 |
| **paraformer-realtime-v1** | 中文 | 16kHz | - | - | - |
| **paraformer-realtime-8k-v2** | 中文 | 8kHz | 电话客服 | - | - |
| **paraformer-realtime-8k-v1** | 中文 | 8kHz | 电话客服 | - | - |

### Gummy系列
| 模型名称 | 支持语言 | 采样率 | 适用场景 | 单价 | 免费额度 |
|---------|----------|--------|----------|------|----------|
| **gummy-realtime-v1** | 中/英/日/韩/粤/德/法/俄/意/西 + 翻译 | 16kHz+ | 会议演讲、直播 | 0.00015元/秒 | 36,000秒/月 |
| **gummy-chat-v1** | 同上 | 16kHz | 对话聊天、指令控制 | 0.00015元/秒 | 36,000秒/月 |

## 模型选择建议
- **多语种混合**：选Gummy
- **中文方言**：选Paraformer-realtime-v2
- **噪音环境**：选Paraformer
- **情感识别**：选Paraformer-realtime-8k-v2
- **语气词过滤**：选Paraformer

## 音频要求
- **格式**：pcm、wav、mp3、opus、speex、aac、amr
- **采样位数**：16bit
- **声道**：单声道
- **时长**：Paraformer不限，Gummy-chat限60秒内

## Python SDK安装
```bash
pip install dashscope pyaudio
```

## 麦克风输入示例
```python
import pyaudio
import dashscope
from dashscope.audio.asr import *

class MicrophoneRecognizer(RecognitionCallback):
    def __init__(self):
        self.mic = None
        self.stream = None
        
    def on_open(self):
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=3200
        )
        print("🎤 开始监听麦克风...")

    def on_close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()
        print("🔇 停止监听")

    def on_event(self, result: RecognitionResult):
        if result and result.sentence:
            print(f"🎯 识别结果: {result.text}")

    def start_listening(self):
        recognizer = RecognitionRecognizer(
            model="paraformer-realtime-v2",
            format="pcm",
            sample_rate=16000,
            callback=self
        )
        recognizer.start()
        
        try:
            while True:
                if self.stream:
                    data = self.stream.read(3200, exception_on_overflow=False)
                    recognizer.send_audio_frame(data)
        except KeyboardInterrupt:
            recognizer.stop()
            self.on_close()

# 使用示例
if __name__ == "__main__":
    dashscope.api_key = "your-api-key"
    recognizer = MicrophoneRecognizer()
    recognizer.start_listening()
```

## 扬声器输出示例
```python
import pyaudio
import dashscope
from dashscope.audio.asr import *

class SpeakerRecognizer(RecognitionCallback):
    def __init__(self):
        self.audio = None
        self.stream = None
        
    def find_speaker_device(self):
        """查找扬声器设备"""
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0 and '扬声器' in dev['name']:
                return i
        return None

    def on_open(self):
        device_index = self.find_speaker_device()
        if device_index is None:
            print("❌ 未找到扬声器设备")
            return
            
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=3200
        )
        print("🔊 开始监听扬声器输出...")

    def on_close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("🔇 停止监听")

    def on_event(self, result: RecognitionResult):
        if result and result.sentence:
            print(f"🎯 识别到说话: {result.text}")

    def start_listening(self):
        recognizer = RecognitionRecognizer(
            model="paraformer-realtime-v2",
            format="pcm",
            sample_rate=16000,
            callback=self
        )
        recognizer.start()
        
        try:
            while True:
                if self.stream:
                    data = self.stream.read(3200, exception_on_overflow=False)
                    recognizer.send_audio_frame(data)
        except KeyboardInterrupt:
            recognizer.stop()
            self.on_close()

# 使用示例
if __name__ == "__main__":
    dashscope.api_key = "your-api-key"
    recognizer = SpeakerRecognizer()
    recognizer.start_listening()
```

## 本地文件识别
```python
import dashscope
from dashscope.audio.asr import *

def recognize_file(file_path):
    recognizer = RecognitionRecognizer(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000
    )
    
    with open(file_path, 'rb') as f:
        audio_data = f.read()
    
    result = recognizer.recognize(audio_data)
    print(f"📁 文件识别结果: {result.text}")

# 使用示例
recognize_file("test.wav")
```

## 错误处理
```python
try:
    recognizer.start()
except Exception as e:
    if "InvalidParameter" in str(e):
        print("参数错误")
    elif "Unauthorized" in str(e):
        print("API密钥无效")
    else:
        print(f"错误: {e}")
```

## 环境配置
```bash
# Windows安装PyAudio
pip install pipwin
pipwin install pyaudio

# Linux/Mac
pip install pyaudio

# 设置API密钥
export DASHSCOPE_API_KEY=your-api-key
```