# 📚 阿里百炼API参考文档

## 🎯 概述
本文档提供阿里百炼全功能API的完整参考，包括文生图、文生文、文生视频等所有模型的详细参数说明。

---

## 🎨 文生图API

### 支持的模型

#### 通义千问文生图 (qwen-image)
- **模型名称**: `qwen-image`
- **特色能力**: 中英文文本渲染、复杂图文布局
- **计费**: 0.25元/张
- **免费额度**: 100张（180天内有效）

#### 通义万相文生图系列
- `wan2.2-t2i-flash`: 极速版（推荐）
- `wan2.2-t2i-plus`: 专业版（推荐）
- `wanx2.1-t2i-turbo`: 2.1极速版
- `wanx2.1-t2i-plus`: 2.1专业版
- `wanx2.0-t2i-turbo`: 2.0极速版

> **模型命名规则**：万相2.2及更新版本使用`wan`前缀，早期版本使用`wanx`前缀。切换模型时请仔细核对名称，避免调用失败。

### 请求参数

#### 基础参数
| 参数 | 类型 | 必填 | 说明 | 千问限制 | 万相限制 |
|---|---|---|---|---|---|
| `model` | string | 是 | 模型名称 | `qwen-image` | `wan2.2-t2i-flash`等 |
| `prompt` | string | 是 | 正向提示词，≤800字符 | ✅ | ✅ |
| `negative_prompt` | string | 否 | 反向提示词，≤500字符 | ✅ | ✅ |
| `size` | string | 否 | 输出尺寸，默认1024*1024 | 固定5种 | 512-1440任意 |
| `n` | int | 否 | 生成图片数量，默认1 | 仅支持1 | 支持1-4 |
| `prompt_extend` | bool | 否 | 智能改写，默认true | ✅ | ✅ |
| `watermark` | bool | 否 | 添加水印，默认false | ✅ | ✅ |
| `seed` | int | 否 | 随机种子，范围0-2147483647 | ❌ | ✅ |

**seed参数说明**：当提供seed值且n>1时，系统会自动为每张图片生成连续种子值（seed, seed+1, seed+2...）。如需生成内容保持相对稳定，请使用相同的seed值。

#### 尺寸支持表
**千问模型固定尺寸**:
- `1328*1328` (1:1) - 正方形
- `1664*928` (16:9) - 宽屏
- `1472*1140` (4:3) - 标准
- `1140*1472` (3:4) - 竖屏
- `928*1664` (9:16) - 竖长

**万相模型灵活尺寸**:
- 范围: 512×512 到 1440×1440
- 限制: 总像素≤200万
- 支持任意宽高比

### 响应格式

#### 成功响应
```json
{
  "request_id": "xxx",
  "output": {
    "task_id": "xxx",
    "task_status": "SUCCEEDED",
    "submit_time": "2025-08-13 18:04:35.703",
    "scheduled_time": "2025-08-13 18:04:35.732",
    "end_time": "2025-08-13 18:04:55.601",
    "results": [
      {
        "orig_prompt": "原始提示词",
        "actual_prompt": "改写后提示词",
        "url": "https://xxx.png"
      }
    ],
    "task_metrics": {
      "TOTAL": 1,
      "SUCCEEDED": 1,
      "FAILED": 0
    }
  }
}
```

#### 错误响应
```json
{
  "request_id": "xxx",
  "error": {
    "code": "InvalidParameter",
    "message": "参数错误详情"
  }
}
```

### 使用示例

#### CLI使用
```bash
# 基础使用
python text2image.py "可爱猫咪" --model wan2.2-t2i-flash --size 1024*1024

# 千问模型文字渲染
python text2image.py "中文对联设计" --model qwen-image --size 1472*1140

# 批量生成
python text2image.py "风景画" --model wan2.2-t2i-flash --n 4 --size 512*512
```

#### JSON配置
```json
{
  "model": "wan2.2-t2i-flash",
  "input": {
    "prompt": "提示词",
    "negative_prompt": "反向提示词"
  },
  "parameters": {
    "size": "1024*1024",
    "n": 1,
    "prompt_extend": true,
    "watermark": false,
    "seed": 12345
  }
}
```

---

## 📝 文生文API

### 支持的模型
- `qwen-turbo`
- `qwen-plus`
- `qwen-max`

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 模型名称 |
| `prompt` | string | 是 | 输入文本 |
| `max_tokens` | int | 否 | 最大生成长度，默认1500 |
| `temperature` | float | 否 | 随机性，0-2，默认1.0 |
| `top_p` | float | 否 | 核采样，0-1，默认0.8 |

### 响应格式
```json
{
  "output": {
    "choices": [
      {
        "message": {
          "content": "生成的文本"
        }
      }
    ]
  }
}
```

---

## 🖼️ 图像编辑API

### 支持的模型

#### 通义千问-图像编辑 (qwen-image-edit)
- **模型名称**: `qwen-image-edit`
- **特色能力**: 中英双语文字编辑、调色、细节增强、风格迁移、增删物体、改变位置和动作
- **计费**: 0.3元/张
- **免费额度**: 100张（180天内有效）
- **图像要求**: 支持JPG、JPEG、PNG、BMP、TIFF、WEBP格式，尺寸384×384到3072×3072像素，大小不超过10MB

### 请求参数

#### 基础参数
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 模型名称，固定为`qwen-image-edit` |
| `messages` | array | 是 | 对话列表，仅支持单轮对话 |
| `negative_prompt` | string | 否 | 反向提示词，≤500字符 |
| `watermark` | bool | 否 | 是否添加水印，默认false |

#### messages结构
```json
{
  "role": "user",
  "content": [
    {
      "image": "图像URL或Base64"
    },
    {
      "text": "编辑指令，≤800字符"
    }
  ]
}
```

#### 图像输入格式
- **URL格式**: 支持HTTP/HTTPS公网地址，不能包含中文字符
- **Base64格式**: `data:{MIME_type};base64,{base64_data}`

### 响应格式

#### 成功响应
```json
{
  "output": {
    "choices": [
      {
        "finish_reason": "stop",
        "message": {
          "role": "assistant",
          "content": [
            {
              "image": "https://xxx.png"
            }
          ]
        }
      }
    ]
  },
  "usage": {
    "width": 1248,
    "height": 832,
    "image_count": 1
  },
  "request_id": "xxx"
}
```

#### 错误响应
```json
{
  "request_id": "xxx",
  "error": {
    "code": "InvalidParameter",
    "message": "参数错误详情"
  }
}
```

### 使用示例

#### HTTP调用
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
    "model": "qwen-image-edit",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": "https://example.com/dog.jpg"
                    },
                    {
                        "text": "将狗改为站立姿势"
                    }
                ]
            }
        ]
    },
    "parameters": {
        "negative_prompt": "低质量",
        "watermark": false
    }
}'
```

#### Python SDK调用
```python
import json
import os
import dashscope
from dashscope import MultiModalConversation

dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1/"

messages = [
    {
        "role": "user",
        "content": [
            {"image": "https://example.com/input.jpg"},
            {"text": "将人物改为站立姿势，背景改为南极"}
        ]
    }
]

response = MultiModalConversation.call(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen-image-edit",
    messages=messages,
    result_format='message',
    stream=False,
    watermark=False,
    negative_prompt="低质量"
)

if response.status_code == 200:
    print(json.dumps(response, ensure_ascii=False))
else:
    print(f"错误码: {response.code}, 错误信息: {response.message}")
```

### 编辑能力示例
- **文字编辑**: 替换图片中的文字内容
- **物体增删**: 添加或移除图片中的物体
- **姿势调整**: 改变人物或动物的动作姿态
- **背景替换**: 更改图片背景场景
- **风格迁移**: 将图片转换为卡通、写实等不同风格
- **细节增强**: 提升图片的清晰度和细节表现

---

## 🖌️ 通义万相图像编辑API

### 支持的模型

#### 通义万相-通用图像编辑 (wanx2.1-imageedit)
- **模型名称**: `wanx2.1-imageedit`
- **特色能力**: 9大编辑功能 - 全局/局部风格化、指令编辑、局部重绘、去水印、扩图、超分、上色、线稿生图、参考卡通生图
- **计费**: 0.14元/张
- **免费额度**: 500张（180天内有效）
- **图像要求**: 支持JPG、JPEG、PNG、BMP、TIFF、WEBP格式，尺寸512×512到4096×4096像素，大小不超过10MB

### 9大编辑功能详解

| 功能名称 | function参数值 | 说明 | 示例场景 |
|---|---|---|---|
| **全局风格化** | `stylization_all` | 整体图像风格转换 | 转换成法国绘本风格 |
| **局部风格化** | `stylization_local` | 指定区域风格转换 | 把房子变成木板风格 |
| **指令编辑** | `description_edit` | 通过文字指令编辑内容 | 把女孩的头发修改为红色 |
| **局部重绘** | `description_edit_with_mask` | 精确区域编辑 | 在指定区域添加陶瓷兔子 |
| **去文字水印** | `remove_watermark` | 去除中英文文字水印 | 去除图像中的文字 |
| **扩图** | `expand` | 按比例扩展图像边界 | 扩展绿色仙子的背景 |
| **图像超分** | `super_resolution` | 高清放大模糊图像 | 将模糊图像变清晰 |
| **图像上色** | `colorization` | 黑白图像转彩色 | 为黑白照片添加色彩 |
| **线稿生图** | `doodle` | 提取线稿并重新生成 | 线稿生成北欧风客厅 |
| **参考卡通生图** | `control_cartoon_feature` | 基于卡通形象生成 | 卡通形象探出头场景 |

### 请求参数

#### 基础参数
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 模型名称，固定为`wanx2.1-imageedit` |
| `function` | string | 是 | 编辑功能类型，见上表 |
| `prompt` | string | 是 | 编辑提示词，≤800字符 |
| `base_image_url` | string | 是 | 输入图像URL或Base64 |
| `mask_image_url` | string | 条件必填 | 局部重绘时的涂抹区域图像 |
| `n` | int | 否 | 生成数量，1-4张，默认1 |
| `seed` | int | 否 | 随机种子，0-2147483647 |
| `watermark` | bool | 否 | 是否添加水印，默认false |

#### 图像输入格式
- **URL格式**: 支持HTTP/HTTPS公网地址
- **Base64格式**: `data:{MIME_type};base64,{base64_data}`
- **本地文件**: `file://绝对路径` 或 `file://相对路径`

#### 局部重绘注意事项
- **mask_image_url**: 黑白图像，白色区域为编辑区域，黑色为保留区域
- **分辨率要求**: mask图像必须与base图像分辨率完全一致

### 响应格式

#### 成功响应（创建任务）
```json
{
  "output": {
    "task_status": "PENDING",
    "task_id": "xxx"
  },
  "request_id": "xxx"
}
```

#### 查询结果响应
```json
{
  "request_id": "xxx",
  "output": {
    "task_id": "xxx",
    "task_status": "SUCCEEDED",
    "submit_time": "2025-02-21 17:56:31.786",
    "end_time": "2025-02-21 17:56:42.530",
    "results": [
      {
        "url": "https://xxx.png"
      }
    ],
    "task_metrics": {
      "TOTAL": 1,
      "SUCCEEDED": 1,
      "FAILED": 0
    }
  },
  "usage": {
    "image_count": 1
  }
}
```

### 使用示例

#### HTTP调用示例

**全局风格化：**
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
  "model": "wanx2.1-imageedit",
  "input": {
    "function": "stylization_all",
    "prompt": "转换成法国绘本风格",
    "base_image_url": "http://example.com/input.jpg"
  },
  "parameters": {
    "n": 1
  }
}'
```

**局部重绘：**
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
  "model": "wanx2.1-imageedit",
  "input": {
    "function": "description_edit_with_mask",
    "prompt": "陶瓷兔子抱着陶瓷小花",
    "base_image_url": "http://example.com/base.jpg",
    "mask_image_url": "http://example.com/mask.png"
  }
}'
```

#### Python SDK三种输入方式

**方式1：公网URL**
```python
from dashscope import ImageSynthesis

rsp = ImageSynthesis.call(
    model="wanx2.1-imageedit",
    function="stylization_all",
    prompt="转换成法国绘本风格",
    base_image_url="http://example.com/input.jpg"
)
```

**方式2：本地文件**
```python
from dashscope import ImageSynthesis

rsp = ImageSynthesis.call(
    model="wanx2.1-imageedit",
    function="super_resolution",
    prompt="图像超分",
    base_image_url="file:///home/images/test.png"  # Linux/macOS
    # base_image_url="file://C:/images/test.png"    # Windows
)
```

**方式3：Base64编码**
```python
import base64
from dashscope import ImageSynthesis

# 编码图像为Base64
def encode_file(file_path):
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded}"

base64_image = encode_file("./test.jpg")
rsp = ImageSynthesis.call(
    model="wanx2.1-imageedit",
    function="colorization",
    prompt="蓝色背景，黄色的叶子",
    base_image_url=base64_image
)
```

### 功能使用技巧

#### 全局风格化
- **支持风格**: 法国绘本、中国水墨、油画等2种风格
- **提示词**: 直接描述目标风格，如"转换成法国绘本风格"

#### 局部风格化
- **支持风格**: 木板、金属、玻璃等8种材质风格
- **提示词**: 指定区域和风格，如"把房子变成木板风格"

#### 指令编辑
- **适用场景**: 简单编辑任务，无需精确控制区域
- **提示词**: 直接描述修改内容，如"把女孩的头发修改为红色"

#### 局部重绘
- **适用场景**: 需要精确控制编辑区域
- **操作步骤**: 1. 创建黑白mask图像 2. 白色区域为编辑区域 3. 黑色区域保持不变

#### 去文字水印
- **适用场景**: 去除中英文文字、水印、logo
- **提示词**: "去除图像中的文字"或"移除水印"

---

## 🎬 文生视频API

### 支持的模型
- `wan2.1-t2v-plus` (专业版)
- `wan2.1-t2v-turbo` (极速版)

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 模型名称 |
| `prompt` | string | 是 | 视频描述，≤1000字符 |
| `resolution` | string | 否 | 分辨率，默认"720*1280" |
| `duration` | int | 否 | 时长秒数，默认5 |
| `fps` | int | 否 | 帧率，默认24 |

### 分辨率支持
- `480*854`
- `720*1280`
- `960*544`
- `1024*576`

---

## 🎵 音频相关API

### 语音合成
- `sambert-zhichu-v1` - 中文语音合成
- `sambert-en-v1` - 英文语音合成

### 语音识别
- `paraformer-v1` - 中文语音识别
- `paraformer-en-v1` - 英文语音识别

---

## 🛠️ 通用规范

### API端点
- **文生图**: `/api/v1/services/aigc/text2image/image-synthesis`
- **文生文**: `/api/v1/services/aigc/text-generation/generation`
- **文生视频**: `/api/v1/services/aigc/video-generation/generation`

### 认证方式
```bash
# Header认证
Authorization: Bearer sk-xxx
X-DashScope-Async: enable
```

### 异步调用流程
1. POST创建任务获取`task_id`
2. GET轮询任务状态
3. 任务有效期24小时
4. 结果有效期24小时

### 错误码说明
| 错误码 | 说明 | 解决建议 |
|---|---|---|
| `InvalidParameter` | 参数错误 | 检查参数格式和范围 |
| `DataInspectionFailed` | 内容不合规 | 修改提示词内容 |
| `TaskFailed` | 任务执行失败 | 重试或联系技术支持 |
| `Unauthorized` | API Key无效 | 检查API Key是否正确 |
| `RateLimitExceeded` | 请求频率超限 | 降低请求频率 |
| `ResourceNotFound` | 任务不存在 | 检查task_id是否正确 |
| `InternalError` | 服务内部错误 | 稍后重试 |
| `ModelNotFound` | 模型不存在 | 检查模型名称是否正确 |
| `QuotaExceeded` | 额度不足 | 充值或等待免费额度重置 |

### 任务状态说明
| 状态 | 说明 |
|---|---|
| `PENDING` | 任务排队中 |
| `RUNNING` | 任务处理中 |
| `SUCCEEDED` | 任务执行成功 |
| `FAILED` | 任务执行失败 |
| `CANCELED` | 任务取消成功 |
| `UNKNOWN` | 任务不存在或状态未知 |

### 任务结果统计
响应中的`task_metrics`字段提供任务执行统计：
- `TOTAL`: 总任务数
- `SUCCEEDED`: 成功任务数
- `FAILED`: 失败任务数

### 限流规则
- **文生图**: 2 RPS
- **文生文**: 10 RPS
- **文生视频**: 1 RPS

---

## 📚 完整示例

### 综合配置示例
```json
{
  "image_tasks": [
    {
      "model": "wan2.2-t2i-flash",
      "prompt": "未来科技城市",
      "size": "1440*810",
      "n": 2
    }
  ],
  "text_tasks": [
    {
      "model": "qwen-turbo",
      "prompt": "生成产品文案"
    }
  ],
  "video_tasks": [
    {
      "model": "wan2.1-t2v-plus",
      "prompt": "日出延时摄影",
      "duration": 10
    }
  ]
}
```

### CLI完整示例
```bash
# 文生图
python text2image.py "未来城市" --model wan2.2-t2i-flash --size 1440*810 --n 2

# 文生文 (未来扩展)
# python text2text.py "写一篇科技文章" --model qwen-turbo

# 文生视频 (未来扩展)  
# python text2video.py "日出延时" --model wan2.1-t2v-plus --duration 10
```

## 🔄 版本更新日志
- v1.0: 基础文生图支持
- v1.1: 添加千问/万相双模型支持
- v1.2: 添加文生文、文生视频API文档占位
- v1.3: 完善所有模型参数说明

## 📞 技术支持
- 官方文档: https://help.aliyun.com/document_detail/2587504.html
- 技术支持群: 钉钉群号12345678
- 问题反馈: https://github.com/aliyun/bailian/issues