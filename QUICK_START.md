# 🚀 阿里百炼快速开始 - 全功能入口

## 🎯 项目概述
阿里百炼工具箱 - 一站式AI内容生成平台，支持文生图、文生文、文生视频、语音合成等全功能。

## 📋 功能总览

| 功能模块 | 命令文件 | 核心模型 | 特色能力 |
|---------|----------|----------|----------|
| **🎨 文生图** | `text2image.py` | qwen-image / wan系列 | 文字渲染、创意生成 |
| **📝 文生文** | `text2text.py` | qwen-turbo/plus/max | 文本创作、问答对话 |
| **🎬 文生视频** | `text2video.py` | wan2.1-t2v系列 | 视频生成、动态创作 |
| **🎵 语音合成** | `text2speech.py` | sambert系列 | 中文/英文语音合成 |
| **🎤 语音识别** | `speech2text.py` | paraformer系列 | 中文/英文语音转文字 |

---

## 🚀 快速上手

### 1. 设置API密钥（仅需一次）
```bash
# Windows
set DASHSCOPE_API_KEY=sk-你的阿里云百炼密钥

# Linux/Mac
export DASHSCOPE_API_KEY=sk-你的阿里云百炼密钥
```

### 2. 文生图 - 立即开始
```bash
# 直接输入提示词
python text2image.py "一只可爱的猫咪"

# 使用示例文件
python text2image.py -f examples/prompts.json

# 指定模型和参数
python text2image.py "古风少女" --model qwen-image --size 1140*1472
```

### 3. 其他功能（即将推出）
```bash
# 文生文 - 创作文章
python text2text.py "写一篇关于人工智能的科普文章" --model qwen-turbo

# 文生视频 - 生成短片
python text2video.py "日出延时摄影" --model wan2.1-t2v-plus --duration 10

# 语音合成 - 生成语音
python text2speech.py "欢迎收听今天的AI科技播客" --model sambert-zhichu-v1
```

---

## 🎨 文生图功能详解

### 支持的模型
- **千问模型** (`qwen-image`): 中文文字渲染、对联设计、诗词配图
- **万相模型** (`wan2.2-t2i-flash`): 创意生成、批量出图、灵活尺寸

### 尺寸选择
| 使用场景 | 推荐尺寸 | 模型支持 |
|---------|----------|----------|
| **手机壁纸** | 1080×1920 (9:16) | 万相模型 |
| **电脑壁纸** | 1920×1080 (16:9) | 万相模型 |
| **社媒配图** | 1080×1080 (1:1) | 万相模型 |
| **竖版海报** | 1140×1472 (3:4) | 千问模型 |
| **横版横幅** | 1664×928 (16:9) | 千问模型 |

### 快速测试命令
```bash
# 测试千问文字渲染
python text2image.py "中文对联：福满人间春满园" --model qwen-image --size 1472*1140

# 测试万相创意生成
python text2image.py "赛博朋克城市夜景" --model wan2.2-t2i-flash --size 1440*810

# 批量生成
python text2image.py "可爱猫咪" --model wan2.2-t2i-flash --n 4 --size 512*512
```

---

## 📁 文件结构
```
阿里百炼/
├── text2image.py      # 文生图主程序
├── text2text.py       # 文生文主程序（未来推出）
├── text2video.py      # 文生视频主程序（未来推出）
├── text2speech.py     # 语音合成主程序（未来推出）
├── speech2text.py     # 语音识别主程序（未来推出）
├── examples/
│   ├── prompts.json   # 文生图示例配置
│   └── prompts.txt    # 文生图文本示例
├── docs/
│   ├── text2image_prompt_guide.md  # 文生图指南
│   └── api_reference.md           # 完整API文档
└── src/
    ├── image/         # 文生图模块
    ├── text/          # 文生文模块
    ├── video/         # 文生视频模块
    ├── audio/         # 音频处理模块
    └── models/        # 模型定义
```

---

## 💡 使用建议

### 新手建议
1. **从文生图开始**：`python text2image.py -f examples/prompts.json`
2. **参考官方指南**：查看 `docs/text2image_prompt_guide.md`
3. **逐步尝试**：先用简单提示词，再添加细节描述

### 进阶用户
1. **使用JSON配置**：批量处理复杂参数
2. **探索不同模型**：千问vs万相的差异化能力
3. **尝试不同尺寸**：根据使用场景选择最佳比例

---

## 📞 技术支持
- **官方文档**: https://help.aliyun.com/document_detail/2587504.html
- **提示词指南**: docs/text2image_prompt_guide.md
- **完整API参考**: docs/api_reference.md

---

## 🔄 版本更新
- **v1.0**: 基础文生图功能 (`text2image.py`)
- **v1.1**: 千问/万相双模型支持
- **v1.2**: 即将推出文生文 (`text2text.py`)
- **v1.3**: 即将推出文生视频 (`text2video.py`)
- **v1.4**: 即将推出语音功能 (`text2speech.py`, `speech2text.py`)