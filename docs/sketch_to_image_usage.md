# 通义万相-涂鸦作画使用指南

## 功能概述
使用通义万相-涂鸦作画模型将手绘草图转换为精美绘画作品，支持多种艺术风格。

## 快速开始

### 命令行工具
```bash
# 基本使用
python sketch_to_image.py sketch.jpg "美丽的花朵"

# 指定风格和参数
python sketch_to_image.py sketch.jpg "梦幻城堡" --style watercolor --weight 5 --n 2

# 等待模式（同步返回结果）
python sketch_to_image.py sketch.jpg "山水画" --wait
```

### 图形界面工具
```bash
# 启动GUI
python tools/sketch_to_image_gui.py
```

## 支持的绘画风格

| 风格名称 | 风格描述 | 参数值 |
|---------|----------|--------|
| 自动 | 随机选择风格 | auto |
| 3D卡通 | 三维卡通效果 | 3d_cartoon |
| 二次元 | 动漫风格 | anime |
| 油画 | 油画效果 | oil_painting |
| 水彩 | 水彩画风格 | watercolor |
| 素描 | 素描效果 | sketch |
| 中国画 | 中国传统绘画 | chinese_painting |
| 扁平插画 | 现代插画风格 | flat_illustration |

## 参数说明

### 通用参数
- **prompt**: 描述文字，最多75个字符
- **sketch**: 草图文件路径（支持JPG、PNG、TIFF、WEBP）
- **style**: 绘画风格，默认为auto
- **weight**: 草图权重（0-10），默认为5
- **n**: 生成数量（1-4张），默认为1
- **output**: 输出目录，默认为./output

### 草图要求
- **格式**: JPG、JPEG、PNG、TIFF、WEBP
- **大小**: ≤10MB
- **分辨率**: 256×256 到 2048×2048像素
- **建议**: 白色背景+黑色线条，保持清晰对比

## 使用示例

### 示例1：简单涂鸦转水彩
```bash
python sketch_to_image.py examples/sketches/simple_drawing.png "一座小房子"
```

### 示例2：指定风格生成
```bash
python sketch_to_image.py sketches/cat.png "可爱的猫咪" --style anime --weight 7 --n 3
```

### 示例3：批量处理
```bash
# 使用配置文件批量处理
python sketch_to_image.py -f examples/sketch_batch.json --output ./results
```

## GUI操作指南

1. **启动应用**
   ```bash
   python tools/sketch_to_image_gui.py
   ```

2. **使用步骤**
   - 输入API密钥（首次使用）
   - 选择草图文件
   - 输入描述文字（≤75字符）
   - 选择绘画风格
   - 设置生成数量（1-4张）
   - 调整草图权重（0-10，默认5）
   - 选择输出目录
   - 点击"开始生成"

3. **功能特点**
   - 实时预览草图
   - 字符计数器
   - 进度显示
   - 结果实时显示
   - 支持任务取消

## 常见问题

### Q: 草图需要什么格式？
A: 支持JPG、PNG、TIFF、WEBP格式，最大10MB

### Q: 为什么只能生成768×768的图片？
A: 当前API版本仅支持768×768正方形输出

### Q: 草图权重是什么意思？
A: 权重越高，生成的图片越接近原始草图；权重越低，AI创意空间越大

### Q: 如何获得更好的效果？
A: 
- 使用清晰的线条，避免复杂细节
- 保持线条与背景对比明显
- 描述文字具体明确
- 尝试不同风格和权重组合

## 计费信息
- **免费额度**: 500张（有效期180天）
- **计费单价**: 0.06元/张
- **限流**: 2 QPS
- **并发限制**: 同时处理1个任务

## 相关文件
- `sketch_to_image.py` - 命令行工具
- `tools/sketch_to_image_gui.py` - 图形界面
- `src/image/sketch_to_image.py` - 核心API封装
- `tools/tools_config.py` - 配置管理