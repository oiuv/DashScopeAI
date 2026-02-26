#!/usr/bin/env python3
"""
DashScope CLI 入口点脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from cli.main import main

if __name__ == '__main__':
    sys.exit(main())
