#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图标管理模块，用于创建和管理应用图标
"""

import os
from typing import Tuple, Optional

class IconManager:
    """图标管理类，负责创建和管理应用图标"""
    
    @staticmethod
    def create_icon(text: str, 
                   size: Tuple[int, int] = (22, 22),
                   bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
                   text_color: Tuple[int, int, int] = (0, 0, 0),
                   filename: str = "icon.png") -> str:
        """
        创建一个简单的文本图标
        
        Args:
            text: 图标文本
            size: 图标尺寸
            bg_color: 背景颜色（RGBA）
            text_color: 文本颜色（RGB）
            filename: 保存的文件名
            
        Returns:
            图标文件路径
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建透明背景图像
            image = Image.new("RGBA", size, bg_color)
            draw = ImageDraw.Draw(image)
            
            # 尝试加载字体，如果失败则使用默认字体
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("Arial", 12)
            except IOError:
                # 使用默认字体
                font = ImageFont.load_default()
            
            # 计算文本位置以居中显示 (兼容新版Pillow)
            try:
                # 新版Pillow方法
                left, top, right, bottom = font.getbbox(text)
                text_width = right - left
                text_height = bottom - top
            except AttributeError:
                try:
                    # 旧版Pillow方法
                    text_width, text_height = draw.textsize(text, font=font)
                except AttributeError:
                    # 如果两种方法都不可用，使用估计值
                    text_width, text_height = len(text) * 7, 14
            
            position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
            
            # 绘制文本 (兼容新版Pillow)
            try:
                draw.text(position, text, fill=text_color, font=font)
            except TypeError:
                # 如果旧方法失败，尝试新方法（不传递font参数）
                draw.text(position, text, fill=text_color)
            
            # 保存图像
            image.save(filename)
            return filename
        except ImportError:
            print("警告: 无法创建图标，缺少PIL库")
            return filename
    
    @staticmethod
    def create_status_icon(color: Tuple[int, int, int] = (50, 50, 255)) -> Optional[str]:
        """
        创建状态栏应用的默认图标
        
        Args:
            color: 图标颜色
            
        Returns:
            图标文件路径，如果创建失败则返回None
        """
        try:
            return IconManager.create_icon("i", text_color=color, filename="status_icon.png")
        except Exception as e:
            print(f"创建图标失败: {e}")
            return None
    
    @staticmethod
    def get_app_icon() -> Optional[str]:
        """
        获取应用图标路径
        
        Returns:
            图标文件路径，如果不存在则创建，失败则返回None
        """
        icon_path = "status_icon.png"
        if os.path.exists(icon_path):
            return icon_path
            
        return IconManager.create_status_icon()
