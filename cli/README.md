# DashScope CLI - 阿里百炼大模型统一命令行工具

统一 CLI 入口，提供便捷的子命令方式来使用阿里百炼大模型的各项功能。

## 安装与配置

### 环境变量

设置 API 密钥（必需）：
```bash
# Windows
set DASHSCOPE_API_KEY=sk-你的密钥

# Linux/Mac
export DASHSCOPE_API_KEY=sk-你的密钥
```

## 使用方法

### 运行方式

```bash
# 方式 1：使用模块运行
python -m cli --help

# 方式 2：使用入口脚本
python dashscope-cli.py --help
```

### 子命令列表

| 子命令 | 功能 | 说明 |
|--------|------|------|
| `text2image` | 文生图 | 根据文本描述生成图像 |
| `image-edit` | 图像编辑 | 编辑现有图像 |
| `sketch2image` | 涂鸦作画 | 根据草图和描述生成图像 |
| `style-repaint` | 人像重绘 | 人像风格转换 |
| `speech-rec` | 语音识别 | 实时语音转文字 |
| `batch-edit` | 批量编辑 | 批量处理图像编辑任务 |

### 共享参数

所有子命令都支持以下共享参数：

- `-k, --api-key`: API 密钥（也可通过环境变量设置）
- `-o, --output`: 输出目录
- `-w, --watermark`: 添加水印标识
- `-v, --verbose`: 显示详细信息

## 子命令详解

### 1. text2image - 文生图

根据文本描述生成精美图像。

```bash
# 基础用法
python -m cli text2image "一只可爱的猫咪"

# 指定模型
python -m cli text2image "赛博朋克城市" -m wan2.2-t2i-plus

# 指定尺寸和数量
python -m cli text2image "未来城市夜景" -s 1440*810 -n 2

# 使用配置文件批量处理
python -m cli text2image -f prompts.json

# 反向提示词
python -m cli text2image "美丽的花" -N "模糊，低质量"

# 关闭智能提示词改写
python -m cli text2image "简单图形" -x
```

**参数说明：**
- `prompt`: 生成图像的文本描述
- `-m, --model`: 模型选择
  - `qwen-image`: 通义千问（中文文字渲染优秀）
  - `wan2.2-t2i-flash`: 极速生成
  - `wan2.2-t2i-plus`: 高质量生成
  - `wanx2.1-t2i-turbo`: 极速版
  - `wanx2.1-t2i-plus`: 专业版
- `-s, --size`: 图像尺寸（格式：宽*高）
- `-n, --n`: 生成图片数量（1-4，千问模型仅支持 1 张）
- `-S, --seed`: 随机种子
- `-N, --negative`: 反向提示词

### 2. image-edit - 图像编辑

编辑现有图像，支持千问和万相两种模型。

```bash
# 千问模型 - 同步返回，适合文字/物体编辑
python -m cli image-edit input.jpg "将狗改为站立姿势" -m qwen-image-edit

# 万相模型 - 全局风格化
python -m cli image-edit input.jpg "法国绘本风格" -m wanx2.1-imageedit -f stylization_all

# 万相模型 - 局部重绘（需要 mask）
python -m cli image-edit base.jpg mask.png "添加陶瓷兔子" -f description_edit_with_mask

# 万相模型 - 超分辨率
python -m cli image-edit blurry.jpg "高清放大" -f super_resolution --upscale-factor 2

# 万相模型 - 扩图
python -m cli image-edit portrait.jpg "一家人在公园" -f expand --top-scale 1.5 --left-scale 1.2
```

**万相 9 大功能：**
- `stylization_all`: 全局风格化
- `stylization_local`: 局部风格化
- `description_edit`: 指令编辑
- `description_edit_with_mask`: 局部重绘
- `remove_watermark`: 去水印
- `expand`: 扩图
- `super_resolution`: 超分辨率
- `colorization`: 黑白上色
- `doodle`: 线稿生图

### 3. sketch2image - 涂鸦作画

根据草图和文本描述生成图像。

```bash
# 基础用法
python -m cli sketch2image sketch.png "一只可爱的猫咪"

# 指定风格
python -m cli sketch2image sketch.png "美丽的风景" --style anime

# 指定草图权重
python -m cli sketch2image sketch.png "未来城市" --weight 8

# 等待完成后下载
python -m cli sketch2image sketch.png "童话世界" --wait
```

**可用风格：**
- `auto`: 自动随机选择
- `3d_cartoon`: 3D 卡通
- `anime`: 动漫
- `oil_painting`: 油画
- `watercolor`: 水彩
- `sketch`: 素描
- `chinese_painting`: 中国画
- `flat_illustration`: 扁平插画

### 4. style-repaint - 人像风格重绘

将人像照片转换为不同艺术风格。

```bash
# 使用预置风格
python -m cli style-repaint person.jpg 3

# 使用自定义风格参考
python -m cli style-repaint person.jpg --style-ref style.jpg

# 查看可用风格
python -m cli style-repaint --styles

# 批量处理
python -m cli style-repaint -f style_repaint_configs.json
```

**预置风格编号：**
- 0: 复古漫画 | 1: 3D 童话 | 2: 二次元 | 3: 小清新
- 4: 未来科技 | 5: 国画古风 | 6: 将军百战 | 7: 炫彩卡通
- 8: 清雅国风 | 9: 喜迎新年 | 14: 国风工笔 | 15: 恭贺新禧
- 30: 童话世界 | 31: 黏土世界 | 32: 像素世界 | ...更多

### 5. speech-rec - 语音识别

实时语音转文字，支持麦克风和扬声器两种模式。

```bash
# 麦克风模式
python -m cli speech-rec --mode mic

# 扬声器模式（识别电脑播放的声音）
python -m cli speech-rec --mode speaker

# 列出所有音频设备
python -m cli speech-rec --list

# 测试音频设置
python -m cli speech-rec --test --mode mic

# 指定音频设备
python -m cli speech-rec --mode mic --device 3
```

### 6. batch-edit - 批量图像编辑

根据配置文件批量处理图像编辑任务。

```bash
# 基础用法
python -m cli batch-edit config.json

# 指定输出目录
python -m cli batch-edit config.json -o ./results

# 处理指定范围的创作
python -m cli batch-edit config.json -s 1 -e 5

# 试运行（不实际处理）
python -m cli batch-edit config.json --dry-run
```

## 配置文件格式

### 文生图 JSON 配置

```json
{
  "prompts": [
    {
      "prompt": "一只可爱的猫咪",
      "negative": "模糊，低质量",
      "size": "1024*1024",
      "model": "wan2.2-t2i-flash",
      "watermark": false,
      "filename": "cat.png"
    }
  ]
}
```

### 文生图 TXT 配置

```
# 注释以#开头
一只可爱的猫咪坐在窗台上
美丽的风景与山脉

未来城市夜景
```

### 批量图像编辑配置

```json
{
  "project_name": "我的创作集",
  "base_image": "base.jpg",
  "output_directory": "./output",
  "creations": [
    {
      "id": 1,
      "name": "创作 1",
      "prompt": "添加春节元素",
      "model": "wanx2.1-imageedit",
      "function": "stylization_all",
      "filename": "creation_1.png"
    }
  ]
}
```

## 常见问题

### API 密钥错误
```
❌ 错误：未找到 API 密钥
```
解决：设置 `DASHSCOPE_API_KEY` 环境变量或使用 `-k` 参数

### 模块不存在
```
ModuleNotFoundError: No module named 'pyaudio'
```
解决：语音识别功能需要安装 pyaudio
```bash
pip install pyaudio
# Windows 用户
pip install pipwin && pipwin install pyaudio
```

### 图像生成失败
检查：
1. API 密钥是否有效
2. 提示词是否合规
3. 图像尺寸是否符合模型要求

## 开发信息

### 项目结构
```
cli/
├── __init__.py
├── __main__.py      # 模块入口
├── main.py          # 主程序
├── commands/        # 子命令模块
│   ├── text2image.py
│   ├── image_edit.py
│   ├── sketch2image.py
│   ├── style_repaint.py
│   ├── speech_rec.py
│   └── batch_edit.py
└── shared/          # 共享工具
    ├── config.py    # 配置管理
    ├── validators.py # 参数验证
    └── output.py    # 输出处理
```

### 添加新子命令

1. 在 `cli/commands/` 创建新模块
2. 实现 `add_arguments(parser)` 函数
3. 实现 `execute(args)` 函数
4. 在 `cli/main.py` 的 `SUBCOMMANDS` 中注册

## 版本

当前版本：1.0.0

## 许可证

MIT License
