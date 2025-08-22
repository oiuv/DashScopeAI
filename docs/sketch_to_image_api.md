# 通义万相-涂鸦作画API完整文档

## 产品概述
通义万相-涂鸦作画通过手绘任意内容加文字描述，即可生成精美的涂鸦绘画作品。作品中的内容在参考手绘线条的同时，兼顾创意性和趣味性。支持扁平插画、油画、二次元、3D卡通和水彩5种风格。

**模型名称**: `wanx-sketch-to-image-lite`

## 计费标准
- **免费额度**: 500张（开通阿里云百炼大模型服务后自动发放，有效期180天）
- **计费单价**: 0.06元/张
- **限流**: 2 QPS（含主账号与RAM子账号）
- **并发限制**: 同时处理中任务数量1个

## 使用场景
- **创意贺卡设计**: 结合节日主题和个人创意，制作个性化贺卡
- **儿童绘本制作**: 为儿童教育制作有趣的插图绘本
- **个性化商品设计**: 为T恤、手机壳等商品设计独特图案
- **社交媒体内容创作**: 创作原创涂鸦插图，提升内容吸引力
- **室内装饰设计**: 定制个性化墙面艺术画或装饰图案

## 支持风格
| 风格类型 | 描述 |
|---------|------|
| `<auto>` | 默认值，由模型随机输出图像风格 |
| `<3d cartoon>` | 3D卡通 |
| `<anime>` | 二次元 |
| `<oil painting>` | 油画 |
| `<watercolor>` | 水彩风格（默认） |
| `<sketch>` | 素描 |
| `<chinese painting>` | 中国画 |
| `<flat illustration>` | 扁平插画 |

## 完整HTTP调用流程

### 步骤1：创建任务获取任务ID

**HTTP端点**: `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis`

**必需请求头**:
- `X-DashScope-Async: enable` - 必须启用异步处理
- `Authorization: Bearer {API_KEY}` - 身份认证
- `Content-Type: application/json`

#### 创建任务示例
```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
    "model": "wanx-sketch-to-image-lite",
    "input": {
        "sketch_image_url": "https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/6609471071/p743851.jpg",
        "prompt": "一棵参天大树"
    },
    "parameters": {
        "size": "768*768",
        "n": 2,
        "sketch_weight": 3,
        "style": "<watercolor>"
    }
}'
```

#### 成功响应示例
```json
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

### 步骤2：根据任务ID查询结果

**HTTP端点**: `GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`

#### 查询任务结果示例
```bash
curl -X GET \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
https://dashscope.aliyuncs.com/api/v1/tasks/0385dc79-5ff8-4d82-bcb6-xxxxxx
```

#### 成功响应示例
```json
{
    "request_id": "85eaba38-0185-99d7-8d16-4d9135238846",
    "output": {
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [
            {
                "url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/123/a1.png"
            },
            {
                "url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/123/b2.png"
            }
        ],
        "task_metrics": {
            "TOTAL": 2,
            "SUCCEEDED": 2,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 2
    }
}
```

## 请求参数详解

### 请求头（Headers）
| 参数 | 类型 | 描述 |
|---|---|---|
| `Content-Type` | string | 必选，必须设置为 `application/json` |
| `Authorization` | string | 必选，格式为 `Bearer {API_KEY}` |
| `X-DashScope-Async` | string | 必选，必须设置为 `enable` |
| `X-DashScope-WorkSpace` | string | 可选，阿里云百炼业务空间ID |

### 请求体（Request Body）

#### 必选参数
| 参数 | 类型 | 描述 |
|---|---|---|
| `model` | string | 必选，调用模型，固定为 `wanx-sketch-to-image-lite` |
| `input` | object | 必选，输入的基本信息 |
| `input.prompt` | string | 必选，提示词，≤75字符 |
| `input.sketch_image_url` | string | 必选，输入草图的URL地址 |

#### 可选参数
| 参数 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `parameters.size` | string | 输出图像分辨率 | `768*768` |
| `parameters.n` | integer | 生成图片数量，1-4张 | 4 |
| `parameters.style` | string | 输出图像风格 | `<watercolor>` |
| `parameters.sketch_weight` | integer | 草图约束程度，0-10 | 10 |
| `parameters.sketch_extraction` | boolean | 是否提取sketch边缘 | false |
| `parameters.sketch_color` | array | 画笔色RGB数值 | [] |

### 输入要求
- **草图格式**：JPG、JPEG、PNG、TIFF、WEBP
- **草图大小**：≤10MB
- **草图分辨率**：256×256 到 2048×2048 像素
- **背景建议**：白色背景+黑色线条
- **比例要求**：草图比例需与输出分辨率一致

## 响应参数详解

### 任务状态枚举
| 状态 | 说明 |
|---|---|
| `PENDING` | 任务排队中 |
| `RUNNING` | 任务处理中 |
| `SUCCEEDED` | 任务执行成功 |
| `FAILED` | 任务执行失败 |
| `CANCELED` | 任务取消成功 |
| `UNKNOWN` | 任务不存在或状态未知 |

### 响应数据结构
- **task_id**: 任务唯一标识
- **task_status**: 当前任务状态
- **results**: 成功时返回的图像URL列表
- **task_metrics**: 任务统计信息
- **usage.image_count**: 实际生成的图片数量
- **request_id**: 请求唯一标识

## 任务生命周期

1. **创建任务** → 返回task_id，状态为PENDING
2. **排队等待** → 状态可能为PENDING或RUNNING
3. **处理完成** → 状态变为SUCCEEDED或FAILED
4. **结果获取** → 24小时内可访问生成的图像URL
5. **自动清理** → 24小时后任务数据自动清除

## 最佳实践

### 草图绘制建议
- 使用清晰的线条，避免过于复杂的细节
- 确保线条与背景对比明显
- 保持适当的留白，避免过度填充

### 提示词优化
- 描述要具体明确，包含颜色、风格、细节
- 使用形容词增强效果，如"美丽的"、"梦幻的"
- 结合风格参数使用，如"水彩风格的花朵"

### 错误处理
- 实现指数退避重试机制
- 监控任务状态，避免无限轮询
- 及时保存生成的图像URL

## 常见错误码
| 错误码 | 描述 | 解决方案 |
|---|---|---|
| 400 | 参数无效 | 检查图像格式、大小、分辨率 |
| 401 | 认证失败 | 验证API密钥是否正确 |
| 429 | 限流 | 实现重试机制，降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

## 使用限制
- **并发限制**: 同时处理中任务数量1个
- **限流**: 2 QPS
- **有效期**: 生成图像URL有效期24小时
- **文件大小**: 输入图像≤10MB