# 📊 千问 vs 万相图像编辑模型对比报告

## 🎯 核心差异总览

| 对比维度 | 通义千问-图像编辑 | 通义万相-通用图像编辑 |
|---|---|---|
| **模型名称** | `qwen-image-edit` | `wanx2.1-imageedit` |
| **计费单价** | 0.3元/张 | 0.14元/张 |
| **免费额度** | 100张 | 500张 |
| **图像规格** | 384×384 ~ 3072×3072 | 512×512 ~ 4096×4096 |
| **接口类型** | **同步** | **异步** |
| **API端点** | `/services/aigc/multimodal-generation/generation` | `/services/aigc/image2image/image-synthesis` |

## 🔧 接口调用方式对比

### 千问-同步接口
```bash
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
# 直接返回结果，无需轮询
```

### 万相-异步接口
```bash
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis
# 返回task_id，需二次查询
GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}
```

## 📋 功能特性对比

| 功能类别 | 千问支持 | 万相支持 | 万相优势 |
|---|---|---|---|
| **基础编辑** | ✅ 文字编辑、物体增删 | ✅ 9大功能 | 功能更丰富 |
| **风格化** | ✅ 风格迁移 | ✅ 全局+局部风格化 | 支持局部风格 |
| **区域控制** | ❌ 无精确控制 | ✅ mask图像精确控制 | 精度更高 |
| **图像修复** | ✅ 细节增强 | ✅ 超分+上色+扩图 | 修复能力更强 |
| **创意生成** | ✅ 姿势调整 | ✅ 线稿生图+卡通生图 | 创意性更强 |

## 🎨 功能矩阵对比

| 具体功能 | 千问实现方式 | 万相实现方式 |
|---|---|---|
| **风格转换** | 指令描述风格 | `function: stylization_all` |
| **局部修改** | 文字描述区域 | `function: description_edit_with_mask` + mask图 |
| **去水印** | 指令"去除文字" | `function: remove_watermark` |
| **图像放大** | 指令"高清" | `function: super_resolution` |
| **黑白上色** | 指令"添加色彩" | `function: colorization` |
| **扩图** | 指令"扩展背景" | `function: expand` |

## 📊 参数结构对比

### 千问-参数结构
```json
{
  "model": "qwen-image-edit",
  "input": {
    "messages": [{
      "role": "user",
      "content": [
        {"image": "url/base64"},
        {"text": "编辑指令"}
      ]
    }]
  },
  "parameters": {
    "negative_prompt": "",
    "watermark": false
  }
}
```

### 万相-参数结构
```json
{
  "model": "wanx2.1-imageedit",
  "input": {
    "function": "stylization_all",
    "prompt": "编辑指令",
    "base_image_url": "url/base64",
    "mask_image_url": "url/base64"  // 局部重绘时必填
  },
  "parameters": {
    "n": 1,
    "seed": 12345,
    "watermark": false
  }
}
```

## 🧩 万相9大编辑功能详解

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

## 🚀 开发注意事项

| 项目 | 千问 | 万相 |
|---|---|---|
| **响应时间** | 实时返回 | 需5-15秒+轮询 |
| **错误处理** | 直接返回错误码 | 需查询任务状态 |
| **图像输入** | URL/Base64 | URL/Base64/本地文件 |
| **并发限制** | 无特殊限制 | 需考虑异步队列 |
| **结果有效期** | 24小时 | 24小时 |

## 🎯 使用建议

### 选择千问的场景
- **快速原型开发**：同步接口，无需轮询
- **简单编辑任务**：文字描述即可完成
- **成本敏感**：单次调用成本低（0.14 vs 0.3元）

### 选择万相的场景
- **专业编辑需求**：9大功能全覆盖
- **精确控制**：支持mask区域精确编辑
- **创意工作**：线稿生图、卡通生图等创意功能
- **批量处理**：500张免费额度

## 📈 性价比分析

| 维度 | 千问 | 万相 | 优势方 |
|---|---|---|---|
| **单价** | 0.3元/张 | 0.14元/张 | 万相 |
| **免费额度** | 100张 | 500张 | 万相 |
| **功能数量** | 基础5项 | 专业9项 | 万相 |
| **开发复杂度** | 简单 | 中等 | 千问 |
| **处理精度** | 一般 | 精确 | 万相 |

## 📝 总结建议

- **简单任务**：千问更快速，成本更低
- **专业编辑**：万相功能最全，控制更精确
- **批量处理**：万相免费额度更多（500 vs 100张）
- **开发效率**：千问同步接口更简单，万相异步更稳定

---

*更新时间：2025年8月20日*  
*数据来源：阿里云百炼官方文档*