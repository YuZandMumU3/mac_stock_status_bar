#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票监控配置入口
"""

import os
import sys
import subprocess

def main():
    """主配置入口"""
    print("🔧 股票监控配置")
    print("=" * 20)
    print()
    print("选择配置方式:")
    print("1. 🚀 快捷配置 (推荐)")
    print("2. 🖥️  图形配置")
    print("3. 📋 查看当前配置")
    print("0. 退出")
    print()
    
    while True:
        choice = input("请选择 (0-3): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == "1":
            subprocess.run([sys.executable, "tools/quick_config.py"])
            break
        elif choice == "2":
            subprocess.run([sys.executable, "tools/config_gui.py"])
            break
        elif choice == "3":
            subprocess.run([sys.executable, "tools/config.py"])
            break
        else:
            print("❌ 请输入 0-3 之间的数字")

if __name__ == "__main__":
    main() 