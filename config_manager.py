#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import threading
from typing import Dict, Any, Optional, Callable

class ConfigManager:
    """配置管理类，负责配置文件的读写和默认配置管理，支持热重载"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()
        
        # 配置变更回调函数列表
        self._change_callbacks = []
        
        # 文件监听相关
        self._last_modified = 0
        self._monitor_thread = None
        self._monitor_stop_flag = threading.Event()
        
        # 启动配置文件监听
        self.start_config_monitor()
    
    def add_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        添加配置变更回调函数
        
        Args:
            callback: 当配置变更时调用的回调函数，接收新配置作为参数
        """
        self._change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        移除配置变更回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    def _notify_config_changed(self) -> None:
        """通知所有注册的回调函数配置已变更"""
        for callback in self._change_callbacks:
            try:
                callback(self.config)
            except Exception as e:
                print(f"配置变更回调函数执行失败: {e}")
    
    def start_config_monitor(self) -> None:
        """启动配置文件监听"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        
        self._monitor_stop_flag.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_config_file, daemon=True)
        self._monitor_thread.start()
        
        # 记录初始修改时间
        try:
            self._last_modified = os.path.getmtime(self.config_path)
        except OSError:
            self._last_modified = 0
    
    def stop_config_monitor(self) -> None:
        """停止配置文件监听"""
        self._monitor_stop_flag.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1)
    
    def _monitor_config_file(self) -> None:
        """监听配置文件变化的后台线程"""
        while not self._monitor_stop_flag.is_set():
            try:
                if os.path.exists(self.config_path):
                    current_modified = os.path.getmtime(self.config_path)
                    
                    # 检查文件是否被修改
                    if current_modified > self._last_modified:
                        print("🔄 检测到配置文件变更，正在重新加载...")
                        
                        # 稍微延迟一下，确保文件写入完成
                        time.sleep(0.5)
                        
                        # 重新加载配置
                        old_config = self.config.copy()
                        try:
                            self.config = self.load_config()
                            self._last_modified = current_modified
                            
                            # 检查配置是否真的发生了变化
                            if self.config != old_config:
                                print("✅ 配置已更新，正在应用新配置...")
                                self._notify_config_changed()
                            else:
                                print("📝 配置文件已重新加载，但内容未变更")
                                
                        except Exception as e:
                            print(f"❌ 配置重新加载失败: {e}")
                            # 恢复旧配置
                            self.config = old_config
                
                # 每秒检查一次
                time.sleep(1)
                
            except Exception as e:
                print(f"配置文件监听错误: {e}")
                time.sleep(5)  # 出错时等待更长时间
    
    def reload_config(self) -> bool:
        """
        手动重新加载配置
        
        Returns:
            是否成功重新加载
        """
        try:
            old_config = self.config.copy()
            self.config = self.load_config()
            
            if self.config != old_config:
                self._notify_config_changed()
                print("✅ 配置已手动重新加载")
                return True
            else:
                print("📝 配置内容未变更")
                return True
                
        except Exception as e:
            print(f"❌ 手动重新加载配置失败: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "update_interval": 5,  # 更新为5秒
            "display_format": "{display_with_trend}",
            "time_format": "%H:%M:%S",
            "date_format": "%Y-%m-%d",
            "custom_info": {
                "enabled": False,
                "text": "自定义信息"
            },
            "system_info": {
                "show_time": True,
                "show_date": False,
                "show_battery": False,
                "show_cpu": False,
                "show_memory": False,
                "show_disk": False
            },
            "network_info": {
                "show_local_ip": False,
                "show_public_ip": False,
                "show_network_usage": False
            },
            "weather_info": {
                "enabled": False,
                "city": "beijing",
                "api_key": ""
            },
            "stock_info": {
                "enabled": True,
                "symbols": ["600519", "000001", "AAPL", "hk00700"],
                "primary_symbol": "600519",
                "show_multiple": False,
                "rotate_stocks": True,
                "rotate_interval": 10,
                "show_index": True,
                "index_code": "000001",
                "use_color_indicators": True,
                "show_trend_chart": True,
                "trend_period_hours": 3,
    
                "use_image_chart": True
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件，如果不存在则创建默认配置
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果配置文件不存在或格式错误，保存并返回默认配置
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典，如果为None则保存当前配置
        """
        if config is None:
            config = self.config
            
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            配置字典
        """
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新当前配置
        
        Args:
            new_config: 新的配置字典
        """
        self.config = new_config
        self.save_config(new_config)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置项的值
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项的值
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set_value(self, key: str, value: Any) -> None:
        """
        设置配置项的值
        
        Args:
            key: 配置项键名
            value: 配置项的值
        """
        keys = key.split(".")
        target = self.config
        
        # 导航到嵌套字典的最后一级
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # 设置值
        target[keys[-1]] = value
        self.save_config()

if __name__ == "__main__":
    # 测试代码
    config_manager = ConfigManager()
    print("当前配置:", config_manager.get_config())
    print("更新间隔:", config_manager.get_value("update_interval"))
    print("股票信息启用:", config_manager.get_value("stock_info.enabled"))
