#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Type
from data_providers.base_provider import BaseDataProvider

class DataProviderFactory:
    """数据提供者工厂，用于管理和获取不同类型的数据提供者"""
    
    def __init__(self):
        """初始化数据提供者工厂"""
        self.providers = {}  # 存储注册的数据提供者
        
    def register_provider(self, provider_class: Type[BaseDataProvider]) -> None:
        """
        注册数据提供者
        
        Args:
            provider_class: 数据提供者类
        """
        provider = provider_class()
        self.providers[provider.supports()] = provider
        
    def get_provider(self, provider_type: str) -> BaseDataProvider:
        """
        获取指定类型的数据提供者
        
        Args:
            provider_type: 提供者类型
            
        Returns:
            对应类型的数据提供者实例
            
        Raises:
            ValueError: 如果请求的提供者类型未注册
        """
        if provider_type not in self.providers:
            raise ValueError(f"未注册的数据提供者类型: {provider_type}")
        
        return self.providers[provider_type]
    
    def get_all_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从所有注册的提供者获取数据
        
        Args:
            config: 配置信息
            
        Returns:
            包含所有数据的字典
        """
        result = {}
        for provider_type, provider in self.providers.items():
            try:
                provider_data = provider.get_data(config)
                result.update(provider_data)
            except Exception as e:
                print(f"获取 {provider_type} 数据时出错: {e}")
        
        return result
    
    def get_registered_providers(self) -> List[str]:
        """
        获取所有注册的提供者类型
        
        Returns:
            提供者类型列表
        """
        return list(self.providers.keys())
