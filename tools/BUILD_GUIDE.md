# 千问水印去除GUI工具打包指南

## 快速打包（推荐）

### 1. 安装依赖
```bash
cd tools
pip install -r requirements-gui.txt
pip install pyinstaller
```

### 2. 一键打包
```bash
python build_exe.py
```

选择打包类型：
- 输入 `1`：发布版本（无控制台窗口）
- 输入 `2`：调试版本（带控制台窗口）

## 手动打包（高级用户）

### 发布版本
```bash
pyinstaller --name="千问水印去除工具" \
           --windowed \
           --onefile \
           --add-data="watermark_remover_config.json;." \
           watermark_remover_gui.py
```

### 调试版本
```bash
pyinstaller --name="千问水印去除工具-调试版" \
           --onefile \
           --console \
           --add-data="watermark_remover_config.json;." \
           watermark_remover_gui.py
```

## 输出文件

打包完成后，生成的exe文件位于：
- `dist/千问水印去除工具.exe`（发布版）
- `dist/千问水印去除工具-调试版.exe`（调试版）

## 文件说明

- `watermark_remover_gui.py` - 主程序
- `requirements-gui.txt` - GUI专用依赖
- `build_exe.py` - 一键打包脚本
- `BUILD_GUIDE.md` - 本打包指南

## 注意事项

1. **首次运行**：需要在有网络环境下初始化配置
2. **文件大小**：打包后exe约50-80MB（包含Python运行时）
3. **兼容性**：Windows 7/8/10/11 64位系统
4. **权限**：需要管理员权限安装依赖

## 分发说明

员工使用时只需：
1. 下载 `千问水印去除工具.exe`
2. 双击运行
3. 输入API密钥
4. 选择图片和输出目录
5. 开始处理

无需安装Python环境，开箱即用！