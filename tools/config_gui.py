#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图形化配置工具
提供简单直观的配置界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from typing import Dict, Any, List

class ConfigGUI:
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("股票监控配置")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('default')
        
        self.create_widgets()
        
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
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{e}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 标题
        title_label = ttk.Label(main_frame, text="股票监控配置", font=('Arial', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1
        
        # 基本设置
        basic_frame = ttk.LabelFrame(main_frame, text="基本设置", padding="10")
        basic_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        basic_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 更新间隔
        ttk.Label(basic_frame, text="更新间隔 (秒):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.update_interval_var = tk.StringVar(value=str(self.config.get("update_interval", 5)))
        update_interval_spinbox = ttk.Spinbox(basic_frame, from_=1, to=300, textvariable=self.update_interval_var, width=10)
        update_interval_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # 颜色指示器
        self.color_var = tk.BooleanVar(value=self.config.get("stock_info", {}).get("use_color_indicators", True))
        color_check = ttk.Checkbutton(basic_frame, text="启用颜色指示器 🔴📈🟢📉", variable=self.color_var)
        color_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 股票设置
        stock_frame = ttk.LabelFrame(main_frame, text="股票设置", padding="10")
        stock_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        stock_frame.columnconfigure(0, weight=1)
        stock_frame.rowconfigure(1, weight=1)
        row += 1
        
        # 股票列表
        list_frame = ttk.Frame(stock_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        
        ttk.Label(list_frame, text="监控的股票:").grid(row=0, column=0, sticky=tk.W)
        
        # 股票列表框架
        listbox_frame = ttk.Frame(stock_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        # 股票列表
        self.stock_listbox = tk.Listbox(listbox_frame, height=6)
        self.stock_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.stock_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stock_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 股票操作按钮
        button_frame = ttk.Frame(stock_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Button(button_frame, text="添加股票", command=self.add_stock).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除选中", command=self.remove_stock).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="快速添加", command=self.quick_add_stocks).pack(side=tk.LEFT)
        
        # 显示模式
        mode_frame = ttk.LabelFrame(stock_frame, text="显示模式", padding="5")
        mode_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.display_mode_var = tk.StringVar()
        current_config = self.config.get("stock_info", {})
        if current_config.get("show_multiple", False):
            self.display_mode_var.set("multiple")
        elif current_config.get("rotate_stocks", False):
            self.display_mode_var.set("rotate")
        else:
            self.display_mode_var.set("single")
        
        ttk.Radiobutton(mode_frame, text="只显示一只", variable=self.display_mode_var, value="single").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="轮换显示", variable=self.display_mode_var, value="rotate").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="同时显示多只", variable=self.display_mode_var, value="multiple").pack(anchor=tk.W)
        
        # 轮换间隔
        rotate_frame = ttk.Frame(mode_frame)
        rotate_frame.pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(rotate_frame, text="轮换间隔:").pack(side=tk.LEFT)
        self.rotate_interval_var = tk.StringVar(value=str(current_config.get("rotate_interval", 10)))
        ttk.Spinbox(rotate_frame, from_=1, to=100, textvariable=self.rotate_interval_var, width=5).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(rotate_frame, text="次更新").pack(side=tk.LEFT, padx=(5, 0))
        
        # 操作按钮
        button_main_frame = ttk.Frame(main_frame)
        button_main_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_main_frame, text="保存配置", command=self.save_settings, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_main_frame, text="重置为默认", command=self.reset_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_main_frame, text="测试颜色", command=self.test_colors).pack(side=tk.LEFT)
        
        # 加载股票列表
        self.load_stock_list()
    
    def load_stock_list(self):
        """加载股票列表到界面"""
        self.stock_listbox.delete(0, tk.END)
        symbols = self.config.get("stock_info", {}).get("symbols", [])
        for symbol in symbols:
            self.stock_listbox.insert(tk.END, symbol)
    
    def add_stock(self):
        """添加股票"""
        stock_code = simpledialog.askstring("添加股票", "请输入6位股票代码:")
        if stock_code:
            stock_code = stock_code.strip()
            if len(stock_code) == 6 and stock_code.isdigit():
                if stock_code not in self.get_current_symbols():
                    self.stock_listbox.insert(tk.END, stock_code)
                else:
                    messagebox.showwarning("警告", "股票代码已存在！")
            else:
                messagebox.showerror("错误", "请输入6位数字的股票代码！")
    
    def remove_stock(self):
        """删除选中的股票"""
        selection = self.stock_listbox.curselection()
        if selection:
            self.stock_listbox.delete(selection[0])
        else:
            messagebox.showwarning("警告", "请先选择要删除的股票！")
    
    def quick_add_stocks(self):
        """快速添加常用股票"""
        popular_stocks = {
            "600519": "贵州茅台",
            "000001": "平安银行", 
            "600036": "招商银行",
            "000858": "五粮液",
            "002415": "海康威视",
            "600276": "恒瑞医药",
            "002594": "比亚迪",
            "300015": "爱尔眼科"
        }
        
        # 创建选择窗口
        select_window = tk.Toplevel(self.root)
        select_window.title("选择股票")
        select_window.geometry("300x400")
        select_window.resizable(False, False)
        
        # 使窗口居中
        select_window.transient(self.root)
        select_window.grab_set()
        
        ttk.Label(select_window, text="选择要添加的股票:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 创建复选框
        vars_dict = {}
        for code, name in popular_stocks.items():
            if code not in self.get_current_symbols():
                var = tk.BooleanVar()
                vars_dict[code] = var
                ttk.Checkbutton(select_window, text=f"{code} - {name}", variable=var).pack(anchor=tk.W, padx=20, pady=2)
        
        def add_selected():
            selected = [code for code, var in vars_dict.items() if var.get()]
            for code in selected:
                self.stock_listbox.insert(tk.END, code)
            select_window.destroy()
        
        button_frame = ttk.Frame(select_window)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="添加选中", command=add_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=select_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def get_current_symbols(self) -> List[str]:
        """获取当前股票列表"""
        return [self.stock_listbox.get(i) for i in range(self.stock_listbox.size())]
    
    def save_settings(self):
        """保存设置"""
        try:
            # 更新配置
            self.config["update_interval"] = int(self.update_interval_var.get())
            
            stock_info = self.config.setdefault("stock_info", {})
            stock_info["enabled"] = True
            stock_info["symbols"] = self.get_current_symbols()
            stock_info["use_color_indicators"] = self.color_var.get()
            
            if stock_info["symbols"]:
                stock_info["primary_symbol"] = stock_info["symbols"][0]
            
            # 设置显示模式
            mode = self.display_mode_var.get()
            if mode == "multiple":
                stock_info["show_multiple"] = True
                stock_info["rotate_stocks"] = False
            elif mode == "rotate":
                stock_info["show_multiple"] = False
                stock_info["rotate_stocks"] = True
                stock_info["rotate_interval"] = int(self.rotate_interval_var.get())
            else:  # single
                stock_info["show_multiple"] = False
                stock_info["rotate_stocks"] = False
            
            # 设置显示格式
            if self.color_var.get():
                self.config["display_format"] = "{colored_display}"
            else:
                self.config["display_format"] = "{stock_name} {stock_price} ({stock_change})"
            
            # 保存配置
            self.save_config()
            
        except ValueError as e:
            messagebox.showerror("错误", "请检查数值输入是否正确！")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")
    
    def reset_config(self):
        """重置为默认配置"""
        if messagebox.askyesno("确认", "确定要重置为默认配置吗？"):
            self.config = self.get_default_config()
            self.refresh_ui()
    
    def refresh_ui(self):
        """刷新界面"""
        # 更新基本设置
        self.update_interval_var.set(str(self.config.get("update_interval", 5)))
        self.color_var.set(self.config.get("stock_info", {}).get("use_color_indicators", True))
        
        # 更新股票列表
        self.load_stock_list()
        
        # 更新显示模式
        current_config = self.config.get("stock_info", {})
        if current_config.get("show_multiple", False):
            self.display_mode_var.set("multiple")
        elif current_config.get("rotate_stocks", False):
            self.display_mode_var.set("rotate")
        else:
            self.display_mode_var.set("single")
        
        self.rotate_interval_var.set(str(current_config.get("rotate_interval", 10)))
    
    def test_colors(self):
        """测试颜色功能"""
        test_window = tk.Toplevel(self.root)
        test_window.title("颜色指示器预览")
        test_window.geometry("400x300")
        test_window.resizable(False, False)
        
        test_window.transient(self.root)
        test_window.grab_set()
        
        ttk.Label(test_window, text="颜色指示器预览", font=('Arial', 14, 'bold')).pack(pady=20)
        
        # 预览框架
        preview_frame = ttk.Frame(test_window)
        preview_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        examples = [
            ("上涨示例", "🔴📈 贵州茅台 1426.0 (+2.15%)"),
            ("下跌示例", "🟢📉 平安银行 12.85 (-1.23%)"),
            ("平盘示例", "⚪️➡️ 招商银行 45.67 (0.00%)")
        ]
        
        for title, example in examples:
            frame = ttk.Frame(preview_frame)
            frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(frame, text=f"{title}:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(frame, text=example, font=('Arial', 12), foreground='blue').pack(anchor=tk.W, padx=20)
        
        ttk.Button(test_window, text="关闭", command=test_window.destroy).pack(pady=20)
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = ConfigGUI()
        app.run()
    except Exception as e:
        print(f"启动配置工具失败: {e}")
        print("请确保已安装tkinter: pip install tk")

if __name__ == "__main__":
    main() 