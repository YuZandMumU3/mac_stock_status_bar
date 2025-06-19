#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据提供者包
包含各种数据提供者模块，用于获取不同类型的数据
"""

from data_providers.base_provider import BaseDataProvider
from data_providers.provider_factory import DataProviderFactory
from data_providers.system_provider import SystemDataProvider
from data_providers.stock_provider import StockDataProvider
from data_providers.network_provider import NetworkDataProvider
from data_providers.weather_provider import WeatherDataProvider

# 创建并配置默认的数据提供者工厂
def create_provider_factory():
    """创建并注册所有数据提供者"""
    factory = DataProviderFactory()
    factory.register_provider(SystemDataProvider)
    factory.register_provider(StockDataProvider)
    factory.register_provider(NetworkDataProvider)
    factory.register_provider(WeatherDataProvider)
    return factory

__all__ = [
    'BaseDataProvider',
    'DataProviderFactory',
    'SystemDataProvider',
    'StockDataProvider',
    'NetworkDataProvider',
    'WeatherDataProvider',
    'create_provider_factory'
]
