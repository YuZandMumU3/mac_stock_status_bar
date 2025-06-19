#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态栏应用控制器
负责协调各个模块的工作，是应用程序的核心
"""

import threading
import time
from typing import Dict, Any

from config_manager import ConfigManager
from data_providers import create_provider_factory, StockDataProvider
from ui.status_bar_ui import StatusBarUI
from utils.thread_manager import ThreadManager

class StatusBarController:
    """状态栏应用控制器，协调各模块工作"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化控制器
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化线程管理器
        self.thread_manager = ThreadManager()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(config_path)
        
        # 注册配置变更回调
        self.config_manager.add_change_callback(self._on_config_changed)
        
        # 初始化数据提供者工厂
        self.provider_factory = create_provider_factory()
        
        # 直接获取股票提供者以便访问其特定方法
        self.stock_provider = self.provider_factory.get_provider("stock")
        
        # 初始化UI
        self.ui = StatusBarUI(
            config_manager=self.config_manager,
            data_callback=self.get_all_data,
            stock_switcher=self.switch_stock
        )
        
        # 定时器
        self._timer = None
        self.update_interval = self.config_manager.get_value("update_interval", 5)
        
        # 数据更新锁，防止重叠更新
        self._update_lock = threading.Lock()
        
        # 上次更新时间
        self._last_update = 0
        
        # 是否有更新操作正在进行
        self._update_in_progress = False
    
    def start(self) -> None:
        """启动应用程序"""
        # 初始更新一次
        self.update_status()
        
        # 启动定时器
        self.start_timer()
        
        # 启动UI
        self.ui.run()
    
    def start_timer(self) -> None:
        """启动定时器，每隔指定时间更新一次状态栏"""
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.update_interval, self.timer_callback)
        self._timer.daemon = True
        self._timer.start()
    
    def timer_callback(self) -> None:
        """定时器回调函数，更新状态并重新启动定时器"""
        # 在后台线程更新状态
        self.thread_manager.submit_task(
            self._async_update_status,
            task_id="status_update",
            callback=lambda _: None  # 无需回调
        )
        
        # 重新启动定时器
        self.start_timer()
    
    def _async_update_status(self):
        """在后台线程中异步更新状态"""
        # 使用锁防止重叠更新
        if not self._update_lock.acquire(blocking=False):
            return  # 已有更新在进行中，跳过本次更新
        
        try:
            # 记录正在更新
            self._update_in_progress = True
            
            # 记录更新时间
            self._last_update = time.time()
            # 获取所有数据
            data = self.provider_factory.get_all_data(self.config_manager.get_config())
            
            # 更新UI（在主线程中）
            self.ui.update_status()
            
        finally:
            # 更新完成
            self._update_in_progress = False
            self._update_lock.release()
    
    def update_status(self) -> None:
        """更新状态栏显示（主线程调用）"""
        # 检查上次更新时间，避免频繁更新
        current_time = time.time()
        if current_time - self._last_update < 0.5 and self._update_in_progress:
            return  # 跳过本次更新
            
        # 立即更新UI，实际数据获取将在后台进行
        self.ui.update_status()
        
        # 如果没有更新操作正在进行，启动一个
        if not self._update_in_progress:
            self.thread_manager.submit_task(
                self._async_update_status,
                task_id="manual_update",
                callback=lambda _: None
            )
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        获取所有数据 (UI调用)
        
        Returns:
            包含所有数据的字典
        """
        return self.provider_factory.get_all_data(self.config_manager.get_config())
    
    def switch_stock(self) -> None:
        """切换显示的股票"""
        if isinstance(self.stock_provider, StockDataProvider):
            self.stock_provider.switch_stock()
            # 手动触发一次更新
            self.update_status()
    
    def stop(self) -> None:
        """停止应用程序"""
        print("🛑 正在停止应用程序...")
        
        # 停止定时器
        if self._timer:
            self._timer.cancel()
        
        # 停止配置文件监听
        self.config_manager.stop_config_monitor()
        
        # 关闭线程管理器
        if hasattr(self, 'thread_manager'):
            self.thread_manager.shutdown()
            
        print("✅ 应用程序已停止")
    
    def _on_config_changed(self, new_config: Dict[str, Any]) -> None:
        """
        配置文件变更回调函数
        
        Args:
            new_config: 新的配置字典
        """
        print("📋 应用新配置...")
        
        # 更新更新间隔
        old_interval = self.update_interval
        new_interval = new_config.get("update_interval", 5)
        
        if old_interval != new_interval:
            print(f"⏱️  更新间隔从 {old_interval}秒 变更为 {new_interval}秒")
            self.update_interval = new_interval
            
            # 重新启动定时器以应用新的间隔
            self.start_timer()
        
        # 清空股票提供者的缓存，强制重新获取数据
        if hasattr(self.stock_provider, 'cache'):
            old_cache_size = len(self.stock_provider.cache)
            self.stock_provider.cache.clear()
            self.stock_provider.cache_time.clear()
            if old_cache_size > 0:
                print(f"🗑️  清空股票缓存（{old_cache_size}个条目）")
        
        # 立即更新显示
        print("🔄 立即更新显示...")
        self.update_status()
        
        print("✅ 新配置已生效！")

def main():
    """应用程序入口点"""
    controller = StatusBarController()
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
        print("应用程序已停止")
if __name__ == "__main__":
    main()

