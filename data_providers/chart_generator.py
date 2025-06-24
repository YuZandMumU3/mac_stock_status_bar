#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票走势图表生成器
生成高精度的股票走势图片用于状态栏显示
"""

import os
import time
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
import threading

class ChartGenerator:
    """股票走势图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "charts")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 缓存清理配置 - 调整为高质量图表
        self.max_cache_files = 30  # 减少最大缓存文件数（因为文件更大）
        self.max_cache_age_hours = 12  # 减少缓存时间（更频繁清理）
        
        # 图表配置 - 增大尺寸以提高清晰度
        self.chart_width = 32    # 稍大的正方形图标
        self.chart_height = 32   # 32x32像素，更清晰
        self.background_color = (25, 28, 35)   # 更深的背景色
        self.grid_color = (60, 65, 75)         # 更明显的网格颜色
        self.line_color = (100, 180, 255)      # 更亮的蓝色
        self.up_color = (255, 69, 58)          # 更鲜艳的上涨红色
        self.down_color = (52, 199, 89)        # 更鲜艳的下跌绿色
        self.text_color = (220, 225, 235)      # 更亮的文字颜色
        self.accent_color = (255, 193, 7)      # 强调色（金黄色）
        
        # 检查依赖
        self.pil_available = False
        self.matplotlib_available = False
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.pil_available = True
            print("✅ PIL库可用，将使用PIL生成图表")
        except ImportError:
            print("⚠️ PIL库不可用")
        
        try:
            import matplotlib
            # 设置非交互式后端，避免GUI相关问题
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from matplotlib.patches import Rectangle
            self.matplotlib_available = True
            print("✅ Matplotlib库可用，将使用Matplotlib生成图表")
        except ImportError:
            print("⚠️ Matplotlib库不可用")
            
        if not self.pil_available and not self.matplotlib_available:
            print("❌ 缺少图表生成依赖库，请安装: pip install Pillow matplotlib")
        
        # 启动时清理一次缓存
        threading.Thread(target=self.smart_cleanup_cache, daemon=True).start()
    
    def generate_chart_image(self, 
                           symbol: str,
                           prices: List[float], 
                           timestamps: Optional[List[datetime]] = None,
                           current_price: float = 0,
                           change_percent: float = 0) -> Optional[str]:
        """
        生成股票走势图片
        
        Args:
            symbol: 股票代码
            prices: 价格列表
            timestamps: 时间戳列表
            current_price: 当前价格
            change_percent: 涨跌幅
            
        Returns:
            图片文件路径，失败返回None
        """
        if not prices or len(prices) < 2:
            return None
            
        # 生成文件名
        timestamp_str = int(time.time())
        filename = f"chart_{symbol}_{timestamp_str}.png"
        filepath = os.path.join(self.cache_dir, filename)
        
        # 定期清理缓存（每10次生成清理一次）
        if timestamp_str % 10 == 0:
            threading.Thread(target=self.smart_cleanup_cache, daemon=True).start()
        
        # 优先使用matplotlib
        if self.matplotlib_available:
            success = self._generate_with_matplotlib(
                filepath, symbol, prices, timestamps, current_price, change_percent
            )
            if success:
                return filepath
        
        # 备用PIL方案
        if self.pil_available:
            success = self._generate_with_pil(
                filepath, symbol, prices, timestamps, current_price, change_percent
            )
            if success:
                return filepath
                
        return None
    
    def _generate_with_matplotlib(self, 
                                filepath: str,
                                symbol: str,
                                prices: List[float], 
                                timestamps: Optional[List[datetime]],
                                current_price: float,
                                change_percent: float) -> bool:
        """使用matplotlib生成图表"""
        try:
            import matplotlib
            # 设置非交互式后端，避免GUI相关问题
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from matplotlib.patches import Rectangle
            
            # 设置matplotlib样式
            plt.style.use('dark_background')
            
            # 创建高质量图形，透明背景，32x32像素
            fig, ax = plt.subplots(figsize=(32/160, 32/160), dpi=160)  # 32x32px正方形图标
            fig.patch.set_facecolor('none')  # 透明背景
            ax.set_facecolor('none')  # 透明背景
            
            # 生成时间轴（如果没有提供）
            if timestamps is None:
                now = datetime.now()
                timestamps = [now - timedelta(minutes=i*10) for i in range(len(prices)-1, -1, -1)]
            
            # 确保时间戳和价格数量一致
            if len(timestamps) != len(prices):
                timestamps = timestamps[:len(prices)]
            
            # 绘制价格线 - 更鲜艳的颜色
            line_color = '#FF453A' if change_percent >= 0 else '#34C759'  # 更鲜艳的上涨红色，下跌绿色
            shadow_color = '#34495e'  # 阴影色
            
            # 绘制主线 - 更细的线条
            ax.plot(timestamps, prices, color=line_color, linewidth=0.7, alpha=1.0)
            
            # 不添加数据点，保持纯线条的简洁性
            
            # 设置坐标轴
            ax.set_xlim(timestamps[0], timestamps[-1])
            ax.set_ylim(min(prices) * 0.995, max(prices) * 1.005)
            
            # 隐藏坐标轴
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            
            # 不显示价格标签，只显示趋势线
            
            # 保存高质量图片，透明背景，精确尺寸
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # 移除所有边距
            plt.savefig(filepath, 
                       facecolor='none',  # 透明背景
                       edgecolor='none',
                       bbox_inches=None,  # 不使用tight模式，保持精确尺寸
                       pad_inches=0,
                       dpi=160,  # 高DPI
                       format='png',
                       transparent=True)  # 启用透明
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"Matplotlib生成图表失败: {e}")
            return False
    
    def _generate_with_pil(self, 
                          filepath: str,
                          symbol: str,
                          prices: List[float], 
                          timestamps: Optional[List[datetime]],
                          current_price: float,
                          change_percent: float) -> bool:
        """使用PIL生成图表"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建图像，使用RGBA模式支持透明
            img = Image.new('RGBA', (self.chart_width, self.chart_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 计算价格范围
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price
            
            if price_range == 0:
                price_range = max_price * 0.01  # 避免除零
            
            # 绘制网格线 - 更细致的网格
            for i in range(1, 5):
                y = int(self.chart_height * i / 5)
                draw.line([(0, y), (self.chart_width, y)], fill=self.grid_color, width=1)
            
            # 计算价格点坐标
            points = []
            for i, price in enumerate(prices):
                x = int(i * (self.chart_width - 1) / (len(prices) - 1))
                y = int(self.chart_height - 1 - (price - min_price) / price_range * (self.chart_height - 1))
                points.append((x, y))
            
            # 绘制价格线 - 适合小正方形的线条
            line_color = self.up_color if change_percent >= 0 else self.down_color
            shadow_color = (45, 50, 60)  # 更深的阴影颜色
            
            if len(points) > 1:
                # 绘制主线 - 纯线条，32x32像素
                draw.line(points, fill=line_color, width=1)
            
            # 不添加价格标签，只显示趋势线
            
            # 保存图片
            img.save(filepath, 'PNG')
            return True
            
        except Exception as e:
            print(f"PIL生成图表失败: {e}")
            return False
    
    def cleanup_old_charts(self, max_age_hours: int = 1):
        """清理旧的图表文件（保留兼容性）"""
        self.smart_cleanup_cache(max_age_hours)
    
    def smart_cleanup_cache(self, max_age_hours: int = None):
        """智能清理缓存文件"""
        try:
            if max_age_hours is None:
                max_age_hours = self.max_cache_age_hours
            
            current_time = time.time()
            chart_files = []
            
            # 收集所有图表文件信息
            for filename in os.listdir(self.cache_dir):
                if filename.startswith('chart_') and filename.endswith('.png'):
                    filepath = os.path.join(self.cache_dir, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                        size = os.path.getsize(filepath)
                        chart_files.append({
                            'path': filepath,
                            'name': filename,
                            'mtime': mtime,
                            'age': current_time - mtime,
                            'size': size
                        })
                    except OSError:
                        # 文件可能已被删除，跳过
                        continue
            
            if not chart_files:
                return
            
            deleted_count = 0
            total_size_freed = 0
            
            # 1. 删除过期文件
            max_age_seconds = max_age_hours * 3600
            for file_info in chart_files[:]:
                if file_info['age'] > max_age_seconds:
                    try:
                        os.remove(file_info['path'])
                        chart_files.remove(file_info)
                        deleted_count += 1
                        total_size_freed += file_info['size']
                    except OSError:
                        pass
            
            # 2. 如果文件数量仍然超过限制，删除最旧的文件
            if len(chart_files) > self.max_cache_files:
                # 按修改时间排序，最旧的在前
                chart_files.sort(key=lambda x: x['mtime'])
                
                files_to_delete = len(chart_files) - self.max_cache_files
                for i in range(files_to_delete):
                    file_info = chart_files[i]
                    try:
                        os.remove(file_info['path'])
                        deleted_count += 1
                        total_size_freed += file_info['size']
                    except OSError:
                        pass
            
            # 3. 清理同一股票的重复文件（保留最新的3个）
            stock_files = {}
            for file_info in chart_files:
                # 从文件名提取股票代码
                parts = file_info['name'].split('_')
                if len(parts) >= 3:
                    stock_code = parts[1]
                    if stock_code not in stock_files:
                        stock_files[stock_code] = []
                    stock_files[stock_code].append(file_info)
            
            for stock_code, files in stock_files.items():
                if len(files) > 3:  # 每个股票最多保留3个图表文件
                    # 按时间排序，删除旧的
                    files.sort(key=lambda x: x['mtime'], reverse=True)
                    for file_info in files[3:]:  # 保留最新的3个
                        try:
                            os.remove(file_info['path'])
                            deleted_count += 1
                            total_size_freed += file_info['size']
                        except OSError:
                            pass
            
            if deleted_count > 0:
                size_mb = total_size_freed / 1024 / 1024
                print(f"🗑️  清理图表缓存: 删除 {deleted_count} 个文件，释放 {size_mb:.2f}MB 空间")
                
        except Exception as e:
            print(f"智能清理缓存失败: {e}")
    
    def get_chart_path(self, symbol: str) -> Optional[str]:
        """获取最新的图表文件路径"""
        try:
            chart_files = []
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(f'chart_{symbol}_') and filename.endswith('.png'):
                    filepath = os.path.join(self.cache_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    chart_files.append((mtime, filepath))
            
            if chart_files:
                # 返回最新的文件
                chart_files.sort(reverse=True)
                return chart_files[0][1]
                
        except Exception as e:
            print(f"获取图表路径失败: {e}")
            
        return None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            chart_files = []
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.startswith('chart_') and filename.endswith('.png'):
                    filepath = os.path.join(self.cache_dir, filename)
                    try:
                        size = os.path.getsize(filepath)
                        mtime = os.path.getmtime(filepath)
                        chart_files.append({
                            'name': filename,
                            'size': size,
                            'mtime': mtime,
                            'age_hours': (time.time() - mtime) / 3600
                        })
                        total_size += size
                    except OSError:
                        continue
            
            # 按股票分组统计
            stock_stats = {}
            for file_info in chart_files:
                parts = file_info['name'].split('_')
                if len(parts) >= 3:
                    stock_code = parts[1]
                    if stock_code not in stock_stats:
                        stock_stats[stock_code] = {'count': 0, 'size': 0}
                    stock_stats[stock_code]['count'] += 1
                    stock_stats[stock_code]['size'] += file_info['size']
            
            return {
                'total_files': len(chart_files),
                'total_size_mb': total_size / 1024 / 1024,
                'cache_dir': self.cache_dir,
                'max_files': self.max_cache_files,
                'max_age_hours': self.max_cache_age_hours,
                'stock_stats': stock_stats,
                'oldest_file_age_hours': max([f['age_hours'] for f in chart_files], default=0)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def clear_all_cache(self) -> bool:
        """清空所有缓存文件"""
        try:
            deleted_count = 0
            total_size_freed = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.startswith('chart_') and filename.endswith('.png'):
                    filepath = os.path.join(self.cache_dir, filename)
                    try:
                        size = os.path.getsize(filepath)
                        os.remove(filepath)
                        deleted_count += 1
                        total_size_freed += size
                    except OSError:
                        continue
            
            if deleted_count > 0:
                size_mb = total_size_freed / 1024 / 1024
                print(f"🗑️  清空图表缓存: 删除 {deleted_count} 个文件，释放 {size_mb:.2f}MB 空间")
            
            return True
            
        except Exception as e:
            print(f"清空缓存失败: {e}")
            return False