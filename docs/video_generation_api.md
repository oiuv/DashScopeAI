# 阿里云百炼视频生成API文档

## 产品概述

阿里云百炼提供多样化的视频模型选择，涵盖文生视频、图生视频（通用/舞蹈/唱演/播报等）、视频编辑（通用/视频风格重绘/视频口型替换）等应用场景。

## 模型分类总览

| 类别 | 说明 |
|------|------|
| **文生视频** | 一句话生成视频，视频风格丰富，画质细腻 |
| **图生视频** | 首帧生视频、首尾帧生视频、多图生视频、图+动作模板生成舞蹈视频、图+音频生成对口型视频 |
| **视频编辑** | 通用视频编辑、视频口型替换、视频风格转换 |

## 文生视频模型

### 通义万相-文生视频模型
通过一句话即可生成视频，视频呈现丰富的艺术风格及影视级画质。

#### 支持的模型

| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **wan2.2-t2v-plus** ⭐ | 万相2.2专业版，画面细节表现、运动稳定性显著提升 | 480P：0.14元/秒<br>1080P：0.70元/秒 | 50秒 |
| **wanx2.1-t2v-turbo** | 万相2.1极速版，文生视频，性价比高 | 0.24元/秒 | 200秒 |
| **wanx2.1-t2v-plus** | 万相2.1专业版，生成细节丰富，画面更具质感 | 0.70元/秒 | 200秒 |

#### 输入示例
```
提示词：一只小猫在月光下奔跑
```

## 图生视频模型

### 1. 基于首帧的图生视频
将输入图片作为视频首帧，再根据提示词生成视频。

#### 支持的模型

| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **wan2.2-i2v-plus** ⭐ | 万相2.2专业版，画面细节表现、运动稳定性显著提升 | 480P：0.14元/秒<br>1080P：0.70元/秒 | 50秒 |
| **wanx2.1-i2v-turbo** | 万相2.1极速版，图生视频，性价比高 | 0.24元/秒 | 200秒 |
| **wanx2.1-i2v-plus** | 万相2.1专业版，生成细节丰富，画面更具质感 | 0.70元/秒 | 200秒 |

#### 输入示例
```
提示词：一只猫在草地上奔跑
输入图片：[首帧图片]
模型：wanx2.1-i2v-turbo
```

### 2. 基于首尾帧的图生视频
只需要提供首帧和尾帧图片，便能根据提示词生成一段丝滑流畅的动态视频。

| 模型名称 | 单价 | 免费额度 |
|----------|------|----------|
| **wanx2.1-kf2v-plus** | 0.70元/秒 | 200秒 |

#### 输入示例
```
首帧图片：[首帧]
尾帧图片：[尾帧]
提示词：写实风格，一只黑色小猫好奇地看向天空，镜头从平视逐渐上升，最后俯拍小猫好奇的眼神
```

## 视频编辑模型

### 1. 通用视频编辑
通义万相-视频编辑统一模型支持多模态输入，包括文本、图像和视频，能够执行视频生成与通用编辑任务。

| 模型名称 | 单价 | 免费额度 |
|----------|------|----------|
| **wanx2.1-vace-plus** | 0.70元/秒 | 50秒 |

#### 支持功能
- **多图参考**：参考主体和背景图片
- **视频重绘**：基于提示词重新生成视频内容
- **局部编辑**：使用掩码图像指定编辑区域
- **视频延展**：延长视频时长
- **视频画面扩展**：扩展视频画面范围

### 2. 视频风格重绘
支持根据用户输入的文字内容，生成符合语义描述的不同风格的视频，或者根据用户输入的视频，进行视频风格重绘。

| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **video-style-transform** | 将输入视频转换为日式漫画、美式漫画等风格 | 720P：0.5元/秒<br>540P：0.2元/秒 | 600秒 |

## 人像视频生成模型

### 1. 舞动人像AnimateAnyone
基于人物图片和人物动作模板，生成人物动作视频。

#### 模型链
| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **animate-anyone-detect-gen2** | 检测输入图片是否符合要求 | 0.004元/张 | 200张 |
| **animate-anyone-template-gen2** | 从人物运动视频中提取动作并生成模板 | 0.08元/秒 | 1800秒 |
| **animate-anyone-gen2** | 基于人物图片和动作模板生成人物动作视频 | - | - |

#### 独立部署模型
| 模型名称 | 部署单价 | 说明 |
|----------|----------|------|
| **animate-anyone-detect** | 10000元/算力单元/月<br>20元/算力单元/小时 | 检测输入图片是否符合要求 |
| **animate-anyone** | 同上 | 基于人物图片和动作模板生成人物动作视频 |

### 2. 悦动人像EMO
基于人物肖像图片和人声音频文件，生成人物肖像动态视频。

#### 模型链
| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **emo-detect-v1** | 检测输入图片是否符合要求 | 0.004元/张 | 200张 |
| **emo-v1** | 生成人物肖像动态视频 | 1:1画幅：0.08元/秒<br>3:4画幅：0.16元/秒 | 1800秒 |

### 3. 灵动人像LivePortrait
基于人物肖像图片和人声音频文件，快速、轻量地生成人物肖像动态视频。

#### 模型链
| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **liveportrait-detect** | 检测输入图片是否符合要求 | 0.004元/张 | 200张 |
| **liveportrait** | 生成人物肖像动态视频 | 0.02元/秒 | 1800秒 |

### 4. 表情包Emoji
基于人脸图片和预设的人脸动态模板，生成人脸动态视频。

#### 模型链
| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **emoji-detect-v1** | 检测输入图片是否符合要求 | 0.004元/张 | 200张 |
| **emoji-v1** | 基于人物肖像图片和表情包模板生成人物同款表情 | 0.08元/秒 | 500秒 |

### 5. 声动人像VideoRetalk
基于人物视频和人声音频，生成人物讲话口型与输入音频相匹配的视频。

| 模型名称 | 说明 | 单价 | 免费额度 |
|----------|------|------|----------|
| **videoretalk** | 生成人物讲话口型与输入音频相匹配的新视频 | 0.08元/秒 | 1800秒 |

## API使用指南

### 1. 文生视频API调用

#### 创建任务
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video/video-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
    "model": "wan2.2-t2v-plus",
    "input": {
        "prompt": "一只小猫在月光下奔跑"
    },
    "parameters": {
        "resolution": "720*1280",
        "duration": 5,
        "fps": 24
    }
}'
```

#### 查询结果
```bash
curl -X GET \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
https://dashscope.aliyuncs.com/api/v1/tasks/{your_task_id}
```

### 2. 图生视频API调用

#### 首帧生视频
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video/video-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
    "model": "wanx2.1-i2v-plus",
    "input": {
        "image_url": "https://example.com/cat.jpg",
        "prompt": "一只猫在草地上奔跑"
    },
    "parameters": {
        "resolution": "720*1280",
        "duration": 3
    }
}'
```

#### 首尾帧生视频
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video/video-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
    "model": "wanx2.1-kf2v-plus",
    "input": {
        "first_frame_url": "https://example.com/first.jpg",
        "last_frame_url": "https://example.com/last.jpg",
        "prompt": "写实风格，一只黑色小猫好奇地看向天空"
    },
    "parameters": {
        "duration": 5
    }
}'
```

## Python SDK使用示例

### 安装依赖
```bash
pip install dashscope
```

### 文生视频示例
```python
import dashscope
from dashscope import VideoSynthesis
import os
import time

# 设置API密钥
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

# 创建文生视频任务
response = VideoSynthesis.async_call(
    model='wan2.2-t2v-plus',
    prompt='一只小猫在月光下奔跑，梦幻风格',
    resolution='720*1280',
    duration=5,
    fps=24
)

# 获取任务ID
task_id = response.output.task_id
print(f"任务ID: {task_id}")

# 轮询查询结果
while True:
    result = VideoSynthesis.fetch(task_id)
    if result.output.task_status == 'SUCCEEDED':
        print("视频生成成功！")
        for video in result.output.results:
            print(f"视频URL: {video.url}")
        break
    elif result.output.task_status == 'FAILED':
        print(f"任务失败: {result.output.message}")
        break
    else:
        print("正在生成中...")
        time.sleep(5)
```

### 图生视频示例
```python
from dashscope import VideoSynthesis

# 首帧生视频
response = VideoSynthesis.async_call(
    model='wanx2.1-i2v-plus',
    image_url='https://example.com/cat.jpg',
    prompt='一只可爱的橘猫在花园里嬉戏',
    resolution='720*1280',
    duration=3
)

# 首尾帧生视频
response = VideoSynthesis.async_call(
    model='wanx2.1-kf2v-plus',
    first_frame_url='https://example.com/start.jpg',
    last_frame_url='https://example.com/end.jpg',
    prompt='日落时分，小鸟从树枝飞向天空',
    duration=4
)
```

## 人像视频生成链式调用

### 悦动人像EMO完整流程
```python
from dashscope import ImageSynthesis, VideoSynthesis

# 1. 检测图片是否符合要求
detect_response = ImageSynthesis.call(
    model='emo-detect-v1',
    image_url='https://example.com/portrait.jpg'
)

if detect_response.output.result == 'pass':
    # 2. 生成EMO视频
    response = VideoSynthesis.async_call(
        model='emo-v1',
        image_url='https://example.com/portrait.jpg',
        audio_url='https://example.com/audio.mp3',
        style_level='active'  # 活泼风格
    )
    
    task_id = response.output.task_id
    print(f"EMO任务ID: {task_id}")
else:
    print("图片不符合要求，请更换图片")
```

## 参数说明

### 通用参数
| 参数 | 类型 | 说明 | 取值范围 |
|------|------|------|----------|
| resolution | string | 视频分辨率 | "480*480", "720*1280", "1080*1920" |
| duration | int | 视频时长（秒） | 1-5（部分模型支持更长） |
| fps | int | 帧率 | 8, 16, 24 |

### 图生视频专用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| image_url | string | 输入图片URL |
| first_frame_url | string | 首帧图片URL |
| last_frame_url | string | 尾帧图片URL |
| prompt | string | 生成提示词 |

### 人像视频参数
| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| audio_url | string | 输入音频URL | - |
| style_level | string | 动作风格强度 | "subtle", "normal", "active" |
| driven_id | string | 表情包模板ID | 见官方模板列表 |

## 错误处理

### 常见错误码
| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 400 | 参数无效 | 检查分辨率、时长是否在支持范围内 |
| 401 | 认证失败 | 验证API密钥是否正确 |
| 429 | 限流 | 实现重试机制，降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

### 异常处理示例
```python
try:
    response = VideoSynthesis.async_call(...)
except Exception as e:
    if "InvalidParameter" in str(e):
        print("参数错误，请检查输入参数")
    elif "Unauthorized" in str(e):
        print("API密钥无效")
    else:
        print(f"未知错误: {e}")
```

## 最佳实践

### 1. 提示词优化
- **具体明确**：描述动作、场景、风格
- **避免歧义**：使用清晰的形容词和名词
- **控制时长**：复杂场景适当延长时长

### 2. 图片准备
- **高质量**：使用清晰、高分辨率的图片
- **合适比例**：确保图片比例与目标视频一致
- **主体突出**：避免复杂背景干扰

### 3. 批量处理
- **异步调用**：避免同步等待超时
- **合理并发**：控制并发任务数量
- **结果缓存**：避免重复生成相同内容

