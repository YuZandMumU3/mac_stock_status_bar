#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一配置入口
让用户选择最适合的配置方式
"""

import sys
import os
import subprocess

def show_menu():
    """显示配置选项菜单"""
    print("🔧 股票监控配置工具")
    print("=" * 25)
    print()
    print("选择配置方式:")
    print("1. 🚀 快捷配置 (推荐) - 命令行界面，简单快速")
    print("2. 🖥️  图形配置 - 可视化界面，直观易用")
    print("3. 📝 手动编辑 - 直接编辑配置文件")
    print("4. 📋 查看配置 - 显示当前配置内容")
    print("0. 🚪 退出")
    print()

def run_quick_config():
    """运行快捷配置"""
    try:
        subprocess.run([sys.executable, "quick_config.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 快捷配置工具启动失败")
    except FileNotFoundError:
        print("❌ 找不到快捷配置工具")

def run_gui_config():
    """运行图形配置"""
    try:
        subprocess.run([sys.executable, "config_gui.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 图形配置工具启动失败")
    except FileNotFoundError:
        print("❌ 找不到图形配置工具")
    except ImportError:
        print("❌ 缺少图形界面库，请安装: pip install tk")

def edit_config_file():
    """编辑配置文件"""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在，请先运行快捷配置创建")
        return
    
    try:
        # 尝试用不同的编辑器打开
        editors = ["code", "nano", "vim", "open"]
        
        for editor in editors:
            try:
                if editor == "open":  # macOS 默认应用
                    subprocess.run([editor, config_file], check=True)
                else:
                    subprocess.run([editor, config_file], check=True)
                print(f"✅ 已用 {editor} 打开配置文件")
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        # 如果所有编辑器都失败，显示文件内容
        print("📝 配置文件内容:")
        print("-" * 40)
        with open(config_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 40)
        print("💡 请手动编辑 config.json 文件")
        
    except Exception as e:
        print(f"❌ 打开配置文件失败: {e}")

def show_current_config():
    """显示当前配置"""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return
    
    try:
        import json
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📋 当前配置:")
        print("-" * 30)
        
        # 基本信息
        print(f"⏰ 更新间隔: {config.get('update_interval', 5)} 秒")
        print(f"📱 显示格式: {config.get('display_format', '')}")
        
        # 股票信息
        stock_info = config.get('stock_info', {})
        if stock_info.get('enabled', False):
            print(f"📊 监控股票: {', '.join(stock_info.get('symbols', []))}")
            print(f"🎨 颜色指示: {'启用' if stock_info.get('use_color_indicators', True) else '禁用'}")
            
            if stock_info.get('show_multiple', False):
                print("📱 显示模式: 同时显示多只")
            elif stock_info.get('rotate_stocks', False):
                interval = stock_info.get('rotate_interval', 10)
                print(f"📱 显示模式: 轮换显示 (每{interval}次更新)")
            else:
                print("📱 显示模式: 只显示一只")
        else:
            print("📊 股票监控: 已禁用")
        
        print("-" * 30)
        
    except json.JSONDecodeError:
        print("❌ 配置文件格式错误")
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")

def main():
    """主函数"""
    try:
        while True:
            show_menu()
            
            choice = input("请选择 (0-4): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                print("🚀 启动快捷配置...")
                run_quick_config()
            elif choice == "2":
                print("🖥️ 启动图形配置...")
                run_gui_config()
            elif choice == "3":
                print("📝 打开配置文件...")
                edit_config_file()
            elif choice == "4":
                show_current_config()
                input("\n按回车继续...")
            else:
                print("❌ 请输入 0-4 之间的数字")
                input("按回车继续...")
            
            print()  # 空行分隔
            
    except KeyboardInterrupt:
        print("\n\n👋 已退出配置")
    except Exception as e:
        print(f"❌ 配置工具出错: {e}")

if __name__ == "__main__":
    main() 