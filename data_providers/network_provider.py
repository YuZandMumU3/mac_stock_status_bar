#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import subprocess
import re
import requests
import psutil
from typing import Dict, Any, Optional

from data_providers.base_provider import BaseDataProvider

class NetworkDataProvider(BaseDataProvider):
    """网络信息提供者，用于获取网络相关数据"""
    
    def __init__(self):
        """初始化网络数据提供者"""
        # 缓存机制，避免频繁请求外部API
        self.ip_cache = None
        self.ip_cache_time = 0
        self.ip_cache_duration = 300  # IP缓存有效期（秒）
    
    def supports(self) -> str:
        return "network"
        
    def get_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取网络信息数据
        
        Args:
            config: 配置信息
            
        Returns:
            包含网络信息的字典
        """
        result = {}
        network_info = config.get("network_info", {})
        
        if network_info.get("show_local_ip", False):
            local_ip = self.get_local_ip()
            if local_ip:
                result["local_ip"] = local_ip
        
        if network_info.get("show_public_ip", False):
            public_ip = self.get_public_ip()
            if public_ip:
                result["public_ip"] = public_ip
        
        if network_info.get("show_network_usage", False):
            net = self.get_network_info()
            result["net_sent"] = f"{net['mb_sent']} MB"
            result["net_recv"] = f"{net['mb_recv']} MB"
        
        return result
    
    def get_local_ip(self) -> Optional[str]:
        """获取本地IP地址"""
        try:
            # 对于macOS系统，使用特定的命令获取IP地址
            if platform.system() == 'Darwin':
                cmd = "ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}'"
                result = subprocess.check_output(cmd, shell=True, text=True)
                matches = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
                if matches:
                    return matches[0]
            elif platform.system() == 'Windows':
                # Windows系统
                import socket
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            else:
                # Linux系统
                cmd = "hostname -I | awk '{print $1}'"
                return subprocess.check_output(cmd, shell=True, text=True).strip()
        except Exception as e:
            print(f"获取本地IP出错: {e}")
        
        return None
    
    def get_public_ip(self) -> Optional[str]:
        """获取公网IP地址"""
        import time
        current_time = time.time()
        
        # 如果缓存有效，直接返回缓存的IP
        if self.ip_cache and (current_time - self.ip_cache_time) < self.ip_cache_duration:
            return self.ip_cache
        
        try:
            response = requests.get("https://api.ipify.org", timeout=2)
            if response.status_code == 200:
                self.ip_cache = response.text.strip()
                self.ip_cache_time = current_time
                return self.ip_cache
        except Exception as e:
            print(f"获取公网IP出错: {e}")
            
            # 尝试备用API
            try:
                response = requests.get("https://ifconfig.me/ip", timeout=2)
                if response.status_code == 200:
                    self.ip_cache = response.text.strip()
                    self.ip_cache_time = current_time
                    return self.ip_cache
            except Exception:
                pass
        
        return None
    
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络使用情况"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "mb_sent": round(net_io.bytes_sent / (1024**2), 2),
            "mb_recv": round(net_io.bytes_recv / (1024**2), 2)
        }
