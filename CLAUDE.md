# CLAUDE.md

这个文件为 Claude Code (claude.ai/code) 在这个代码仓库中工作时提供指导。

## 项目概述

**阿里百炼大模型工具集** - Alibaba Bailian Large Model Toolkit
基于阿里云百炼API的综合AI内容生成平台，支持文生图、文生文、文生视频、语音合成和向量化服务。

## 架构

### 核心结构
```
src/
├── image/           # 文生图模块（主要模块）
│   ├── text2image.py    # Text2ImageGenerator主类
│   ├── models.py        # Pydantic请求/响应模型
│   └── __init__.py
├── utils/           # 工具模块
│   └── file_utils.py    # 提示词文件处理
├── text/            # 文生文（待开发）
├── video/           # 文生视频（待开发）
├── audio/           # 音频处理（待开发）
├── vector/          # 向量化服务（待开发）
└── chat/            # 对话模型（待开发）
```

### 关键模型
- **Text2ImageGenerator**: 图像生成主类，支持同步/异步调用
- **ImageGenerationRequest**: Pydantic请求模型
- **ImageGenerationResponse**: Pydantic响应模型

## 开发命令

### 安装配置
```bash
# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -e ".[dev]"

# 设置API密钥（必需）
export DASHSCOPE_API_KEY=sk-你的密钥
# Windows系统：
set DASHSCOPE_API_KEY=sk-你的密钥
```

### 运行应用
```bash
# 基础文生图生成
python text2image.py "一只可爱的猫咪"

# 使用配置文件
python text2image.py -f examples/prompts.json

# 高级参数使用
python text2image.py "赛博朋克城市" --model wan2.2-t2i-plus --size 1440*810 --n 2

# 批量处理
python text2image.py -f examples/prompts.txt --output ./batch_results
```

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_text2image.py

# 带覆盖率测试
pytest --cov=src tests/

# 代码检查
flake8 src/
black src/
mypy src/
```

## API使用模式

### 图像生成
```python
from src.image import Text2ImageGenerator

# 初始化
generator = Text2ImageGenerator(api_key="你的密钥")

# 生成单张图片
result = generator.generate_image(
    prompt="美丽的风景",
    size="1024*1024",
    model="wan2.2-t2i-flash"
)

# 批量处理
configs = [
    {"prompt": "猫咪", "size": "512*512"},
    {"prompt": "小狗", "size": "1024*1024"}
]
```

### 支持的模型
- **qwen-image**: 通义千问模型（中文文字渲染优秀）
- **wan2.2-t2i-flash**: 极速生成（512-1440像素，1-4张图）
- **wan2.2-t2i-plus**: 高质量生成（512-1440像素，1-4张图）
- **wanx2.1-t2i-turbo**: 极速版（512-1440像素）
- **wanx2.1-t2i-plus**: 专业版（512-1440像素）

### 尺寸限制
- **千问模型**: 固定尺寸：1328×1328、1664×928、1472×1140、1140×1472、928×1664
- **万相模型**: 512-1440像素任意组合，最大200万像素

## 文件格式

### JSON配置文件格式
```json
{
  "prompts": [
    {
      "prompt": "提示词文本",
      "negative": "要避免的内容",
      "size": "1024*1024",
      "model": "wan2.2-t2i-flash",
      "watermark": false,
      "filename": "自定义名称.png"
    }
  ]
}
```

### 文本文件格式
```
# 注释以#开头
一只可爱的猫咪坐在窗台上
美丽的风景与山脉
# 空行会被忽略

未来城市夜景
```

## 图像编辑功能

### 支持的编辑模型
- **qwen-image-edit**: 通义千问-图像编辑（同步接口，0.3元/张）
  - 文字编辑、物体增删、姿势调整、风格迁移
- **wanx2.1-imageedit**: 万相-通用图像编辑（异步接口，0.14元/张）
  - 9大功能：全局风格化、局部风格化、指令编辑、局部重绘、去水印、扩图、超分、上色、线稿生图

### 图像编辑命令
```bash
# 千问编辑 - 同步
python image_edit.py input.jpg "将狗改为站立姿势" --model qwen-image-edit

# 万相全局风格化
python image_edit.py input.jpg "转换成法国绘本风格" --model wanx2.1-imageedit --function stylization_all

# 万相局部重绘（需要mask）
python image_edit.py base.jpg mask.png "添加陶瓷兔子" --function description_edit_with_mask

# 批量处理示例文件
python image_edit.py -f examples/image_edit_examples.json
```

### 万相9大编辑功能
- `stylization_all`: 全局风格化
- `stylization_local`: 局部风格化
- `description_edit`: 指令编辑
- `description_edit_with_mask`: 局部重绘
- `remove_watermark`: 去水印
- `expand`: 扩图
- `super_resolution`: 超分辨率
- `colorization`: 黑白上色
- `doodle`: 线稿生图

### mask图像创建工具
```bash
# 创建矩形mask
python -m src.utils.mask_utils photo.jpg --type rectangle --coords 100 100 200 150 --output mask.png

# 创建圆形mask
python -m src.utils.mask_utils photo.jpg --type circle --coords 200 150 50 --output mask.png

# 基于颜色创建智能mask
python -m src.utils.mask_utils photo.jpg --color 255 0 0 --tolerance 30 --output red_mask.png
```

## 常见开发任务

### 添加新编辑模型
1. 在 `src/image/models.py` 中添加新的ModelType枚举
2. 在 `ImageEditor` 类中添加对应的方法
3. 在 `image_edit.py` 中添加CLI支持

### 使用图像编辑API
```python
from src.image import ImageEditor, WanxImageEditor

# 统一接口
editor = ImageEditor()
result = editor.edit_image(
    model="wanx2.1-imageedit",
    function="stylization_all",
    image_url="input.jpg",
    prompt="法国绘本风格"
)

# 专用类
wanx_editor = WanxImageEditor()
result = wanx_editor.stylization_all("input.jpg", "法国绘本风格")
```

### 调试技巧
- 使用 `echo $DASHSCOPE_API_KEY` 检查API密钥有效性
- 千问模型同步返回，万相模型需轮询状态
- 检查 `edited_images/` 目录中的输出文件
- mask图像必须为灰度图，白色区域为编辑区域

## 环境变量
- `DASHSCOPE_API_KEY`: 阿里云百炼必需API密钥
- `DASHSCOPE_BASE_URL`: 可选自定义API端点

## 错误处理
常见错误模式：
- `429`: 限流 - 实现指数退避
- `400`: 参数无效 - 检查图像格式和尺寸限制
- `401`: 认证失败 - 验证API密钥
- 图像规格错误：千问384×384-3072×3072，万相512×512-4096×4096

## 测试策略
- `tests/test_image_edit.py` 中的编辑功能单元测试
- mask图像验证测试
- 不同模型间的兼容性测试
- 异步任务状态轮询测试
- 实际API调用测试（需要有效API密钥）

## 关键依赖
- `httpx`: API调用的HTTP客户端
- `pydantic`: 数据验证
- `pillow`: 图像处理和mask创建
- `numpy`: mask数组操作