#!/usr/bin/env python3
"""
DashScope CLI 入口点
"""

from .main import main

if __name__ == '__main__':
    import sys
    import os
    # Windows 控制台 UTF-8 编码支持
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul')
    sys.exit(main())
