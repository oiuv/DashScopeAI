# 示例文件目录说明

本目录包含阿里百炼大模型工具集的各种使用示例和配置文件。

## 目录结构

```
examples/
├── text2image/          # 文生图(Text-to-Image)配置和提示词
├── image_edit/          # 图生图(Image-to-Image)编辑配置
├── style-repaint/       # 人像风格重绘配置
├── scripts/             # Python示例脚本
├── prompts/             # 通用提示词文件
└── README.md           # 本说明文档
```

## 目录详细说明

### text2image/
文生图相关配置文件，支持以下模型：
- `wan2.2-t2i-flash` - 极速生成
- `wan2.2-t2i-plus` - 高质量生成
- `qwen-image` - 通义千问模型（中文文字渲染优秀）
- `wanx2.1-t2i-turbo` - 极速版
- `wanx2.1-t2i-plus` - 专业版

### image_edit/
图生图编辑配置文件，支持两大编辑系统：

**通义千问编辑模型 (qwen-image-edit)**
- 文字编辑、物体增删、姿势调整、风格迁移
- 同步接口，0.3元/张

**万相编辑模型 (wanx2.1-imageedit)**
- 全局风格化、局部风格化、指令编辑、局部重绘
- 去水印、扩图、超分、上色、线稿生图
- 异步接口，0.14元/张

### style-repaint/
人像风格重绘专用配置，使用 `wanx-style-repaint-v1` 模型：
- 支持多种艺术风格转换
- 专门针对人像优化
- 批量处理示例配置

### scripts/
Python示例脚本，可直接运行：
- `text2image_qwen_example.py` - Qwen文生图基础示例
- `image_edit_qwen_example.py` - Qwen图像编辑基础示例

### prompts/
通用提示词文件，可用于批量处理：
- `.txt` 格式 - 每行一个提示词
- `.json` 格式 - 详细参数配置

## 使用示例

### 运行脚本示例
```bash
# 文生图示例
python scripts/text2image_qwen_example.py

# 图生图示例（需准备input.png）
python scripts/image_edit_qwen_example.py
```

### 使用配置文件
```bash
# 批量文生图
python text2image.py -f text2image/t2i_prompts.json

# 批量图生图
python image_edit.py -f image_edit/wanx_stylization_examples.json

# 人像风格重绘
python style_repaint.py -f style-repaint/style_repaint_examples.json
```

## 文件命名约定

- `qwen_*` - 通义千问相关配置
- `wanx_*` - 万相系列模型配置
- `t2i_*` - 文生图相关
- `*_examples.json` - 批量示例配置
- `*_demo.json` - 演示配置

## 注意事项

1. 运行前确保已设置 `DASHSCOPE_API_KEY` 环境变量
2. 部分模型需要特定尺寸的输入图像
3. 异步模型需要轮询获取结果
4. 编辑功能可能需要额外的mask图像