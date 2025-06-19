#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
import datetime
import platform
import os
from typing import Dict, Any, Optional

from data_providers.base_provider import BaseDataProvider

class SystemDataProvider(BaseDataProvider):
    """系统信息提供者，用于获取系统相关的数据"""
    
    def supports(self) -> str:
        return "system"
        
    def get_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取系统信息数据
        
        Args:
            config: 配置信息
            
        Returns:
            包含系统信息的字典
        """
        result = {}
        system_info = config.get("system_info", {})
        
        if system_info.get("show_time", False):
            result["time"] = self.get_time(config.get("time_format", "%H:%M:%S"))
        
        if system_info.get("show_date", False):
            result["date"] = self.get_date(config.get("date_format", "%Y-%m-%d"))
        
        if system_info.get("show_battery", False):
            battery = self.get_battery()
            if battery:
                result["battery"] = f"{battery['percent']}%"
                result["battery_charging"] = "⚡" if battery.get("charging") else ""
        
        if system_info.get("show_cpu", False):
            cpu = self.get_cpu_info()
            result["cpu"] = f"{cpu['percent']}%"
        if system_info.get("show_memory", False):
            memory = self.get_memory_info()
            result["memory"] = f"{memory['percent']}%"
            result["memory_used_gb"] = f"{memory['used_gb']} GB"
            result["memory_total_gb"] = f"{memory['total_gb']} GB"
        
        if system_info.get("show_disk", False):
            disk = self.get_disk_info()
            result["disk"] = f"{disk['percent']}%"
            result["disk_free_gb"] = f"{disk['free_gb']} GB"
            result["disk_total_gb"] = f"{disk['total_gb']} GB"
            
        return result
    
    def get_time(self, format_str: str = "%H:%M:%S") -> str:
        """获取当前时间"""
        return datetime.datetime.now().strftime(format_str)
    
    def get_date(self, format_str: str = "%Y-%m-%d") -> str:
        """获取当前日期"""
        return datetime.datetime.now().strftime(format_str)
    
    def get_battery(self) -> Optional[Dict[str, Any]]:
        """获取电池信息"""
        try:
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    return {
                        "percent": battery.percent,
                        "power_plugged": battery.power_plugged,
                        "charging": battery.power_plugged,
                        "time_left": battery.secsleft if battery.secsleft != -1 else None
                    }
        except Exception:
            pass
        return None
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
            "physical_count": psutil.cpu_count(logical=False)
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2)
        }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2)
        }
