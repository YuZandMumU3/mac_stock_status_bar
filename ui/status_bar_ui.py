#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import rumps
import threading
from typing import Dict, Any, Callable, Optional

from utils.thread_manager import ThreadManager

class StatusBarUI:
    """状态栏UI管理类，负责处理用户界面元素和交互"""
    
    def __init__(self, 
                 config_manager,
                 data_callback: Callable[[], Dict[str, Any]],
                 stock_switcher: Optional[Callable[[], None]] = None):
        """
        初始化状态栏UI
        
        Args:
            config_manager: 配置管理器实例
            data_callback: 获取数据的回调函数
            stock_switcher: 切换股票的回调函数（可选）
        """
        self.config_manager = config_manager
        self.data_callback = data_callback
        self.stock_switcher = stock_switcher
        self.thread_manager = ThreadManager()
        
        # UI刷新锁，防止多线程更新冲突
        self._ui_lock = threading.RLock()
        
        # 上次更新UI的时间
        self._last_ui_update = 0
        
        # 初始化图标
        from utils.icon_manager import IconManager
        icon_path = IconManager.get_app_icon()
        
        # 创建状态栏应用
        self.app = rumps.App("StatusBar", icon=icon_path)
        
        # 设置菜单
        self._setup_menu()
        
        # 初始显示信息
        self.app.title = "正在加载..."
    
    def _setup_menu(self) -> None:
        """设置菜单项"""
        # 创建菜单项列表
        menu_items = [
            ("更新信息", self.update_info),
            ("重新加载配置", self.reload_config),
            None,  # 分隔符
            ("编辑显示格式", self.edit_format),
        ]
        
        # 如果有股票切换功能，添加菜单项
        if self.stock_switcher:
            menu_items.append(("切换股票", self.switch_stock))
        
        menu_items.extend([
            ("编辑配置文件", self.edit_config_file),
            None,  # 分隔符
            ("退出 (⌘Q)", self.quit)
        ])
        
        # 创建菜单
        self.app.menu = []
        for item in menu_items:
            if item is None:
                self.app.menu.add(rumps.separator)
            else:
                name, callback = item
                self.app.menu.add(rumps.MenuItem(name, callback=callback))
    
    def update_status(self) -> None:
        """更新状态栏显示的信息（可从任何线程调用）"""
        # 使用线程管理器在后台线程获取数据
        self.thread_manager.submit_task(
            self._async_get_data,
            task_id="ui_data_fetch",
            callback=self._update_ui_with_data
        )
    
    def _async_get_data(self) -> Dict[str, Any]:
        """异步获取数据"""
        try:
            return self.data_callback()
        except Exception as e:
            print(f"获取数据出错: {e}")
            return {}
    
    def _update_ui_with_data(self, info: Dict[str, Any]) -> None:
        """
        使用获取的数据更新UI
        
        Args:
            info: 数据字典
        """
        # 使用锁保护UI更新
        with self._ui_lock:
            # 检查是否启用了自定义信息
            if self.config_manager.get_value("custom_info.enabled", False):
                custom_text = self.config_manager.get_value("custom_info.text", "")
                if custom_text:
                    self.app.title = custom_text
                    return
            
            # 检查是否有图片走势图
            if info.get("has_chart_image", False) and info.get("chart_image_path"):
                chart_path = info.get("chart_image_path")
                if os.path.exists(chart_path):
                    try:
                        # 直接使用图片路径作为状态栏图标
                        self.app.icon = chart_path
                        
                        # 设置简化的文字显示
                        stock_name = info.get("stock_name", "")
                        stock_price = info.get("stock_price", "")
                        change_percent = info.get("colored_change_percent", "")
                        
                        if stock_name and stock_price:
                            self.app.title = f"{stock_name} {stock_price} {change_percent}"
                        else:
                            # 格式化显示内容
                            display_format = self.config_manager.get_value("display_format", "")
                            display_text = display_format.format(**info)
                            self.app.title = display_text
                        return
                    except Exception as e:
                        print(f"设置图片图标失败: {e}")
            
            # 恢复默认图标
            from utils.icon_manager import IconManager
            default_icon = IconManager.get_app_icon()
            if self.app.icon != default_icon:
                self.app.icon = default_icon
            
            # 格式化显示内容
            display_format = self.config_manager.get_value("display_format", "")
            try:
                display_text = display_format.format(**info)
                self.app.title = display_text
            except KeyError as e:
                # 如果格式化失败（可能是配置中引用了未获取的信息），显示错误
                self.app.title = f"格式错误: {e}"
    
    def update_info(self, _) -> None:
        """更新信息菜单回调"""
        self.app.title = "正在刷新..."
        self.update_status()
    
    def reload_config(self, _) -> None:
        """重新加载配置菜单回调"""
        self.app.title = "正在重新加载配置..."
        
        # 在后台线程重新加载配置
        def reload_and_update():
            success = self.config_manager.reload_config()
            if success:
                # 配置重新加载成功，更新显示
                self.update_status()
            else:
                # 配置重新加载失败，显示错误
                self.app.title = "配置重新加载失败"
                
        self.thread_manager.submit_task(
            reload_and_update,
            task_id="reload_config"
        )
    
    def switch_stock(self, _) -> None:
        """切换股票菜单回调"""
        if self.stock_switcher:
            # 显示正在切换的提示
            self.app.title = "正在切换..."
            
            # 在后台线程执行切换操作
            def switch_and_update():
                self.stock_switcher()
                self.update_status()
                
            self.thread_manager.submit_task(
                switch_and_update,
                task_id="switch_stock"
            )
        else:
            rumps.alert("错误", "股票切换功能未启用")
    
    def edit_format(self, _) -> None:
        """编辑显示格式菜单回调"""
        current_format = self.config_manager.get_value("display_format", "")
        response = rumps.Window(
            message="请输入显示格式（使用{变量名}引用信息）",
            default_text=current_format,
            dimensions=(400, 100)
        ).run()
        
        if response.clicked:
            # 在后台线程更新配置
            def update_format():
                self.config_manager.set_value("display_format", response.text)
                self.update_status()
                
            self.thread_manager.submit_task(
                update_format,
                task_id="update_format"
            )
    
    def edit_config_file(self, _) -> None:
        """编辑配置文件菜单回调"""
        try:
            config_path = os.path.abspath(self.config_manager.config_path)
            # 尝试用默认应用程序打开文件
            if platform.system() == 'Darwin':  # macOS
                os.system(f"open '{config_path}'")
            elif platform.system() == 'Windows':  # Windows
                os.system(f'start "" "{config_path}"')
            else:  # Linux
                os.system(f"xdg-open '{config_path}'")
        except Exception as e:
            rumps.alert("错误", f"无法打开配置文件: {e}")
    
    def quit(self, _) -> None:
        """退出应用程序菜单回调"""
        # 显示确认对话框
        if rumps.alert("确认", "确定要退出应用吗？", ok="退出", cancel="取消"):
            # 用户点击了"退出"按钮
            rumps.quit_application()
    
    def run(self) -> None:
        """运行状态栏应用程序"""
        # 在启动前执行一次数据更新
        self.update_status()
        self.app.run()
