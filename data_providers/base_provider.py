#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseDataProvider(ABC):
    """数据提供者基类"""
    
    @abstractmethod
    def get_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取数据
        
        Args:
            config: 配置信息
            
        Returns:
            包含数据的字典
        """
        pass
        
    @abstractmethod
    def supports(self) -> str:
        """
        返回此提供者支持的数据类型名称
        
        Returns:
            数据类型名称
        """
        pass
