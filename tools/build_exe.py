#!/usr/bin/env python3
"""
通用GUI工具打包脚本 - 为tools目录下任意GUI脚本生成exe
"""

import os
import sys
from pathlib import Path
import glob

def install_requirements():
    """安装打包依赖"""
    print("📦 安装打包依赖...")
    os.system(f"{sys.executable} -m pip install --user pyinstaller")
    os.system(f"{sys.executable} -m pip install --user requests")
    os.system(f"{sys.executable} -m pip install --user pillow")

def list_available_scripts():
    """列出tools目录下所有可用的Python GUI脚本"""
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ 未找到tools目录")
        return []
    
    scripts = []
    for py_file in tools_dir.glob("*.py"):
        if py_file.name != "build_exe.py":  # 排除打包脚本本身
            scripts.append(py_file)
    
    return scripts

def build_exe(script_path, app_name=None, console=False, additional_data=None):
    """构建exe文件"""
    script_path = Path(script_path)
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    if app_name is None:
        app_name = script_path.stem.replace('_gui', '').replace('_', ' ').title()
    
    print(f"🔨 开始构建: {app_name}")
    
    # 基础命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f'"--name={app_name}"',
        "--onefile",
        "--clean",
        "--noconfirm",
        "--add-data", f'"{Path(__file__).parent / "tools_config.py"};."',
        "--add-data", f'"{Path(__file__).parent / "requirements.txt"};."'
    ]
    
    # 是否带控制台
    if console:
        cmd.append("--console")
    else:
        cmd.append("--windowed")
    
    # 添加常用隐藏导入
    hidden_imports = [
        "tkinter", "tkinter.ttk", "tkinter.filedialog", 
        "tkinter.messagebox", "tkinter.simpledialog"
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # 添加额外数据文件
    if additional_data:
        for data_path in additional_data:
            if Path(data_path).exists():
                cmd.extend(["--add-data", f'"{data_path};."'])
    
    # 添加脚本
    cmd.append(f'"{str(script_path)}"')
    
    print("📋 打包命令:", " ".join(cmd))
    
    # 执行打包
    result = os.system(" ".join(cmd))
    
    if result == 0:
        print("✅ 打包成功！")
        print(f"📁 输出目录: {Path('dist').absolute()}")
        print(f"📁 可执行文件: {Path(f'dist/{app_name}.exe').absolute()}")
        return True
    else:
        print("❌ 打包失败")
        return False

def interactive_select_script():
    """交互式选择要打包的脚本"""
    scripts = list_available_scripts()
    
    if not scripts:
        print("❌ tools目录下未找到可用的Python脚本")
        return None
    
    print("\n📁 发现以下可用的GUI脚本:")
    for i, script in enumerate(scripts, 1):
        print(f"{i}. {script.name}")
    
    try:
        choice = int(input("\n请选择要打包的脚本编号: ").strip())
        if 1 <= choice <= len(scripts):
            return scripts[choice-1]
        else:
            print("❌ 无效的选择")
            return None
    except ValueError:
        print("❌ 请输入有效的数字")
        return None

def main():
    """主函数"""
    print("🚀 通用GUI工具打包程序")
    print("=" * 60)
    print("支持打包tools目录下任意Python GUI脚本为exe")
    print("=" * 60)
    
    # 检查tools目录
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ 未找到tools目录，请确保在项目根目录运行")
        print("当前目录:", Path.cwd())
        sys.exit(1)
    
    # 安装依赖
    install_requirements()
    
    # 选择打包脚本
    selected_script = interactive_select_script()
    if not selected_script:
        sys.exit(1)
    
    # 询问打包类型
    print(f"\n📋 已选择打包: {selected_script.name}")
    print("\n选择打包类型:")
    print("1. 正式发布版本 (无控制台)")
    print("2. 调试版本 (带控制台)")
    
    choice = input("请选择 (1/2): ").strip()
    
    # 询问数据文件
    additional_data = []
    data_choice = input("是否包含额外数据文件？(y/n): ").strip().lower()
    if data_choice == 'y':
        data_path = input("请输入数据文件路径（相对tools目录）: ").strip()
        if data_path:
            full_path = tools_dir / data_path
            if full_path.exists():
                additional_data.append(str(full_path))
                print(f"✅ 已添加数据文件: {data_path}")
            else:
                print(f"⚠️ 数据文件不存在: {full_path}")
    
    # 执行打包
    console_mode = choice == "2"
    success = build_exe(selected_script, console=console_mode, additional_data=additional_data)
    
    if success:
        print("\n🎉 打包完成！")
        print("💡 生成的exe文件位于 dist/ 目录下")
    else:
        print("\n❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print("🚀 通用GUI工具打包程序")
        print("=" * 60)
        print("支持打包tools目录下任意Python GUI脚本为exe")
        print("=" * 60)
        print("\n使用方法: python build_exe.py")
        print("\n将按照交互式流程选择脚本和配置")
        print("\n可选参数:")
        print("  -h, --help    显示此帮助信息")
    else:
        main()