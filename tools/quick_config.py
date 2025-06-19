#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快捷配置工具
提供简单明了的配置选项
"""

import json
import os
from typing import Dict, Any

class QuickConfig:
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "update_interval": 5,
            "display_format": "{colored_display}",
            "stock_info": {
                "enabled": True,
                "symbols": ["600519"],
                "primary_symbol": "600519",
                "show_multiple": False,
                "rotate_stocks": False,
                "rotate_interval": 10,
                "use_color_indicators": True
            }
        }
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        print("✅ 配置已保存！")
    
    def show_current_config(self):
        """显示当前配置"""
        print("\n=== 当前配置 ===")
        stock_info = self.config.get("stock_info", {})
        
        print(f"📊 监控股票: {', '.join(stock_info.get('symbols', []))}")
        print(f"⏰ 更新间隔: {self.config.get('update_interval', 5)} 秒")
        print(f"🎨 颜色指示: {'启用' if stock_info.get('use_color_indicators', True) else '禁用'}")
        
        if stock_info.get('show_multiple', False):
            print("📱 显示模式: 同时显示多只")
        elif stock_info.get('rotate_stocks', False):
            interval = stock_info.get('rotate_interval', 10)
            print(f"📱 显示模式: 轮换显示 (每{interval}次更新)")
        else:
            print("📱 显示模式: 只显示一只")
    
    def quick_setup(self):
        """快速设置"""
        print("🚀 股票监控快速配置")
        print("=" * 30)
        
        # 选择预设方案
        print("\n选择配置方案:")
        print("1. 💼 单只股票监控 (适合专注某只股票)")
        print("2. 🔄 多股票轮换 (适合监控多只股票)")
        print("3. 📊 多股票同显 (适合大屏幕)")
        print("4. ⚙️  自定义配置")
        print("5. 📋 查看当前配置")
        print("0. 🚪 退出")
        
        while True:
            choice = input("\n请选择 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                return
            elif choice == "1":
                self.setup_single_stock()
                break
            elif choice == "2":
                self.setup_rotating_stocks()
                break
            elif choice == "3":
                self.setup_multiple_stocks()
                break
            elif choice == "4":
                self.custom_setup()
                break
            elif choice == "5":
                self.show_current_config()
                input("\n按回车继续...")
                self.quick_setup()
                return
            else:
                print("❌ 请输入 0-5 之间的数字")
    
    def setup_single_stock(self):
        """设置单只股票监控"""
        print("\n💼 单只股票监控设置")
        print("-" * 20)
        
        stock_code = self.get_stock_input("请输入股票代码")
        if not stock_code:
            return
        
        color_enabled = self.get_yes_no("启用颜色指示器？", True)
        update_interval = self.get_number_input("更新间隔(秒)", 5, 1, 300)
        
        # 更新配置
        self.config["update_interval"] = update_interval
        self.config["stock_info"] = {
            "enabled": True,
            "symbols": [stock_code],
            "primary_symbol": stock_code,
            "show_multiple": False,
            "rotate_stocks": False,
            "use_color_indicators": color_enabled
        }
        
        if color_enabled:
            self.config["display_format"] = "{colored_display}"
        else:
            self.config["display_format"] = "{stock_name} {stock_price} ({stock_change})"
        
        self.save_config()
        self.show_preview()
    
    def setup_rotating_stocks(self):
        """设置轮换股票监控"""
        print("\n🔄 多股票轮换设置")
        print("-" * 20)
        
        stocks = self.get_multiple_stocks()
        if not stocks:
            return
        
        color_enabled = self.get_yes_no("启用颜色指示器？", True)
        update_interval = self.get_number_input("更新间隔(秒)", 5, 1, 300)
        rotate_interval = self.get_number_input("轮换间隔(次更新)", 10, 1, 100)
        
        # 更新配置
        self.config["update_interval"] = update_interval
        self.config["stock_info"] = {
            "enabled": True,
            "symbols": stocks,
            "primary_symbol": stocks[0],
            "show_multiple": False,
            "rotate_stocks": True,
            "rotate_interval": rotate_interval,
            "use_color_indicators": color_enabled
        }
        
        if color_enabled:
            self.config["display_format"] = "{colored_display}"
        else:
            self.config["display_format"] = "{stock_name} {stock_price} ({stock_change})"
        
        self.save_config()
        self.show_preview()
    
    def setup_multiple_stocks(self):
        """设置多股票同时显示"""
        print("\n📊 多股票同时显示设置")
        print("-" * 20)
        
        stocks = self.get_multiple_stocks()
        if not stocks:
            return
        
        color_enabled = self.get_yes_no("启用颜色指示器？", True)
        update_interval = self.get_number_input("更新间隔(秒)", 10, 1, 300)
        
        # 更新配置
        self.config["update_interval"] = update_interval
        self.config["stock_info"] = {
            "enabled": True,
            "symbols": stocks,
            "primary_symbol": stocks[0],
            "show_multiple": True,
            "rotate_stocks": False,
            "use_color_indicators": color_enabled
        }
        
        if color_enabled:
            self.config["display_format"] = "{colored_display}"
        else:
            self.config["display_format"] = "{stock_name} {stock_price} ({stock_change})"
        
        self.save_config()
        self.show_preview()
    
    def custom_setup(self):
        """自定义设置"""
        print("\n⚙️ 自定义配置")
        print("-" * 15)
        
        print("当前配置选项:")
        print("1. 修改监控股票")
        print("2. 切换颜色指示器")
        print("3. 修改更新间隔")
        print("4. 修改显示模式")
        print("0. 返回主菜单")
        
        while True:
            choice = input("\n请选择 (0-4): ").strip()
            
            if choice == "0":
                self.quick_setup()
                return
            elif choice == "1":
                self.modify_stocks()
            elif choice == "2":
                self.toggle_colors()
            elif choice == "3":
                self.modify_interval()
            elif choice == "4":
                self.modify_display_mode()
            else:
                print("❌ 请输入 0-4 之间的数字")
                continue
            
            self.save_config()
            self.show_current_config()
    
    def modify_stocks(self):
        """修改监控股票"""
        stocks = self.get_multiple_stocks()
        if stocks:
            self.config["stock_info"]["symbols"] = stocks
            self.config["stock_info"]["primary_symbol"] = stocks[0]
    
    def toggle_colors(self):
        """切换颜色指示器"""
        current = self.config.get("stock_info", {}).get("use_color_indicators", True)
        new_value = self.get_yes_no("启用颜色指示器？", not current)
        
        self.config["stock_info"]["use_color_indicators"] = new_value
        
        if new_value:
            self.config["display_format"] = "{colored_display}"
        else:
            self.config["display_format"] = "{stock_name} {stock_price} ({stock_change})"
    
    def modify_interval(self):
        """修改更新间隔"""
        current = self.config.get("update_interval", 5)
        new_interval = self.get_number_input(f"更新间隔(秒，当前{current})", current, 1, 300)
        self.config["update_interval"] = new_interval
    
    def modify_display_mode(self):
        """修改显示模式"""
        print("\n显示模式:")
        print("1. 只显示一只")
        print("2. 轮换显示")
        print("3. 同时显示多只")
        
        while True:
            choice = input("请选择 (1-3): ").strip()
            
            if choice == "1":
                self.config["stock_info"]["show_multiple"] = False
                self.config["stock_info"]["rotate_stocks"] = False
                break
            elif choice == "2":
                self.config["stock_info"]["show_multiple"] = False
                self.config["stock_info"]["rotate_stocks"] = True
                interval = self.get_number_input("轮换间隔(次更新)", 10, 1, 100)
                self.config["stock_info"]["rotate_interval"] = interval
                break
            elif choice == "3":
                self.config["stock_info"]["show_multiple"] = True
                self.config["stock_info"]["rotate_stocks"] = False
                break
            else:
                print("❌ 请输入 1-3 之间的数字")
    
    def get_stock_input(self, prompt: str) -> str:
        """获取股票代码输入"""
        popular_stocks = {
            "1": ("600519", "贵州茅台"),
            "2": ("000001", "平安银行"),
            "3": ("600036", "招商银行"),
            "4": ("000858", "五粮液"),
            "5": ("002415", "海康威视"),
            "6": ("002594", "比亚迪")
        }
        
        print(f"\n{prompt}:")
        print("常用股票 (输入序号):")
        for key, (code, name) in popular_stocks.items():
            print(f"  {key}. {code} - {name}")
        print("  或直接输入6位股票代码")
        
        while True:
            user_input = input("请输入: ").strip()
            
            if user_input in popular_stocks:
                code, name = popular_stocks[user_input]
                print(f"✅ 选择了 {code} - {name}")
                return code
            elif len(user_input) == 6 and user_input.isdigit():
                print(f"✅ 添加股票 {user_input}")
                return user_input
            elif user_input == "":
                print("❌ 取消操作")
                return ""
            else:
                print("❌ 请输入正确的选项或6位股票代码")
    
    def get_multiple_stocks(self) -> list:
        """获取多只股票"""
        stocks = []
        
        print("\n添加股票 (输入空行结束):")
        while True:
            if len(stocks) == 0:
                stock = self.get_stock_input("第一只股票")
            else:
                stock = self.get_stock_input(f"第{len(stocks)+1}只股票 (可选)")
            
            if not stock:
                break
            
            if stock not in stocks:
                stocks.append(stock)
            else:
                print("⚠️ 股票已存在，跳过")
        
        if not stocks:
            print("❌ 未添加任何股票")
            return []
        
        print(f"✅ 共添加 {len(stocks)} 只股票: {', '.join(stocks)}")
        return stocks
    
    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """获取是否选择"""
        default_text = "Y/n" if default else "y/N"
        while True:
            answer = input(f"{prompt} ({default_text}): ").strip().lower()
            
            if answer == "":
                return default
            elif answer in ["y", "yes", "是", "1"]:
                return True
            elif answer in ["n", "no", "否", "0"]:
                return False
            else:
                print("❌ 请输入 y/n")
    
    def get_number_input(self, prompt: str, default: int, min_val: int, max_val: int) -> int:
        """获取数字输入"""
        while True:
            try:
                answer = input(f"{prompt} (默认{default}): ").strip()
                
                if answer == "":
                    return default
                
                num = int(answer)
                if min_val <= num <= max_val:
                    return num
                else:
                    print(f"❌ 请输入 {min_val}-{max_val} 之间的数字")
            except ValueError:
                print("❌ 请输入有效数字")
    
    def show_preview(self):
        """显示预览"""
        print("\n🎉 配置完成！")
        self.show_current_config()
        
        print("\n💡 现在可以:")
        print("  • 运行 python3 status_bar_app.py 启动应用")
        print("  • 运行 python3 test_color_feature.py 测试颜色")
        print("  • 再次运行此工具修改配置")

def main():
    """主函数"""
    try:
        config_tool = QuickConfig()
        config_tool.quick_setup()
    except KeyboardInterrupt:
        print("\n\n👋 已取消配置")
    except Exception as e:
        print(f"❌ 配置工具出错: {e}")

if __name__ == "__main__":
    main() 