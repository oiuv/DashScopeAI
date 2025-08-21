# 阿里百炼API参考文档

## 接口规范概览

### 通用规范

#### 认证方式
```http
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

#### 响应结构
```json
{
  "request_id": "string",
  "output": {...},
  "usage": {...},
  "error": {...}  // 错误时
}
```

---

## 图像编辑API

### 通义千问-图像编辑 (qwen-image-edit)

#### 基本信息
- **接口类型**: 同步接口
- **HTTP端点**: `POST /api/v1/services/aigc/multimodal-generation/generation`
- **计费**: 0.3元/张
- **免费额度**: 50张/月

#### 请求参数

##### 请求体结构
```json
{
  "model": "qwen-image-edit",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "image": "string"
          },
          {
            "text": "string"
          }
        ]
      }
    ]
  },
  "parameters": {
    "negative_prompt": "string",
    "watermark": false
  }
}
```

##### 参数说明
| 参数 | 类型 | 必填 | 限制 | 说明 |
|---|---|---|---|---|
| `model` | string | 是 | 固定`qwen-image-edit` | 模型名称 |
| `input.messages[].content[].image` | string | 是 | 384-3072px, ≤10MB | 输入图像URL或Base64 |
| `input.messages[].content[].text` | string | 是 | ≤800字符 | 编辑提示词 |
| `parameters.negative_prompt` | string | 否 | ≤500字符 | 反向提示词 |
| `parameters.watermark` | boolean | 否 | 默认false | 添加水印标识 |

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

### 通义万相-通用图像编辑 (wanx2.1-imageedit)

#### 基本信息
- **接口类型**: 异步接口
- **HTTP端点**: `POST /api/v1/services/aigc/image2image/image-synthesis`
- **计费**: 0.14元/张
- **免费额度**: 500张/月
- **必需请求头**: `X-DashScope-Async: enable`

#### 请求参数

##### 请求体结构
```json
{
  "model": "wanx2.1-imageedit",
  "input": {
    "function": "string",
    "prompt": "string",
    "base_image_url": "string",
    "mask_image_url": "string"
  },
  "parameters": {
    "n": 1,
    "seed": 12345,
    "watermark": false,
    "strength": 0.5,
    "top_scale": 1.0,
    "bottom_scale": 1.0,
    "left_scale": 1.0,
    "right_scale": 1.0,
    "upscale_factor": 1,
    "is_sketch": false
  }
}
```

##### 参数说明
| 参数 | 类型 | 必填 | 限制 | 说明 |
|---|---|---|---|---|
| `model` | string | 是 | 固定`wanx2.1-imageedit` | 模型名称 |
| `input.function` | string | 是 | 见功能表 | 编辑功能类型 |
| `input.prompt` | string | 是 | ≤800字符 | 编辑提示词 |
| `input.base_image_url` | string | 是 | 512-4096px, ≤10MB | 输入图像URL或Base64 |
| `input.mask_image_url` | string | 条件必填 | 与base同分辨率 | 局部重绘时的mask图像 |
| `parameters.n` | integer | 否 | 1-4，默认1 | 生成图片数量 |
| `parameters.seed` | integer | 否 | 0-2147483647 | 随机种子 |
| `parameters.watermark` | boolean | 否 | 默认false | 添加水印标识 |
| `parameters.strength` | float | 否 | [0.0, 1.0]，默认0.5 | 图像修改幅度（全局风格化/指令编辑） |
| `parameters.top_scale` | float | 否 | [1.0, 2.0]，默认1.0 | 向上扩图比例（扩图功能） |
| `parameters.bottom_scale` | float | 否 | [1.0, 2.0]，默认1.0 | 向下扩图比例（扩图功能） |
| `parameters.left_scale` | float | 否 | [1.0, 2.0]，默认1.0 | 向左扩图比例（扩图功能） |
| `parameters.right_scale` | float | 否 | [1.0, 2.0]，默认1.0 | 向右扩图比例（扩图功能） |
| `parameters.upscale_factor` | integer | 否 | 1-4，默认1 | 放大倍数（超分辨率功能） |
| `parameters.is_sketch` | boolean | 否 | 默认false | 输入是否为线稿（线稿生图功能） |

#### 功能类型表
| function值 | 功能描述 | mask需求 | 特殊参数 |
|---|---|---|---|
| `stylization_all` | 全局风格化 | 不需要 | `strength` |
| `stylization_local` | 局部风格化 | 不需要 | - |
| `description_edit` | 指令编辑 | 不需要 | `strength` |
| `description_edit_with_mask` | 局部重绘 | **必填** | - |
| `remove_watermark` | 去水印 | 不需要 | - |
| `expand` | 扩图 | 不需要 | `top_scale`, `bottom_scale`, `left_scale`, `right_scale` |
| `super_resolution` | 超分辨率 | 不需要 | `upscale_factor` |
| `colorization` | 黑白上色 | 不需要 | - |
| `doodle` | 线稿生图 | 不需要 | `is_sketch` |
| `control_cartoon_feature` | 参考卡通生图 | 不需要 | - |

#### 功能详细说明

##### 1. 全局风格化 (stylization_all)
- **功能描述**: 整张图像风格迁移，支持法国绘本风格、金箔艺术风格
- **提示词技巧**: "转换成xx风格"，如"转换成法国绘本风格"
- **控制参数**: `strength` 控制修改幅度，0.0接近原图，1.0修改最大

##### 2. 局部风格化 (stylization_local)
- **功能描述**: 局部区域风格迁移，支持8种固定风格：

| 中文风格名 | 英文标识 | 说明 |
|---|---|---|
| 冰雕 | ice | 冰雕艺术效果 |
| 云朵 | cloud | 云朵质感效果 |
| 花灯 | chinese festive lantern | 中国传统花灯风格 |
| 木板 | wooden | 木质纹理效果 |
| 青花瓷 | blue and white porcelain | 中国青花瓷风格 |
| 毛茸茸 | fluffy | 毛茸茸材质效果 |
| 毛线 | weaving | 毛线编织效果 |
| 气球 | balloon | 气球质感效果 |

- **使用场景**: 
  - 个性化定制：仅对人物、背景等特定区域进行风格化
  - 广告设计：突出某个商品或元素的艺术风格
- **提示词技巧**: "把xx变成xx风格"，如"把房子变成冰雕风格"

##### 3. 指令编辑 (description_edit)
- **功能描述**: 无需指定区域，通过指令增加/修改内容
- **使用场景**: 个人形象装扮、添加配饰、换发色等
- **提示词技巧**: 使用"添加"、"修改"等操作描述
- **控制参数**: `strength` 控制修改幅度

##### 4. 局部重绘 (description_edit_with_mask)
- **功能描述**: 指定区域进行增加、修改或删除操作
- **使用场景**: 
  - 换装（如修改衣服颜色）
  - 替换局部物件（如桌上的茶杯替换为花瓶）
  - 删除干扰物（如旅游照的遮挡物）

- **提示词技巧**：

  **增加或修改操作**，可用两种方式描述：
  - **方式一**：描述具体动作，如"给小狗添加一顶帽子"
  - **方式二**：客观描述期望内容，如"一只戴着帽子的小狗"

  **删除操作**，需分类处理：
  - **删除小元素**（占据空间较少）：提示词可留空（prompt=""）
  - **删除大元素**（占据空间较大）：详细描述擦除后的内容，如"一个透明玻璃花瓶放在桌子上"，避免简单描述为"删除xxx"

- **必需参数**：
  - `mask_image_url`：**必填**，与`base_image_url`同分辨率的mask图像
  - mask规则：白色区域为编辑区域，黑色区域保持不变

##### 5. 去水印 (remove_watermark)
- **功能描述**: 有效去除图像中的文字（中英文）及水印标识
- **使用场景**: 
  - 图像二次处理：去除文字干扰，提升视觉效果
  - 广告设计：去除品牌水印标识，便于重新设计
  - 内容创作：清理图片素材，去除不需要的文字信息
- **提示词技巧**: 
  - 通用描述："去除图像中的文字"
  - 精确描述："去除英文文字"、"去除中文水印"、"去除品牌标识"

##### 6. 扩图 (expand)
- **功能描述**: 对图像在上、下、左、右四个方向按比例扩展，智能填充扩展区域的内容
- **使用场景**: 
  - 海报设计：将竖图扩展为横版以适应封面尺寸要求
  - 摄影二次构图：扩展背景后重新调整主体位置，优化构图
  - 社交媒体适配：适配不同平台的标准尺寸比例
  - 广告banner制作：将方形图片扩展为横幅尺寸
- **控制参数**: 
  - `top_scale`: 向上扩展比例 [1.0-2.0]，默认1.0
  - `bottom_scale`: 向下扩展比例 [1.0-2.0]，默认1.0  
  - `left_scale`: 向左扩展比例 [1.0-2.0]，默认1.0
  - `right_scale`: 向右扩展比例 [1.0-2.0]，默认1.0
- **提示词技巧**: 描述扩图后整体的画面内容，如"一家人在公园草坪上"、"城市天际线背景"

##### 7. 超分辨率 (super_resolution)
- **功能描述**: 高清放大技术，将模糊或低分辨率图像转化为清晰、高分辨率图像，同时智能增强图像细节
- **关键参数**: 
  - `upscale_factor`: 放大倍数，取值范围1-4，默认1
  - 当`upscale_factor=1`时，仅提升清晰度不进行放大
- **使用场景**: 
  - 老旧照片修复：提升老照片清晰度，还原珍贵回忆
  - 图像高清打印：将小尺寸图片放大到高分辨率用于打印
  - 数字档案优化：提升历史档案图片质量
  - 电商产品图优化：提升商品图片质量，增强用户体验
- **提示词技巧**: 
  - 通用描述："图像超分"、"高清修复"
  - 具体描述："提升清晰度并保持细节"、"高清放大处理"

##### 8. 黑白上色 (colorization)
- **功能描述**: 智能色彩还原技术，将黑白或灰度图像转化为自然生动的彩色图像
- **使用场景**: 
  - 历史照片还原：为珍贵的黑白历史照片添加真实色彩
  - 儿童绘本上色：将黑白线稿转化为彩色绘本插图
  - 艺术创作：为黑白摄影作品添加艺术化色彩风格
  - 家庭相册修复：为老照片上色，焕发新生
- **提示词技巧**: 
  - 自动上色：不提供具体颜色描述，模型自动选择适合色彩
  - 指定颜色：精确描述期望颜色，如"蓝色背景，黄色叶子，红色花朵"
  - 风格描述："自然真实色彩"、"温暖复古色调"、"清新明亮风格"

##### 9. 线稿生图 (doodle)
- **功能描述**: 从图像提取线稿并基于提示词生成新图像
- **使用场景**: 建筑概念设计、插画设计、涂鸦作画
- **控制参数**: `is_sketch=true` 时直接基于线稿作画

##### 10. 参考卡通生图 (control_cartoon_feature)
- **功能描述**: 基于卡通形象生成新场景
- **使用场景**: 卡通IP开发、儿童教育插图
- **提示词技巧**: 详细描述卡通形象行动，如"卡通形象小心翼翼地探出头"

#### 任务结果查询
```http
GET /api/v1/tasks/{task_id}
Authorization: Bearer {API_KEY}
```

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
  "output": {
    "task_id": "xxx",
    "task_status": "SUCCEEDED",
    "results": [
      {
        "url": "https://xxx.png"
      }
    ]
  }
}
```

---

## 图像格式规范

### 支持格式
- JPG、JPEG、PNG、BMP、TIFF、WEBP

### 输入方式
1. **URL格式**: 公网可访问的HTTP/HTTPS地址
2. **Base64格式**: `data:{MIME_type};base64,{base64_data}`

### 尺寸限制
| 模型 | 最小尺寸 | 最大尺寸 | 文件大小 |
|---|---|---|---|
| qwen-image-edit | 384×384 | 3072×3072 | 10MB |
| wanx2.1-imageedit | 512×512 | 4096×4096 | 10MB |

---

## 错误码规范

### HTTP状态码
- `400` - 参数无效
- `401` - 认证失败
- `429` - 请求频率超限
- `500` - 服务器内部错误

### 业务错误码
- `InvalidParameter` - 参数格式错误
- `DataInspectionFailed` - 内容不合规
- `TaskFailed` - 任务执行失败
- `ResourceNotFound` - 任务或资源不存在

---

## 任务状态

| 状态 | 说明 |
|---|---|
| `PENDING` | 任务排队中 |
| `RUNNING` | 任务处理中 |
| `SUCCEEDED` | 任务执行成功 |
| `FAILED` | 任务执行失败 |
| `CANCELED` | 任务取消成功 |
| `UNKNOWN` | 任务不存在或状态未知 |

---

## 配额与限制

### 免费额度
- **千问-图像编辑**: 50张/月
- **万相-通用图像编辑**: 500张/月

### 并发限制
- **个人用户**: 10 QPS
- **企业用户**: 50 QPS

### 价格说明
- **千问-图像编辑**: 0.3元/张
- **万相-通用图像编辑**: 0.14元/张

---

## 参考链接
- 官方文档: https://help.aliyun.com/zh/model-studio/