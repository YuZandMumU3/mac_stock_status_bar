#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import pickle
from typing import Dict, Any, Optional, List
import threading
from functools import wraps

# 创建一个锁，用于保护缓存访问
cache_lock = threading.RLock()

def with_cache_lock(func):
    """装饰器，确保函数执行时持有缓存锁"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with cache_lock:
            return func(self, *args, **kwargs)
    return wrapper

class StockDataProvider:
    """A股股票数据提供者，用于获取A股股票相关数据"""
    
    def __init__(self):
        """初始化A股数据提供者"""
        # 缓存机制
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 60  # 缓存有效期60秒，减少API请求
        self.current_stock_index = 0
        self.rotate_counter = 0
        
        # 导入thread_manager
        from utils.thread_manager import ThreadManager
        self.thread_manager = ThreadManager()
        
        # 持久化缓存路径
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 尝试加载持久化缓存
        self._load_persistent_cache()
        
        # 可用的接口方法
        self.primary_method = "stock_individual_info_em"  # 主要方法：个股信息
        self.fallback_method = "stock_zh_a_hist"  # 备用方法：历史数据
        self.api_available = False
        
        # 尝试导入 akshare
        self.ak = None
        self.pd = None
        try:
            import akshare as ak
            import pandas as pd
            self.ak = ak
            self.pd = pd
            self.api_available = True
            print("✅ AKShare库加载成功，使用个股信息接口获取数据")
        except ImportError as e:
            print(f"❌ 无法导入AKShare库 - {e}")
            print("请运行: pip install akshare")
    
    def supports(self) -> str:
        return "stock"
    
    def _load_persistent_cache(self):
        """加载持久化缓存"""
        try:
            cache_file = os.path.join(self.cache_dir, "stock_cache.pkl")
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.cache = cache_data.get('cache', {})
                    self.cache_time = cache_data.get('cache_time', {})
        except Exception as e:
            print(f"加载缓存失败: {e}")
    
    @with_cache_lock
    def _save_persistent_cache(self):
        """保存持久化缓存"""
        try:
            cache_file = os.path.join(self.cache_dir, "stock_cache.pkl")
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'cache': self.cache,
                    'cache_time': self.cache_time
                }, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")
            
    @with_cache_lock
    def update_cache(self, key, value):
        """更新缓存"""
        self.cache[key] = value
        self.cache_time[key] = time.time()
        # 每5次更新保存一次持久化缓存
        if len(self.cache) % 5 == 0:
            self.thread_manager.submit_task(
                self._save_persistent_cache,
                task_id="save_cache"
            )
    
    @with_cache_lock
    def get_from_cache(self, key):
        """从缓存获取数据"""
        if key in self.cache:
            # 股票名称缓存使用更长的时间（24小时）
            if key.startswith("stock_name_"):
                cache_duration = 24 * 60 * 60  # 24小时
            else:
                cache_duration = self.cache_duration  # 默认60秒
            
            if time.time() - self.cache_time.get(key, 0) < cache_duration:
                return self.cache[key]
        return None
        
    def get_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取A股股票数据"""
        stock_info = config.get("stock_info", {})
        if not stock_info.get("enabled", False):
            return {}
        
        # 获取要显示的股票符号
        symbols = stock_info.get("symbols", [])
        if not symbols:
            return {}
            
        # 过滤只保留A股代码（6位数字）
        a_stock_symbols = [s for s in symbols if len(s) == 6 and s.isdigit()]
        if not a_stock_symbols:
            return {"error": "没有有效的A股代码"}
        
        # 处理股票轮换
        if stock_info.get("rotate_stocks", False):
            self.rotate_counter += 1
            if self.rotate_counter >= stock_info.get("rotate_interval", 10):
                self.current_stock_index = (self.current_stock_index + 1) % len(a_stock_symbols)
                self.rotate_counter = 0
        
        # 保存颜色设置以供格式化方法使用
        self.use_color_indicators = stock_info.get("use_color_indicators", True)
        
        # 显示多只股票或单只股票
        if stock_info.get("show_multiple", False):
            return self.get_multiple_stocks(a_stock_symbols)
        else:
            symbol = a_stock_symbols[self.current_stock_index % len(a_stock_symbols)]
            stock_data = self.get_stock_price(symbol)
            if stock_data:
                # 直接返回股票数据，不嵌套在stock字段下
                return stock_data
            else:
                # 返回友好的错误信息
                return self._format_stock_data_with_color({
                    "symbol": f"{symbol}",
                    "price": "获取中...",
                    "change": "0",
                    "change_percent": "0%",
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return {}
    
    def switch_stock(self) -> None:
        """手动切换股票"""
        pass
    
    def _get_color_indicator(self, change_percent_str: str) -> str:
        """
        根据涨跌幅获取颜色指示符
        
        Args:
            change_percent_str: 涨跌幅字符串，如 "2.5%" 或 "-1.8%"
            
        Returns:
            颜色指示符字符串
        """
        try:
            # 提取数值
            change_value = float(change_percent_str.replace("%", "").strip())
            
            if change_value > 0:
                # 上涨 - 红色圆圈 + 箭头
                return "🔴📈"
            elif change_value < 0:
                # 下跌 - 绿色圆圈 + 箭头
                return "🟢📉"
            else:
                # 平盘 - 灰色圆圈
                return "⚪️➡️"
        except (ValueError, TypeError):
            return "⚪️"
    
    def _format_stock_data_with_color(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        为股票数据添加颜色指示，并返回带颜色的格式化数据
        
        Args:
            stock_data: 原始股票数据
            
        Returns:
            包含颜色指示的股票数据
        """
        if not stock_data:
            return stock_data
            
        # 获取涨跌幅和颜色指示
        change_percent = stock_data.get("change_percent", "0%")
        use_color = getattr(self, 'use_color_indicators', True)
        color_indicator = self._get_color_indicator(change_percent) if use_color else ""
        
        # 创建带颜色的股票数据副本
        colored_data = stock_data.copy()
        
        # 添加颜色指示到各个字段
        colored_data["color_indicator"] = color_indicator
        colored_data["stock_symbol"] = stock_data.get("symbol", "")  # 保留原始symbol
        colored_data["stock_name"] = stock_data.get("symbol", "").split("(")[0] if "(" in stock_data.get("symbol", "") else ""
        colored_data["stock_code"] = stock_data.get("symbol", "").split("(")[1].replace(")", "") if "(" in stock_data.get("symbol", "") else ""
        colored_data["stock_price"] = stock_data.get("price", "")
        colored_data["stock_change"] = stock_data.get("change_percent", "")
        
        # 为涨跌额和涨跌幅添加格式化（不重复颜色指示器）
        try:
            change_value = float(change_percent.replace("%", "").strip())
            # 涨跌额和涨跌幅不需要重复颜色指示器，只需要正确的符号
            if change_value > 0:
                colored_data["colored_change"] = f"+{stock_data.get('change', '')}"
                colored_data["colored_change_percent"] = f"+{change_percent}"
            elif change_value < 0:
                colored_data["colored_change"] = f"{stock_data.get('change', '')}"
                colored_data["colored_change_percent"] = f"{change_percent}"
            else:
                colored_data["colored_change"] = f"{stock_data.get('change', '')}"
                colored_data["colored_change_percent"] = f"{change_percent}"
        except (ValueError, TypeError):
            colored_data["colored_change"] = f"{stock_data.get('change', '')}"
            colored_data["colored_change_percent"] = f"{change_percent}"
            
        # 创建完整的带颜色显示文本
        prefix = f"{color_indicator} " if use_color and color_indicator else ""
        colored_data["colored_display"] = f"{prefix}{colored_data.get('stock_name', '')} {colored_data.get('stock_price', '')} ({colored_data.get('colored_change_percent', '').strip()})"
        
        return colored_data

    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取A股股票价格"""
        if not symbol.isdigit() or len(symbol) != 6:
            return None
            
        # 先检查缓存
        cache_key = f"a_stock_{symbol}"
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            # 对缓存数据也应用颜色格式化
            return self._format_stock_data_with_color(cached_data)
        
        # 如果API可用，尝试获取新数据
        if self.api_available and self.ak and self.pd:
            result = self._get_a_stock_data(symbol)
            if result:
                # 缓存原始数据（不带颜色）
                self.update_cache(cache_key, result)
                # 返回带颜色的数据
                return self._format_stock_data_with_color(result)
        
        # 尝试使用旧缓存数据
        old_cache = self.cache.get(cache_key)
        if old_cache:
            result = old_cache.copy()
            result["price"] = f"{result.get('price', 'N/A')} (缓存)"
            return self._format_stock_data_with_color(result)
            
        return None
    
    def _get_a_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取A股数据，只使用历史数据接口（最稳定）"""
        # 只使用历史数据接口，避免个股信息接口的pandas错误
        try:
            result = self._get_stock_via_history(symbol)
            if result:
                return result
        except Exception as e:
            print(f"历史数据接口获取失败: {e}")
        
        # 如果历史数据接口失败，返回空（不再使用个股信息接口）
        return None
    
    def _get_stock_via_history(self, symbol: str) -> Optional[Dict[str, Any]]:
        """通过历史数据接口获取股票数据（优化版）"""
        try:
            # 获取历史数据
            hist_df = self.ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="")
            if hist_df is None or hist_df.empty:
                print(f"历史数据为空: {symbol}")
                return None
            
            # 获取最新一天的数据
            latest = hist_df.iloc[-1]
            
            # 提取数据，使用get方法避免KeyError
            price = latest.get('收盘', 0)
            change = latest.get('涨跌额', 0) 
            change_percent = latest.get('涨跌幅', 0)
            
            # 验证数据有效性
            if price == 0 or price is None:
                print(f"价格数据无效: {symbol}, price={price}")
                return None
            
            # 股票名称从代码生成
            name = self._get_stock_name(symbol)
            
            # 确保涨跌幅格式正确
            if isinstance(change_percent, (int, float)):
                change_percent_str = f"{change_percent}%"
            else:
                change_percent_str = str(change_percent)
                if not change_percent_str.endswith('%'):
                    change_percent_str += "%"
            
            return {
                "symbol": f"{name}({symbol})",
                "price": str(price),
                "change": str(change),
                "change_percent": change_percent_str,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"历史数据获取失败: {symbol} - {e}")
            return None
    
    def _get_stock_name(self, symbol: str) -> str:
        """
        纯API动态获取股票名称
        尝试多个API接口来获取股票名称，不使用本地映射
        """
        # 检查名称缓存
        name_cache_key = f"stock_name_{symbol}"
        cached_name = self.get_from_cache(name_cache_key)
        if cached_name:
            return cached_name
        
        # 如果API不可用，直接返回默认格式
        if not self.api_available or not self.ak:
            default_name = f"股票{symbol}"
            self.cache[name_cache_key] = default_name
            self.cache_time[name_cache_key] = time.time()
            return default_name
        
        # 尝试多种API方法获取股票名称
        stock_name = None
        
        # 方法1: 使用股票基本信息接口
        stock_name = self._try_get_name_via_basic_info(symbol)
        if stock_name:
            self.cache[name_cache_key] = stock_name
            self.cache_time[name_cache_key] = time.time()
            return stock_name
        
        # 方法2: 使用实时行情接口（最可靠的方法）
        stock_name = self._try_get_name_via_realtime_quote(symbol)
        if stock_name:
            self.cache[name_cache_key] = stock_name
            self.cache_time[name_cache_key] = time.time()
            return stock_name
        
        # 方法3: 使用股票列表接口
        stock_name = self._try_get_name_via_stock_list(symbol)
        if stock_name:
            self.cache[name_cache_key] = stock_name
            self.cache_time[name_cache_key] = time.time()
            return stock_name
        
        # 方法4: 使用简化的单股查询
        stock_name = self._try_get_name_simple_query(symbol)
        if stock_name:
            self.cache[name_cache_key] = stock_name
            self.cache_time[name_cache_key] = time.time()
            return stock_name
        
        # 所有方法都失败，使用默认格式并缓存（避免重复尝试）
        default_name = f"股票{symbol}"
        self.cache[name_cache_key] = default_name
        self.cache_time[name_cache_key] = time.time()
        return default_name
    
    def _try_get_name_via_basic_info(self, symbol: str) -> Optional[str]:
        """方法1: 通过股票基本信息接口获取名称"""
        try:
            stock_info = self.ak.stock_individual_info_em(symbol=symbol)
            if stock_info is not None and not stock_info.empty:
                # 查找包含股票名称的字段
                for _, row in stock_info.iterrows():
                    item = str(row.get('item', '')).strip()
                    value = str(row.get('value', '')).strip()
                    
                    # 查找包含股票名称的字段
                    if any(keyword in item for keyword in ['股票简称', '简称', '名称', '股票名称']):
                        if self._is_valid_stock_name(value):
                            return value
                
                # 如果没找到明确的名称字段，查找第一个有效的中文名称
                for _, row in stock_info.iterrows():
                    value = str(row.get('value', '')).strip()
                    if self._is_valid_stock_name(value):
                        return value
        except Exception:
            pass
        return None
    
    def _try_get_name_via_realtime_quote(self, symbol: str) -> Optional[str]:
        """方法2: 通过实时行情接口获取名称"""
        try:
            # 尝试获取沪深A股实时行情
            if hasattr(self.ak, 'stock_zh_a_spot_em'):
                spot_data = self.ak.stock_zh_a_spot_em()
                if spot_data is not None and not spot_data.empty:
                    # 查找对应的股票代码
                    if '代码' in spot_data.columns:
                        matching_stocks = spot_data[spot_data['代码'] == symbol]
                        if not matching_stocks.empty and '名称' in spot_data.columns:
                            name = str(matching_stocks.iloc[0]['名称']).strip()
                            if self._is_valid_stock_name(name):
                                return name
        except Exception:
            pass
        
        # 尝试其他实时行情接口
        try:
            if hasattr(self.ak, 'stock_zh_a_spot'):
                spot_data = self.ak.stock_zh_a_spot()
                if spot_data is not None and not spot_data.empty:
                    if 'code' in spot_data.columns:
                        matching_stocks = spot_data[spot_data['code'] == symbol]
                        if not matching_stocks.empty and 'name' in spot_data.columns:
                            name = str(matching_stocks.iloc[0]['name']).strip()
                            if self._is_valid_stock_name(name):
                                return name
        except Exception:
            pass
        
        return None
    
    def _try_get_name_via_history_data(self, symbol: str) -> Optional[str]:
        """方法3: 通过历史数据接口获取名称（改进版）"""
        # 这个方法通常不能获取股票名称，只是数据列名
        # 暂时跳过，避免获取到错误的"开盘"等列名
        return None
    
    def _try_get_name_via_stock_list(self, symbol: str) -> Optional[str]:
        """方法4: 通过股票列表接口获取名称"""
        try:
            # 尝试获取股票基本信息列表
            if hasattr(self.ak, 'stock_info_a_code_name'):
                stock_list = self.ak.stock_info_a_code_name()
                if stock_list is not None and not stock_list.empty:
                    # 查找对应的股票代码
                    if 'code' in stock_list.columns:
                        matching_stocks = stock_list[stock_list['code'] == symbol]
                        if not matching_stocks.empty and 'name' in stock_list.columns:
                            name = str(matching_stocks.iloc[0]['name']).strip()
                            if self._is_valid_stock_name(name):
                                return name
        except Exception:
            pass
        
        try:
            # 尝试获取沪深A股基本信息
            if hasattr(self.ak, 'stock_zh_a_spot_em'):
                spot_data = self.ak.stock_zh_a_spot_em()
                if spot_data is not None and not spot_data.empty:
                    if '代码' in spot_data.columns and '名称' in spot_data.columns:
                        matching_stocks = spot_data[spot_data['代码'] == symbol]
                        if not matching_stocks.empty:
                            name = str(matching_stocks.iloc[0]['名称']).strip()
                            if self._is_valid_stock_name(name):
                                return name
        except Exception:
            pass
        
        try:
            # 尝试获取股票基础信息
            if hasattr(self.ak, 'tool_trade_date_hist_sina'):
                # 使用工具类获取股票基本信息
                pass
        except Exception:
            pass
        
        return None
    
    def _try_get_name_simple_query(self, symbol: str) -> Optional[str]:
        """方法4: 使用简化的单股查询"""
        try:
            # 这个方法与方法1类似，但作为备用
            stock_info = self.ak.stock_individual_info_em(symbol=symbol)
            if stock_info is not None and not stock_info.empty:
                # 直接查找股票简称字段
                for _, row in stock_info.iterrows():
                    item = str(row.get('item', '')).strip()
                    value = str(row.get('value', '')).strip()
                    
                    if item == '股票简称' and self._is_valid_stock_name(value):
                        return value
                
                # 查找其他可能的名称字段
                for _, row in stock_info.iterrows():
                    item = str(row.get('item', '')).strip()
                    value = str(row.get('value', '')).strip()
                    
                    if any(keyword in item for keyword in ['简称', '名称']) and self._is_valid_stock_name(value):
                        return value
        except Exception:
            pass
        return None
    
    def _is_valid_stock_name(self, name: str) -> bool:
        """验证是否为有效的股票名称"""
        if not name or name == 'None' or name == 'nan':
            return False
        
        # 去除空白字符
        name = name.strip()
        if not name:
            return False
        
        # 检查长度（股票名称通常2-10个字符）
        if not (2 <= len(name) <= 10):
            return False
        
        # 检查是否包含中文字符
        if not any('\u4e00' <= char <= '\u9fff' for char in name):
            return False
        
        # 排除明显不是股票名称的内容
        invalid_patterns = [
            '股票', '代码', '价格', '涨跌', '成交', '市值', '日期', '时间',
            '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅',
            '换手率', '市盈率', '市净率', '总市值', '流通市值'
        ]
        if any(pattern in name for pattern in invalid_patterns):
            return False
        
        # 排除纯数字或日期格式
        if name.replace('.', '').replace('-', '').replace('/', '').isdigit():
            return False
        
        return True
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """获取多只A股股票数据"""
        stocks = []
        for symbol in symbols[:3]:  # 最多显示3只股票，避免界面过于拥挤
            stock_data = self.get_stock_price(symbol)
            if stock_data:
                stocks.append(stock_data)
        
        if stocks:
            return {"stocks": stocks}
        else:
            # 如果没有数据，返回友好提示
            return {
                "stocks": [self._format_stock_data_with_color({
                    "symbol": "A股数据",
                    "price": "获取中...",
                    "change": "0",
                    "change_percent": "0%",
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                })]
            }
    
    def reset_failed_methods(self):
        """重置失效的方法"""
        print("重置A股数据获取方法...")
        
        # 清空过期缓存
        current_time = time.time()
        expired_keys = []
        for key, cache_time in self.cache_time.items():
            if current_time - cache_time > self.cache_duration * 10:  # 保留更长时间的缓存
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_time:
                del self.cache_time[key]

