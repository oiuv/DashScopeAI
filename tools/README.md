# 阿里百炼GUI工具集

这个目录包含基于阿里云百炼API的各种GUI工具。

## 工具列表

### 1. 海报生成器 (poster_generator_gui.py)
- 使用通义千问图像模型生成海报
- 支持中文提示词和视觉要求
- 实时预览和下载功能

### 2. 水印去除器 (watermark_remover_gui.py)
- 使用万相模型去除图片水印
- 支持批量处理
- 保持原始图片质量

### 3. 图片调整器 (image_resizer.py)
- 批量调整图片尺寸
- 保持宽高比例
- 支持多种输出格式

## 打包说明

使用 `build_exe.py` 打包任意GUI工具为Windows可执行文件：

```bash
# 运行交互式打包程序
python tools/build_exe.py

# 按提示选择：
# 1. 选择要打包的GUI脚本
# 2. 选择打包类型（发布版/调试版）
# 3. 选择是否包含额外数据文件
```

## 依赖安装

```bash
# 安装所有依赖
pip install -r tools/requirements.txt

# 安装打包工具
pip install pyinstaller
```

## 配置文件

- `tools_config.py` - 统一配置管理
- `tools_config.json` - API密钥配置（已排除版本控制）

## 注意事项

- 打包前确保已设置 `DASHSCOPE_API_KEY` 环境变量
- 生成的exe文件位于项目根目录的 `dist/` 文件夹中
- 首次运行可能需要管理员权限