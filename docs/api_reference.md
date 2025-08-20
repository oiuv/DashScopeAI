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
    ]
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