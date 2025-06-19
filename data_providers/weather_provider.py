#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from typing import Dict, Any, Optional

from data_providers.base_provider import BaseDataProvider

class WeatherDataProvider(BaseDataProvider):
    """天气信息提供者，用于获取天气相关数据"""
    
    def __init__(self):
        """初始化天气数据提供者"""
        # 缓存机制，避免频繁请求API
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 1800  # 缓存有效期（秒，默认30分钟）
    
    def supports(self) -> str:
        return "weather"
        
    def get_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取天气信息数据
        
        Args:
            config: 配置信息
            
        Returns:
            包含天气信息的字典
        """
        result = {}
        weather_info = config.get("weather_info", {})
        
        if not weather_info.get("enabled", False):
            return result
        
        city = weather_info.get("city", "beijing")
        api_key = weather_info.get("api_key", "")
        
        if api_key:
            weather_data = self.get_weather(city, api_key)
            if weather_data:
                result.update({
                    "weather_temp": f"{weather_data['temp']}°C",
                    "weather_desc": weather_data["description"],
                    "weather_city": weather_data["city"]
                })
        
        return result
    
    def get_weather(self, city: str = "beijing", api_key: str = "") -> Optional[Dict[str, Any]]:
        """
        获取天气信息
        
        Args:
            city: 城市名称
            api_key: OpenWeatherMap API密钥
            
        Returns:
            包含天气信息的字典，如果获取失败则返回None
        """
        # 缓存键
        cache_key = f"{city}_{api_key}"
        
        # 检查缓存
        now = time.time()
        if cache_key in self.cache and now - self.cache_time.get(cache_key, 0) < self.cache_duration:
            return self.cache[cache_key]
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "city": data["name"]
                }
                
                # 更新缓存
                self.cache[cache_key] = result
                self.cache_time[cache_key] = now
                
                return result
        except Exception as e:
            print(f"获取天气信息出错: {e}")
            
            # 尝试备用方法
            try:
                result = self._get_weather_alternative(city)
                if result:
                    self.cache[cache_key] = result
                    self.cache_time[cache_key] = now
                    return result
            except Exception:
                pass
        
        return None
    
    def _get_weather_alternative(self, city: str) -> Optional[Dict[str, Any]]:
        """尝试使用备用方法获取天气信息"""
        # 这里可以实现备用的天气获取方法
        # 例如使用其他API或爬虫等
        # 目前返回None表示未实现
        return None
