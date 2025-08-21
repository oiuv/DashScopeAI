#!/usr/bin/env python3
"""
打包千问水印去除GUI工具为exe文件的构建脚本
"""

import os
import sys
from pathlib import Path

def install_requirements():
    """安装打包依赖"""
    print("📦 安装打包依赖...")
    os.system(f"{sys.executable} -m pip install --user pyinstaller")
    os.system(f"{sys.executable} -m pip install --user requests")

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")
    
    # 打包命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=千问水印去除工具",
        "--windowed",
        "--onefile",
        "--add-data=tools/watermark_remover_config.json;.",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--clean",
        "--noconfirm",
        "tools/watermark_remover_gui.py"
    ]
    
    # 执行打包
    result = os.system(" ".join(cmd))
    
    if result == 0:
        print("✅ 打包成功！")
        print(f"📁 输出目录: {Path('dist').absolute()}")
        print(f"📁 可执行文件: {Path('dist/千问水印去除工具.exe').absolute()}")
    else:
        print("❌ 打包失败")
        sys.exit(1)

def build_with_console():
    """构建带控制台的版本（调试用）"""
    print("🔧 构建调试版本...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=千问水印去除工具-调试版",
        "--onefile",
        "--console",
        "--add-data=tools/watermark_remover_config.json;.",
        "--clean",
        "--noconfirm",
        "tools/watermark_remover_gui.py"
    ]
    
    os.system(" ".join(cmd))

def main():
    """主函数"""
    print("🚀 千问水印去除工具打包程序")
    print("=" * 50)
    
    # 检查当前目录
    gui_script = Path("tools/watermark_remover_gui.py")
    if not gui_script.exists():
        print("❌ 未找到 GUI 脚本，请确保在项目根目录运行")
        print("当前目录:", Path.cwd())
        print("预期文件:", gui_script.absolute())
        sys.exit(1)
    
    # 安装依赖
    install_requirements()
    
    # 询问打包类型
    print("\n选择打包类型:")
    print("1. 正式发布版本 (无控制台)")
    print("2. 调试版本 (带控制台)")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        build_exe()
    elif choice == "2":
        build_with_console()
    else:
        print("❌ 无效选择")
        sys.exit(1)

if __name__ == "__main__":
    main()