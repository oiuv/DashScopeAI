# 🚀 快速开始 - 直接生成图片

## 多种输入方式，支持文件读取

### 1. 设置API密钥（仅需一次）
```bash
# Windows
set DASHSCOPE_API_KEY=sk-你的阿里云百炼密钥

# Linux/Mac
export DASHSCOPE_API_KEY=sk-你的阿里云百炼密钥
```

### 2. 直接生成图片

#### **方式1：命令行直接输入**
```bash
python generate.py "一只可爱的猫咪"
```

#### **方式2：从文本文件读取**
```bash
# 使用示例文件
python generate.py -f examples/prompts.txt

# 使用自己的文本文件
python generate.py -f my_prompts.txt
```

**文本文件格式** (`my_prompts.txt`):
```
# 这是注释，会被忽略
一只可爱的橘猫，卡通风格
山水画，青山绿水，水墨风格
古风美女，汉服，樱花树下
```

#### **方式3：从JSON文件读取（推荐）**
```bash
# 使用示例文件
python generate.py -f examples/prompts.json

# 使用自己的JSON文件
python generate.py -f my_config.json
```

**JSON文件格式** (`my_config.json`):
```json
{
  "prompts": [
    {
      "prompt": "详细的提示词描述",
      "negative": "不希望在图像中出现的内容",
      "size": "1472*1140",
      "watermark": false,
      "filename": "custom_name.png"
    }
  ]
}
```

#### **方式4：批量处理**
```bash
# 批量生成多个图片
python generate.py -b examples/prompts.json
```

### 3. 命令行参数

#### **通用参数**
```bash
python generate.py [输入方式] [选项]

输入方式（三选一）:
  "直接提示词"           直接输入提示词
  -f, --file FILE       从文件读取提示词
  -b, --batch FILE      批量处理JSON文件

选项:
  --size SIZE           图像尺寸 (1328*1328/1664*928/1472*1140/1140*1472/928*1664)
  --negative TEXT       反向提示词
  --api-key KEY         API密钥
  --output DIR          输出目录 (默认: ./generated_images)
  --filename NAME       输出文件名
  --no-watermark        不添加水印
  --no-extend           不开启智能改写
```

### 4. 使用示例

#### **简单文本文件使用**
创建 `my_prompts.txt`:
```
# 可爱动物
一只微笑的柴犬，白色背景，卡通风格
小熊猫抱着竹子，森林环境，写实风格

# 风景
中国山水画，青山绿水，晨雾缭绕
樱花盛开的日本街道，粉色花瓣飘落

# 人物
古风美女，汉服，樱花树下，唯美光线
赛博朋克女孩，霓虹灯下，未来城市背景
```

运行：
```bash
python generate.py -f my_prompts.txt
```

#### **高级JSON文件使用**
创建 `advanced_config.json`:
```json
{
  "prompts": [
    {
      "prompt": "宫崎骏风格，阳光下的古街，青衫弟子手拿阿里云卡片",
      "negative": "模糊,低质量,畸形",
      "size": "1472*1140",
      "watermark": false,
      "filename": "阿里云古风街景.png"
    },
    {
      "prompt": "未来科技实验室，全息投影，科学家操作AI界面",
      "negative": "黑暗,混乱,低分辨率",
      "size": "1664*928",
      "watermark": false,
      "filename": "未来实验室.png"
    }
  ]
}
```

#### **批量生成**
```bash
# 批量生成所有配置
python generate.py -b advanced_config.json

# 批量生成到指定目录
python generate.py -b advanced_config.json --output ./my_images
```

#### **组合使用**
```bash
# 从文件读取，指定输出目录
python generate.py -f my_prompts.txt --output ./cute_animals --size 1328*1328

# 批量处理，自定义设置
python generate.py -b batch_config.json --no-watermark --output ./high_quality
```

### 5. 支持的文件格式

#### **文本文件 (.txt)**
- 每行一个提示词
- 支持空行（自动忽略）
- 支持注释（以#开头）

#### **JSON文件 (.json)**
- 结构化配置
- 支持完整参数（提示词、反向提示、尺寸、文件名等）
- 支持批量处理

### 6. 输出结果

所有生成的图片会自动保存在：
- 默认：`./generated_images/`
- 自定义：`--output` 指定的目录

文件命名：
- 文本文件：自动生成（基于提示词内容）
- JSON文件：使用配置的`filename`字段

### 7. 快速测试

```bash
# 测试文本文件
python generate.py -f examples/prompts.txt

# 测试JSON文件
python generate.py -f examples/prompts.json

# 测试批量处理
python generate.py -b examples/prompts.json
```

现在你可以：
- ✅ 直接在命令行输入提示词
- ✅ 从文本文件批量读取简单提示词
- ✅ 从JSON文件读取完整配置
- ✅ 批量生成多张图片
- ✅ 管理复杂的提示词集合